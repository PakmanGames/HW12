import shutil
import subprocess
import os
import json

def get_container_logs(name: str, lines: int = 300):
    """Get the last N lines of container logs"""
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        for path in ["/usr/bin/docker", "/usr/local/bin/docker", "/bin/docker"]:
            if os.path.exists(path):
                docker_cmd = path
                break
    
    if not docker_cmd:
        return "Error: Docker binary not found"
    
    try:
        result = subprocess.run(
            [docker_cmd, "logs", "--tail", str(lines), name],
            capture_output=True, text=True, timeout=10
        )
        # Combine stdout and stderr
        logs = result.stdout + result.stderr
        return logs if logs else "No logs available"
    except Exception as e:
        return f"Error fetching logs: {str(e)}"


def get_container_state(name: str):
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        # Fallback paths
        for path in ["/usr/bin/docker", "/usr/local/bin/docker", "/bin/docker"]:
            if os.path.exists(path):
                docker_cmd = path
                break
    
    if not docker_cmd:
        return None

    try:
        result = subprocess.run(
            [docker_cmd, "inspect", name],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
            
        info = json.loads(result.stdout)[0]
        state = info["State"]
        
        return {
            "status": state["Status"],
            "restart_count": info.get("RestartCount", 0),  # RestartCount is at container level, not State level
            "exit_code": state.get("ExitCode", 0),
            "finished_at": state.get("FinishedAt", ""),
            "started_at": state.get("StartedAt", "")
        }
    except Exception as e:
        print(f"Exception inspecting {name}: {str(e)}")
        return None
