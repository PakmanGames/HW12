# Use a lightweight base image with Python for scripting
FROM python:3.12-slim

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install docker CLI so the container can inspect other containers
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user for safety
# RUN useradd -ms /bin/bash monitoruser
# USER monitoruser

WORKDIR /app

# Install Python dependencies (if any)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy monitor script(s)
COPY agent.py .

COPY docker_tools.py .

# Run the monitor
CMD ["python", "agent.py"]
