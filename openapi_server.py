from fastapi import FastAPI, HTTPException, Body, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import os
import sys

# Add the MCP server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MCP server components
# These imports will need to be adjusted based on the actual structure of the comfyui-mcp-server
from mcp_adapter import MCPServer  # Adjust import according to actual structure

# Initialize FastAPI
app = FastAPI(
    title="ComfyUI MCP API",
    description="OpenAPI-compatible interface for ComfyUI Machine Communication Protocol",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Server
mcp_server = MCPServer()  # Adjust initialization parameters as needed

# Define Pydantic models for request/response objects
class WorkflowRequest(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="ComfyUI workflow JSON")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Input parameters for the workflow")

class WorkflowResponse(BaseModel):
    job_id: str = Field(..., description="ID of the submitted job")
    status: str = Field(..., description="Status of the job submission")

class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="ID of the job")
    status: str = Field(..., description="Current status of the job")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Job outputs if complete")
    error: Optional[str] = Field(None, description="Error message if failed")

# Define API endpoints
@app.post("/api/workflow", response_model=WorkflowResponse, tags=["Workflow"])
async def submit_workflow(request: WorkflowRequest):
    """
    Submit a ComfyUI workflow for processing
    """
    try:
        # Process the workflow using the MCP server
        job_id = mcp_server.submit_workflow(request.workflow, request.inputs)
        return {"job_id": job_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job/{job_id}", response_model=JobStatusResponse, tags=["Job"])
async def get_job_status(job_id: str):
    """
    Get the status of a previously submitted job
    """
    try:
        # Get job status from the MCP server
        status = mcp_server.get_job_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/job/{job_id}", tags=["Job"])
async def cancel_job(job_id: str):
    """
    Cancel a running job
    """
    try:
        mcp_server.cancel_job(job_id)
        return {"status": "cancelled", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/models", tags=["Models"])
async def list_models():
    """
    List available models
    """
    try:
        models = mcp_server.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints as needed based on the MCP server capabilities

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)