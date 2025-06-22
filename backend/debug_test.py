import os
from letta_client import Letta, MessageCreate
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize client
api_key = os.getenv("LETTA_API_KEY")
client = Letta(token=api_key)

def test_simple_interaction():
    """Test a simple interaction with one agent to debug tool calling."""
    
    # Get the first agent
    agents = client.agents.list()
    if not agents:
        print("No agents found!")
        return
    
    agent = agents[0]
    print(f"Testing with agent: {agent.name} ({agent.id})")
    
    # Send a very simple message
    simple_prompt = f"""
Please use the agent_like_ad tool with these parameters:
- agent_id: {agent.name}
- ad_id: test_ad

Just call the tool and tell me if it worked.
"""
    
    print("\n=== Sending simple prompt ===")
    print(simple_prompt)
    
    try:
        # Try streaming to see the full interaction
        print("\n=== Streaming response ===")
        stream = client.agents.messages.create_stream(
            agent_id=agent.id,
            messages=[MessageCreate(role="user", content=simple_prompt)]
        )
        
        print("Stream chunks:")
        for i, chunk in enumerate(stream):
            print(f"  {i+1}. Type: {chunk.message_type}")
            if hasattr(chunk, 'content') and chunk.content:
                print(f"     Content: {chunk.content}")
            if hasattr(chunk, 'tool_call') and chunk.tool_call:
                print(f"     Tool: {chunk.tool_call.name}")
                print(f"     Args: {chunk.tool_call.arguments}")
            if hasattr(chunk, 'tool_return') and chunk.tool_return:
                print(f"     Tool Return: {chunk.tool_return}")
    
    except Exception as e:
        print(f"Error in streaming: {e}")

if __name__ == "__main__":
    test_simple_interaction() 