import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# We are creating a simple CLI runner, so FastAPI app is not strictly needed for now,
# but we'll keep it for potential future API endpoints.
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Digital Clone Simulation Environment"}

def print_usage():
    """Prints the command usage instructions."""
    print("Usage: python -m backend.main [command]")
    print("\nCommands:")
    print("  create       - Run the agent creation script to populate agents.")
    print("  simulate     - Run the ad simulation with the existing agents.")
    print("  serve        - (Future use) Starts the FastAPI web server.")
    print("\nExamples:")
    print("  python -m backend.main create")
    print("  python -m backend.main simulate")

def main():
    """Main entry point to run different modules."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        print("Running agent creation module...")
        from backend.create_agents import main as create_main
        create_main()
    elif command == "simulate":
        print("Running simulation module...")
        from backend.simulation import main as simulate_main
        simulate_main()
    elif command == "serve":
        print("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
