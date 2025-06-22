import os
import sys
import time
import asyncio
import json
import re
from letta_client import Letta, MessageCreate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- Configuration ---
api_key = os.getenv("LETTA_API_KEY")
if not api_key:
    raise ValueError("LETTA_API_KEY not found in .env file.")
CLIENT = Letta(token=api_key)

def extract_json_from_string(text: str) -> dict:
    """
    Finds and parses the first valid JSON object within a string.
    Handles cases where the JSON is embedded in other text.
    """
    if not text or not text.strip():
        print(f"Warning: Empty or whitespace-only response received")
        return None
    
    # Try to find JSON object enclosed in curly braces
    # Look for the first { and the last } to handle nested objects
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        print(f"Warning: No valid JSON structure found in text: '{text[:100]}...'")
        return None
    
    json_str = text[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode JSON from string: '{json_str[:100]}...', Error: {e}")
        
        # Try to clean up common issues
        # Remove any trailing commas before closing braces/brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', json_str)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"Warning: Even cleaned JSON failed to parse: '{cleaned[:100]}...'")
            return None

async def run_simulation_with_ad_copy(ad_copy: str):
    """Runs the simulation for all agents against a single ad, returning JSON results."""
    ad_id = "user_provided_ad"
    print(f"--- Starting Simulation for Ad: '{ad_id}' ---")

    # 1. Get all available agents
    try:
        agents = CLIENT.agents.list()
        if not agents:
            print("No agents found. Please create them first.")
            raise Exception("No agents available for simulation.")
        
    except Exception as e:
        print(f"Failed to connect to Letta server or fetch agent details. Error: {e}")
        raise e

    print(f"Found {len(agents)} agents. Presenting ad and collecting results...")

    # 2. Present the ad to each agent concurrently
    tasks = [run_agent_interaction(agent, ad_id, ad_copy) for agent in agents]
    results = await asyncio.gather(*tasks)

    # Filter out any None results from failed interactions
    successful_results = [res for res in results if res]
    
    print("\n--- Simulation Complete ---")
    print(f"Successfully collected {len(successful_results)} results.")
    return successful_results

async def run_agent_interaction(agent, ad_id: str, ad_content: str):
    """Presents an ad to a single agent and processes its response."""
    print(f"\n-> Presenting ad to agent: {agent.name} ({agent.id})")

    prompt = f"""
You are on a social media platform and you see the following ad.
Your name is {agent.name}. Your personality is stored in your 'persona' memory block.

Ad Content: "{ad_content}"

You must complete this task in TWO PHASES:

PHASE 1 - TAKE ACTIONS:
Based on your persona, use the provided tools to react to this ad. You can use one or more tools (e.g., like and comment).

PHASE 2 - PROVIDE ANALYSIS (MANDATORY):
After your tool calls, you MUST immediately provide a JSON analysis of your reaction.

Your JSON response must be a single line with no other text, starting with {{{{ and ending with }}}}.

**If you took multiple actions, for the "reaction" field in the JSON, choose the one that you feel is your PRIMARY reaction.** For example, if you liked and commented, and the comment is more significant, use "comment".

Required format:
{{"reaction": "primary_action", "confidence": 0-100, "reasoning": "why you reacted this way", "tags": ["keyword1", "keyword2"], "final_message": "your social media post"}}

The `reaction` value should be one of `like`, `dislike`, `comment`, `repost`, or `ignore`.

IMPORTANT: You MUST complete both phases. Do not stop after phase 1.

Example complete interaction:
1. [Agent uses tool: agent_like_ad]
2. [Agent uses tool: agent_comment_ad]
3. {{"reaction": "comment", "confidence": 90, "reasoning": "I liked it, but my main action is commenting to ask for more details.", "tags": ["eco", "fashion"], "final_message": "Love it! Can you provide more info on your ethical sourcing?"}}
"""
    try:
        # Send the prompt to the agent
        print(f"  - Sending prompt to {agent.name}...")
        response = CLIENT.agents.messages.create_stream(
            agent_id=agent.id,
            messages=[MessageCreate(role="user", content=prompt)],
        )
        
        # Track tool calls and content
        tool_calls = []
        response_content = ""
        
        for chunk in response:
            if chunk.message_type == "assistant_message" and chunk.content:
                response_content += chunk.content
            elif chunk.message_type == "tool_call_message":
                tool_name = chunk.tool_call.name
                tool_calls.append(tool_name)
                print(f"  - Tool Call by {agent.name}: {tool_name}")
        
        print(f"  - Tool calls made: {tool_calls}")
        print(f"  - Raw response from {agent.name} (length: {len(response_content)}): '{response_content}'")
        
        # If we got an empty response but tool calls were made, try to get a follow-up
        if not response_content.strip() and tool_calls:
            print(f"  - Agent {agent.name} made tool calls but gave empty response. Requesting JSON...")
            follow_up_stream = CLIENT.agents.messages.create_stream(
                agent_id=agent.id,
                messages=[MessageCreate(role="user", content="Please provide your JSON analysis now as required in the format: {\"reaction\": \"action\", \"confidence\": 0-100, \"reasoning\": \"explanation\", \"tags\": [\"tag1\", \"tag2\"], \"final_message\": \"your post\"}")],
            )
            follow_up_content = ""
            for chunk in follow_up_stream:
                if chunk.message_type == "assistant_message" and chunk.content:
                    follow_up_content += chunk.content
            response_content = follow_up_content
            print(f"  - Follow-up response from {agent.name} (length: {len(response_content)}): '{response_content}'")
        
        if not response_content.strip():
            print("Warning: Empty or whitespace-only response received")
            return None
        
        # Extract the JSON from the agent's final response
        json_response = extract_json_from_string(response_content)
        
        if json_response:
            # Add agent info to the response
            json_response['agent_id'] = agent.id
            json_response['agent_name'] = agent.name
            # FIX: The agent object from list() doesn't contain memory_blocks.
            # We will return a placeholder for now.
            json_response['description'] = "Persona description (details not available from list view)."
            return json_response
        else:
            print(f"  - Error: Could not parse JSON response from agent '{agent.name}'")
            return None

    except Exception as e:
        print(f"  - Error interacting with agent '{agent.name}': {e}")
        return None

def main():
    """Main function to select an ad and run the simulation."""
    # This main function is now for local testing purposes only
    print("This script is now intended to be run as part of the FastAPI server.")
    print("To test locally, you can call run_simulation_with_ad_copy directly.")
    # Example usage:
    # ad_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'ads', 'sample_ad.txt')
    # with open(ad_file, 'r') as f:
    #     sample_ad = f.read()
    # asyncio.run(run_simulation_with_ad_copy(sample_ad))

if __name__ == "__main__":
    main() 