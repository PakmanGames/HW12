import time
import subprocess
import json
import shutil
import os
from google import genai
import datetime
import requests
from docker_tools import get_container_state, get_container_logs

gemini_api = os.environ.get("GENAI_API_KEY")
backend_route = os.environ.get("AGENT_BACKEND_URL")
agent_id = os.environ.get("AGENT_ID")


def post_status( error: str, explanation: str, suggestion: str, time: datetime.datetime):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gemini_api}"
    }
    
    payload = {
        "id": agent_id,
        "errorMessage": error,
        "explaination": explanation,
        "suggestedFix": suggestion,
        "occurredAt": time.isoformat()
    }
    
    error_route = f"{backend_route}/api/errors"

    try:
        response = requests.post(error_route, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to post status: {e}")
        return None



def get_gemini_response(prompt: str) -> str:
    client = genai.Client(api_key=gemini_api)
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content




TARGETS = ["agent-app-1", "agent-test-container-1"]  # container names

# Track restart counts to detect exits
restart_counts = {}

# Track container status: "alive" or "fail"
container_status = {}

bad_states = ["exited", "dead", "restarting"]


def on_fail(container_name: str, logs: str):
    """Called when a container transitions from alive to fail"""
    # TODO: Implement failure handling logic
    print(f"[{container_name}] 🔥 FAILURE DETECTED - Transitioning to FAIL state")
    # This is where you can add custom logic like:
    # - Analyze logs with AI
    # - Send alerts
    # - Attempt recovery
    # - Post to backend


def main():
    print("Starting Agent Monitor...")
    print(f"PATH: {os.environ.get('PATH')}")
    print(f"Docker binary: {shutil.which('docker')}")
    
    # Initialize all containers as alive
    for name in TARGETS:
        container_status[name] = "alive"
    
    while True:
        for name in TARGETS:
            state = get_container_state(name)
            
            if state is None:
                print(f"[{name}] Error: Could not inspect container")
                continue
            
            status = state["status"]
            restart_count = state["restart_count"]
            exit_code = state["exit_code"]
            
            # Initialize restart count tracking
            if name not in restart_counts:
                restart_counts[name] = restart_count
                print(f"[{name}] Initial state: {status}, RestartCount={restart_count}")
                continue
            
            # Determine if container is currently in a failed state
            is_failed = status in bad_states or restart_count > restart_counts[name]
            
            if is_failed:
                # Container is in a failed state
                if container_status[name] == "alive":
                    # Transition from alive -> fail
                    error_logs = get_container_logs(name, lines=300)
                    print(f"[{name}] ⚠️  Container failed! Status={status}, ExitCode={exit_code}, RestartCount={restart_count}")
                    container_status[name] = "fail"
                    on_fail(name, error_logs)
                    
                    # Update restart count
                    if restart_count > restart_counts[name]:
                        restart_counts[name] = restart_count
                # else: Already in fail state, don't call on_fail again
            else:
                # Container is healthy/running
                if container_status[name] == "fail":
                    # Transition from fail -> alive (recovery)
                    print(f"[{name}] ✅ Container recovered! Status={status}")
                    container_status[name] = "alive"
                else:
                    # Still alive
                    print(f"[{name}] Status={status}, RestartCount={restart_count}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()