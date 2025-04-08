# mcp_adapter.py
import json
import os
import requests
from typing import Dict, Any, Optional

import subprocess
import time
import threading

class MCPServer:
    
    """
    Adapter class for the ComfyUI MCP Server
    """
    def __init__(self, comfy_api_url="http://127.0.0.1:8188"):
        self.comfy_api_url = comfy_api_url
        self.active_jobs = {}
        
    def submit_workflow(self, workflow: Dict[str, Any], inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a workflow to ComfyUI
        """
        # If inputs are provided, update the workflow with them
        if inputs:
            # Logic to merge inputs into the workflow
            # This will depend on the specific structure of ComfyUI workflows
            pass
        
        # Submit to ComfyUI API
        prompt_url = f"{self.comfy_api_url}/prompt"
        response = requests.post(prompt_url, json={"prompt": workflow})
        data = response.json()
        
        # Store job information
        job_id = data.get("prompt_id")
        self.active_jobs[job_id] = {"status": "queued", "progress": 0}
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job
        """
        # Check if job is in our tracking
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        # Query ComfyUI for status
        history_url = f"{self.comfy_api_url}/history/{job_id}"
        response = requests.get(history_url)
        
        if response.status_code == 200:
            data = response.json()
            # Update our tracking with the latest info
            if job_id in data:
                job_data = data[job_id]
                status = "completed" if job_data.get("completed", False) else "running"
                outputs = job_data.get("outputs", {})
                
                self.active_jobs[job_id] = {
                    "status": status,
                    "progress": job_data.get("progress", 0) * 100,
                    "outputs": outputs
                }
        
        return self.active_jobs[job_id]
    
    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a running job
        """
        cancel_url = f"{self.comfy_api_url}/queue"
        response = requests.post(cancel_url, json={"delete": [job_id]})
        
        if response.status_code == 200:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = "cancelled"
        else:
            raise ValueError(f"Failed to cancel job {job_id}")
    
    def list_models(self) -> Dict[str, Any]:
        """
        List available models
        """
        object_info_url = f"{self.comfy_api_url}/object_info"
        response = requests.get(object_info_url)
        
        if response.status_code == 200:
            data = response.json()
            # Extract model information
            models = {}
            
            # Process checkpoints
            if "CheckpointLoaderSimple" in data:
                models["checkpoints"] = data["CheckpointLoaderSimple"].get("input", {}).get("required", {}).get("ckpt_name", [])
            
            # Process samplers
            if "KSampler" in data:
                models["samplers"] = data["KSampler"].get("input", {}).get("required", {}).get("sampler_name", [])
            
            # Add more model types as needed
            
            return models
        else:
            raise ValueError("Failed to retrieve model information")
        
        
class MCPServerSubprocess:
    def __init__(self, server_path):
        self.server_path = server_path
        self.process = None
        self.start_server()
    
    def start_server(self):
        # Start the original MCP server as a subprocess
        self.process = subprocess.Popen(
            ["python", f"{self.server_path}/server.py"],  # Adjust path as needed
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it time to start
        time.sleep(5)
        
        # Start a thread to monitor the server
        threading.Thread(target=self._monitor_server, daemon=True).start()
    
    def _monitor_server(self):
        while self.process:
            line = self.process.stdout.readline()
            if not line:
                break
            print(f"MCP Server: {line.decode().strip()}")
    
    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process = None