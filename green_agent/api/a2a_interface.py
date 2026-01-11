"""A2A Protocol Interface for RAID-AI Green Agent"""
# Run with: python3 -m green_agent.api.a2a_interface
# NOTE: go to http://localhost:8000/benchmark/info to see benchmark info 

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import json

from green_agent.main import RAIDGreenAgent

app = FastAPI(title="RAID-AI Green Agent API")
agent = RAIDGreenAgent()

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    if not agent.bugs_catalog:
        agent.initialize_benchmark()

class BugRequest(BaseModel):
    bug_index: int

class FixSubmission(BaseModel):
    bug_index: int
    fixed_files: Dict[str, str]  # filepath -> content
    patch: Optional[str] = None

@app.get("/")
async def root():
    return {"name": "RAID-AI Green Agent", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "RAID-AI Green Agent"}

@app.get("/benchmark/info")
async def get_benchmark_info():
    """Get benchmark information"""
    return agent.export_benchmark_info()

@app.get("/bugs/list")
async def list_bugs():
    """List all bugs in the benchmark"""
    return {"bugs": agent.bugs_catalog}

@app.get("/bugs/{bug_index}")
async def get_bug(bug_index: int):
    """Get a specific bug"""
    bug = agent.get_bug(bug_index)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug

@app.post("/evaluate")
async def evaluate_fix(submission: FixSubmission):
    """Evaluate a fix submission"""
    # This would evaluate the submitted fix
    # For now, just return placeholder
    return {
        "bug_index": submission.bug_index,
        "status": "received",
        "message": "Fix evaluation not yet implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
