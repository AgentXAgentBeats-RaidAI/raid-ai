"""A2A Protocol Interface for RAID-AI Green Agent"""
# Run with: python3 -m green_agent.api.a2a_interface
# NOTE: go to http://localhost:8000/benchmark/info to see benchmark info 

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager

from green_agent.main import RAIDGreenAgent

# Store assessment results in memory (in production, use proper database)
assessment_results = []
active_assessments = {}
agent = RAIDGreenAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not agent.bugs_catalog:
        agent.initialize_benchmark()
    
    # Create results directory
    Path("data/assessment_results").mkdir(parents=True, exist_ok=True)
    
    yield
    # Shutdown (if needed)

app = FastAPI(title="RAID-AI Green Agent API", lifespan=lifespan)

class BugRequest(BaseModel):
    bug_index: int

class FixSubmission(BaseModel):
    bug_index: int
    fixed_files: Dict[str, str]  # filepath -> content
    patch: Optional[str] = None

class AssessmentRequest(BaseModel):
    agent_id: str
    docker_image: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    bug_indices: Optional[List[int]] = None  # If not provided, run all bugs

class AssessmentResult(BaseModel):
    assessment_id: str
    agent_id: str
    bug_index: int
    bug_framework: str
    total_score: float
    correctness_score: float
    code_quality_score: float
    efficiency_score: float
    minimal_change_score: float
    execution_time_seconds: float
    assessment_timestamp: str
    reproducible: bool = True

@app.get("/")
async def root():
    return {"name": "RAID-AI Green Agent", "version": "0.1.0", "protocol": "A2A"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "RAID-AI Green Agent"}

@app.get("/benchmark/info")
async def get_benchmark_info():
    """Get benchmark information - A2A Protocol requirement"""
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

@app.post("/assess")
async def start_assessment(request: AssessmentRequest, background_tasks: BackgroundTasks):
    """Start assessment of a purple agent - A2A Protocol endpoint"""
    assessment_id = str(uuid.uuid4())
    
    # Store assessment info
    active_assessments[assessment_id] = {
        "agent_id": request.agent_id,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "progress": {"completed": 0, "total": len(request.bug_indices) if request.bug_indices else len(agent.bugs_catalog)}
    }
    
    # Run assessment in background
    background_tasks.add_task(
        run_assessment, 
        assessment_id, 
        request.agent_id, 
        request.bug_indices or list(range(len(agent.bugs_catalog)))
    )
    
    return {
        "assessment_id": assessment_id,
        "status": "started",
        "agent_id": request.agent_id,
        "estimated_duration_minutes": (len(request.bug_indices) if request.bug_indices else len(agent.bugs_catalog)) * 10
    }

async def run_assessment(assessment_id: str, agent_id: str, bug_indices: List[int]):
    """Run assessment for a purple agent"""
    try:
        results = []
        
        for i, bug_index in enumerate(bug_indices):
            # Update progress
            active_assessments[assessment_id]["progress"]["completed"] = i
            
            # For demo purposes, simulate assessment with placeholder scores
            # In real implementation, this would:
            # 1. Deploy the purple agent via Docker
            # 2. Send bug to purple agent
            # 3. Receive fix from purple agent  
            # 4. Evaluate fix using agent.evaluate_fix()
            
            bug = agent.get_bug(bug_index)
            if not bug:
                continue
                
            # Simulate assessment duration
            time.sleep(2)  # Remove in production
            
            # Create mock result (replace with real evaluation)
            result = AssessmentResult(
                assessment_id=assessment_id,
                agent_id=agent_id,
                bug_index=bug_index,
                bug_framework=bug['language'],
                total_score=0.75,  # Would come from agent.evaluate_fix()
                correctness_score=0.8,
                code_quality_score=0.7,
                efficiency_score=0.8,
                minimal_change_score=0.7,
                execution_time_seconds=45.0,
                assessment_timestamp=datetime.now(timezone.utc).isoformat(),
                reproducible=True
            )
            
            results.append(result)
            assessment_results.append(result)
        
        # Mark assessment complete
        active_assessments[assessment_id]["status"] = "completed"
        active_assessments[assessment_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save results to file for persistence
        save_assessment_results(assessment_id, results)
        
    except Exception as e:
        active_assessments[assessment_id]["status"] = "failed"
        active_assessments[assessment_id]["error"] = str(e)

def save_assessment_results(assessment_id: str, results: List[AssessmentResult]):
    """Save assessment results to JSON file"""
    results_file = f"data/assessment_results/{assessment_id}.json"
    with open(results_file, 'w') as f:
        json.dump([result.model_dump() for result in results], f, indent=2)

@app.get("/assess/{assessment_id}")
async def get_assessment_status(assessment_id: str):
    """Get assessment status and results"""
    if assessment_id not in active_assessments:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment_info = active_assessments[assessment_id]
    
    # If completed, include results
    if assessment_info["status"] == "completed":
        results = [r for r in assessment_results if r.assessment_id == assessment_id]
        assessment_info["results"] = [r.model_dump() for r in results]
    
    return assessment_info

@app.get("/leaderboard")
async def get_leaderboard():
    """Get current leaderboard rankings"""
    # Group results by agent_id and calculate aggregate scores
    agent_scores = {}
    
    for result in assessment_results:
        agent_id = result.agent_id
        if agent_id not in agent_scores:
            agent_scores[agent_id] = {
                "agent_id": agent_id,
                "total_assessments": 0,
                "avg_score": 0.0,
                "bugs_fixed": 0,
                "avg_execution_time": 0.0,
                "last_assessment": result.assessment_timestamp
            }
        
        agent_scores[agent_id]["total_assessments"] += 1
        agent_scores[agent_id]["avg_score"] = (
            agent_scores[agent_id]["avg_score"] * (agent_scores[agent_id]["total_assessments"] - 1) + 
            result.total_score
        ) / agent_scores[agent_id]["total_assessments"]
        
        if result.correctness_score > 0.8:
            agent_scores[agent_id]["bugs_fixed"] += 1
    
    # Sort by average score
    leaderboard = sorted(agent_scores.values(), key=lambda x: x["avg_score"], reverse=True)
    
    return {"leaderboard": leaderboard, "last_updated": datetime.now(timezone.utc).isoformat()}

@app.get("/results")
async def get_all_results():
    """Get all assessment results for analysis"""
    return {"results": [r.model_dump() for r in assessment_results]}

@app.post("/evaluate")
async def evaluate_fix(submission: FixSubmission):
    """Legacy evaluate endpoint for compatibility"""
    # This would evaluate the submitted fix
    # For now, just return placeholder
    return {
        "bug_index": submission.bug_index,
        "status": "received", 
        "message": "Use /assess endpoint for full A2A protocol assessment"
    }

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard HTML"""
    from fastapi.responses import FileResponse
    import os
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    return FileResponse(dashboard_path, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
