import os
import requests
import time
import json
from langchain.tools import Tool
from typing import Optional

JENKINS_BASE_URL = os.getenv("JENKINS_URL", "http://localhost:8080")
JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

def check_jenkins_connection():
    """Check if Jenkins is accessible."""
    try:
        response = requests.get(f"{JENKINS_BASE_URL}/api/json", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_jenkins_job(job_name: str, job_config: str) -> str:
    """Create a new Jenkins job with the given configuration."""
    if not all([JENKINS_USERNAME, JENKINS_API_TOKEN]):
        return "Jenkins credentials not configured. Please set JENKINS_USERNAME and JENKINS_API_TOKEN."
    
    job_url = f"{JENKINS_BASE_URL}/createItem?name={job_name}"
    
    headers = {
        'Content-Type': 'application/xml',
        'Authorization': f'Basic {requests.utils.b64encode(f"{JENKINS_USERNAME}:{JENKINS_API_TOKEN}".encode()).decode()}'
    }
    
    try:
        response = requests.post(job_url, data=job_config, headers=headers)
        if response.status_code == 200:
            return f"Jenkins job '{job_name}' created successfully."
        elif response.status_code == 400:
            return f"Invalid job configuration for '{job_name}'."
        else:
            return f"Failed to create job '{job_name}'. Status: {response.status_code}"
    except Exception as e:
        return f"Error creating job '{job_name}': {str(e)}"

def trigger_jenkins_job(job_name: str) -> str:
    """Trigger a Jenkins job build."""
    if not all([JENKINS_USERNAME, JENKINS_API_TOKEN]):
        return "Jenkins credentials not configured. Please set JENKINS_USERNAME and JENKINS_API_TOKEN."
    
    job_url = f"{JENKINS_BASE_URL}/job/{job_name}/build"
    
    try:
        response = requests.post(
            job_url,
            auth=(JENKINS_USERNAME, JENKINS_API_TOKEN)
        )
        
        if response.status_code == 201:
            return f"Jenkins job '{job_name}' triggered successfully."
        elif response.status_code == 403:
            return f"Permission denied. Check your Jenkins credentials and token."
        elif response.status_code == 404:
            return f"Job '{job_name}' not found on Jenkins server."
        else:
            return f"Failed to trigger Jenkins job '{job_name}'. Status code: {response.status_code}"
    except Exception as e:
        return f"Error triggering job '{job_name}': {str(e)}"

def get_job_status(job_name: str) -> str:
    """Get the current status of a Jenkins job."""
    if not all([JENKINS_USERNAME, JENKINS_API_TOKEN]):
        return "Jenkins credentials not configured."
    
    job_url = f"{JENKINS_BASE_URL}/job/{job_name}/lastBuild/api/json"
    
    try:
        response = requests.get(
            job_url,
            auth=(JENKINS_USERNAME, JENKINS_API_TOKEN)
        )
        
        if response.status_code == 200:
            build_info = response.json()
            result = build_info.get('result', 'IN_PROGRESS')
            number = build_info.get('number', 'N/A')
            return f"Job '{job_name}' build #{number}: {result}"
        elif response.status_code == 404:
            return f"Job '{job_name}' not found or no builds exist."
        else:
            return f"Failed to get job status. Status code: {response.status_code}"
    except Exception as e:
        return f"Error getting job status: {str(e)}"

def get_build_logs(job_name: str, build_number: Optional[int] = None) -> str:
    """Get build logs for a Jenkins job."""
    if not all([JENKINS_USERNAME, JENKINS_API_TOKEN]):
        return "Jenkins credentials not configured."
    
    if build_number is None:
        build_url = f"{JENKINS_BASE_URL}/job/{job_name}/lastBuild/consoleText"
    else:
        build_url = f"{JENKINS_BASE_URL}/job/{job_name}/{build_number}/consoleText"
    
    try:
        response = requests.get(
            build_url,
            auth=(JENKINS_USERNAME, JENKINS_API_TOKEN)
        )
        
        if response.status_code == 200:
            logs = response.text
            if len(logs) > 2000:
                logs = logs[:2000] + "\n... (truncated)"
            return f"Build logs for '{job_name}':\n{logs}"
        elif response.status_code == 404:
            return f"Build logs not found for '{job_name}'."
        else:
            return f"Failed to get build logs. Status code: {response.status_code}"
    except Exception as e:
        return f"Error getting build logs: {str(e)}"

def analyze_build_errors(job_name: str) -> str:
    """Analyze build logs for common errors and provide suggestions."""
    if not all([JENKINS_USERNAME, JENKINS_API_TOKEN]):
        return "Jenkins credentials not configured."
    
    logs_response = get_build_logs(job_name)
    
    if logs_response.startswith("Error"):
        return logs_response
    
    logs = logs_response.split("Build logs for")[1].split("\n", 1)[1] if "Build logs for" in logs_response else ""
    
    error_patterns = {
        "Compilation Error": ["error:", "Error:", "compilation failed"],
        "Dependency Issue": ["ModuleNotFoundError", "ImportError", "npm ERR", "pip install"],
        "Permission Error": ["Permission denied", "access denied", "EACCES"],
        "Network Error": ["Connection refused", "timeout", "network error"],
        "Build Tool Error": ["maven", "gradle", "npm", "yarn"],
        "Test Failure": ["FAILED", "AssertionError", "test failed"]
    }
    
    found_errors = []
    for error_type, patterns in error_patterns.items():
        for pattern in patterns:
            if pattern.lower() in logs.lower():
                found_errors.append(error_type)
                break
    
    if found_errors:
        return f"Error Analysis for '{job_name}':\nFound issues: {', '.join(set(found_errors))}\n\nFull logs:\n{logs}"
    else:
        return f"No common errors detected in '{job_name}' build logs.\n\nLogs:\n{logs}"

def get_jenkins_tool(job_name: str):
    """Create a comprehensive Jenkins tool with multiple functions."""
    
    def jenkins_operations(operation: str) -> str:
        """Handle various Jenkins operations based on the operation type."""
        operation = operation.lower().strip()
        
        if "trigger" in operation or "build" in operation or "run" in operation:
            return trigger_jenkins_job(job_name)
        elif "status" in operation or "check" in operation:
            return get_job_status(job_name)
        elif "logs" in operation or "output" in operation:
            return get_build_logs(job_name)
        elif "error" in operation or "analyze" in operation or "debug" in operation:
            return analyze_build_errors(job_name)
        elif "create" in operation:
            job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>Auto-generated job for {job_name}</description>
  <builders>
    <hudson.tasks.Shell>
      <command>echo "Hello from {job_name}!"
echo "Build started at $(date)"
echo "Build completed successfully"</command>
    </hudson.tasks.Shell>
  </builders>
</project>"""
            return create_jenkins_job(job_name, job_config)
        else:
            return f"Available operations for job '{job_name}': trigger, status, logs, analyze, create"
    
    return Tool.from_function(
        func=jenkins_operations,
        name="jenkins_operations",
        description=f"Perform Jenkins operations on job '{job_name}'. Operations: trigger/build job, check status, get logs, analyze errors, create job. Use keywords like 'trigger', 'status', 'logs', 'analyze', or 'create' in your request."
    )
