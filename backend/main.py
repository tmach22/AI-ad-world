import sys
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import os

# Adjust the path to import from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.create_agents import recreate_agents_from_csv, create_agents_from_csv
from backend.simulation import run_simulation_with_ad_copy

app = FastAPI(
    title="Persona Engagement API",
    description="API for creating persona agents and simulating their engagement with ad content.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This is necessary to allow the React frontend (running on a different port)
# to communicate with this FastAPI backend.
origins = [
    "http://localhost:3000",  # Default React dev server port
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Digital Clone Simulation Environment API"}

@app.post("/agents/recreate", tags=["Agents"])
async def http_recreate_agents(file: UploadFile = File(...)):
    """
    Deletes all existing agents and creates new ones from an uploaded CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, detail="Invalid file type. Please upload a CSV.")
    
    try:
        # Read the file into an in-memory text stream
        csv_content = await file.read()
        csv_file_like_object = io.StringIO(csv_content.decode('utf-8'))
        
        count = await recreate_agents_from_csv(csv_file_like_object)
        return {"message": f"Successfully recreated {count} agents."}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to recreate agents: {str(e)}")

@app.post("/agents/add", tags=["Agents"])
async def http_add_agents(file: UploadFile = File(...)):
    """
    Adds new agents from an uploaded CSV file without deleting existing ones.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, detail="Invalid file type. Please upload a CSV.")
    
    try:
        # Read the file into an in-memory text stream
        csv_content = await file.read()
        csv_file_like_object = io.StringIO(csv_content.decode('utf-8'))
        
        count = await create_agents_from_csv(csv_file_like_object)
        return {"message": f"Successfully added {count} new agents."}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to add new agents: {str(e)}")

@app.post("/simulate", tags=["Simulation"])
async def http_run_simulation(ad_copy: str):
    """
    Runs the ad simulation with the provided ad copy against all existing agents.
    """
    if not ad_copy or not ad_copy.strip():
        raise HTTPException(400, detail="Ad copy cannot be empty.")
        
    try:
        simulation_results = await run_simulation_with_ad_copy(ad_copy)
        return simulation_results
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to run simulation: {str(e)}")

def start_server():
    """Starts the FastAPI web server."""
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
