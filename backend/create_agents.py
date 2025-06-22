import os
import sys
import csv
import inspect
import asyncio
from letta_client import Letta
from backend import tools_v2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- Configuration ---
# Use Letta Cloud
api_key = os.getenv("LETTA_API_KEY")
if not api_key:
    raise ValueError("LETTA_API_KEY not found in .env file. Please create a .env file in the 'digital-clone' directory.")
CLIENT = Letta(token=api_key)

PERSONALITIES_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'agent_personalities.csv')
AGENT_CONFIG = {
    "model": "openai/gpt-4o-mini",
    "embedding": "openai/text-embedding-3-small"
}

# Manually define tool schemas to handle extra server-side args
CUSTOM_TOOL_SCHEMAS = [
    {
        "name": "agent_like_ad",
        "description": "Use this tool to express a 'like' for an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being liked."}
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "agent_dislike_ad",
        "description": "Use this tool to express a 'dislike' for an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being disliked."}
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "agent_comment_ad",
        "description": "Use this tool to post a comment on an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad for the comment."},
                "comment_text": {"type": "string", "description": "The content of the comment."}
            },
            "required": ["agent_id", "ad_id", "comment_text"]
        }
    },
    {
        "name": "agent_repost_ad",
        "description": "Use this tool to repost an advertisement, similar to a retweet.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being reposted."},
                "repost_reason": {"type": "string", "description": "The reason or commentary for the repost."}
            },
            "required": ["agent_id", "ad_id", "repost_reason"]
        }
    },
    {
        "name": "agent_ignore_ad",
        "description": "Use this tool to ignore an advertisement without any engagement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being ignored."}
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "read_shared_knowledge",
        "description": "Reads the shared knowledge base accessible to all agents.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "write_shared_knowledge",
        "description": "Writes or appends content to the shared knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The information to add to the shared knowledge base."}
            },
            "required": ["content"]
        }
    }
]


async def delete_all_agents():
    """Deletes all agents from the Letta server."""
    print("Deleting all existing agents...")
    try:
        agents = CLIENT.agents.list()
        if not agents:
            print("  - No agents found to delete.")
            return
        
        print(f"  - Found {len(agents)} agents to delete.")
        
        # Delete agents one by one to avoid overwhelming the API
        deleted_count = 0
        for agent in agents:
            try:
                CLIENT.agents.delete(agent.id)
                deleted_count += 1
                print(f"  - Deleted agent {agent.name} ({deleted_count}/{len(agents)})")
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  - Warning: Failed to delete agent {agent.name}: {e}")
                # Continue with other agents even if one fails
                continue
        
        print(f"  - Successfully deleted {deleted_count} out of {len(agents)} agents.")
    except Exception as e:
        print(f"An error occurred while listing/deleting agents: {e}")
        # We re-raise the exception to be handled by the API endpoint
        raise e

def register_tools():
    """Registers all custom tools with the Letta server using manual schemas and source code."""
    print("Registering fresh tools...")
    
    # Read the entire source code of the tools_v2 module
    try:
        tools_source_code = inspect.getsource(tools_v2)
    except TypeError:
        with open(tools_v2.__file__, 'r') as f:
            tools_source_code = f.read()

    tool_names = []
    for schema in CUSTOM_TOOL_SCHEMAS:
        try:
            tool = CLIENT.tools.create(
                json_schema=schema,
                source_code=tools_source_code
            )
            tool_names.append(tool.name)
            print(f"  - Registered tool '{tool.name}'")
        except Exception as e:
            if "already exists" in str(e):
                tool_names.append(schema['name'])
                print(f"  - Tool '{schema['name']}' already exists.")
            else:
                print(f"Error registering tool '{schema['name']}': {e}")
                sys.exit(1)
    return tool_names

def create_agent_from_row(agent_name: str, personality_text: str, tool_names: list):
    """Creates a single agent from a personality text."""
    # The persona memory block holds the core, read-only identity.
    persona_content = f"""
You are a person with the following personality: {personality_text}.
Your name is {agent_name}.
You are interacting with a social media feed. When you see an ad, you MUST use one or more of the provided tools to react.
You can use agent_like_ad, agent_dislike_ad, agent_comment_ad, agent_repost_ad, or agent_ignore_ad.
After using the tools, output a short, final message expressing your overall opinion.
    """

    print(f"Creating agent '{agent_name}'...")
    try:
        # To avoid conflicts, let's first check if an agent with this name already exists
        existing_agents = CLIENT.agents.list(name=agent_name)
        if existing_agents:
            print(f"  - Agent with name '{agent_name}' already exists. Skipping.")
            return None

        agent = CLIENT.agents.create(
            name=agent_name,
            memory_blocks=[
                {
                    "label": "persona",
                    "value": persona_content,
                },
                {
                    "label": "interaction_history",
                    "value": "This memory block stores your past ad interactions. You can read and write to it.",
                    "description": "A read-write memory of past interactions with ads."
                }
            ],
            tools=tool_names + ["core_memory_append", "core_memory_replace"],
            model=AGENT_CONFIG["model"],
            embedding=AGENT_CONFIG["embedding"]
        )
        print(f"  - Successfully created agent '{agent.name}' with ID: {agent.id}")
        return agent
    except Exception as e:
        print(f"  - Error creating agent '{agent_name}': {e}")
        return None


async def recreate_agents_from_csv(csv_file_like_object):
    """
    Deletes all existing agents and creates new ones from a CSV file stream.
    """
    print("--- Starting Agent Recreation from CSV ---")
    
    # 1. Delete all old agents first
    await delete_all_agents()

    # 2. Register all tools (this can remain synchronous)
    tool_names = register_tools()
    if not tool_names:
        print("No tools were registered. Halting agent creation.")
        raise Exception("Tool registration failed.")

    # 3. Read the personalities from the in-memory CSV
    try:
        reader = csv.DictReader(csv_file_like_object)
        personalities = list(reader)
    except Exception as e:
        print(f"Error reading or parsing CSV file stream: {e}")
        raise e
    
    if not personalities:
        print("No personalities found in the provided CSV.")
        return 0

    print(f"Found {len(personalities)} personalities. Creating agents...")

    # 4. Create an agent for each personality
    created_count = 0
    for person in personalities:
        agent_name = person.get("name")
        personality_desc = person.get("personality_description")
        if not agent_name or not personality_desc:
            print(f"Skipping row due to missing 'name' or 'personality_description': {person}")
            continue
        
        # The creation logic itself is synchronous, but we call it
        agent = create_agent_from_row(agent_name, personality_desc, tool_names)
        if agent:
            created_count += 1

    print("--- Agent Recreation Complete ---")
    return created_count


async def create_agents_from_csv(csv_file_like_object):
    """
    Creates new agents from a CSV file stream without deleting existing ones.
    """
    print("--- Starting Agent Creation from CSV ---")

    # 1. Register all tools (this can remain synchronous)
    tool_names = register_tools()
    if not tool_names:
        print("No tools were registered. Halting agent creation.")
        raise Exception("Tool registration failed.")

    # 2. Read the personalities from the in-memory CSV
    try:
        reader = csv.DictReader(csv_file_like_object)
        personalities = list(reader)
    except Exception as e:
        print(f"Error reading or parsing CSV file stream: {e}")
        raise e
    
    if not personalities:
        print("No personalities found in the provided CSV.")
        return 0

    print(f"Found {len(personalities)} personalities. Creating agents...")

    # 3. Create an agent for each personality
    created_count = 0
    for person in personalities:
        agent_name = person.get("name")
        personality_desc = person.get("personality_description")
        if not agent_name or not personality_desc:
            print(f"Skipping row due to missing 'name' or 'personality_description': {person}")
            continue
        
        # The creation logic itself is synchronous, but we call it
        agent = create_agent_from_row(agent_name, personality_desc, tool_names)
        if agent:
            created_count += 1

    print("--- Agent Creation Complete ---")
    return created_count


def main():
    """Main function to register tools and create agents from a CSV file."""
    print("--- Starting Agent Population from CSV ---")
    
    # 1. Register all tools
    tool_names = register_tools()
    if not tool_names:
        print("No tools were registered. Exiting.")
        return

    # 2. Find and read the personalities CSV
    if not os.path.exists(PERSONALITIES_CSV):
        print(f"Error: Personalities CSV not found at '{PERSONALITIES_CSV}'")
        return
        
    try:
        with open(PERSONALITIES_CSV, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            personalities = list(reader)
    except Exception as e:
        print(f"Error reading or parsing CSV file: {e}")
        return
    
    if not personalities:
        print(f"No personalities found in '{PERSONALITIES_CSV}'.")
        return

    print(f"Found {len(personalities)} personalities. Creating agents...")

    # 3. Create an agent for each personality in the CSV
    for person in personalities:
        agent_name = person.get("name")
        personality_desc = person.get("personality_description")
        if not agent_name or not personality_desc:
            print(f"Skipping row due to missing 'name' or 'personality_description': {person}")
            continue
        create_agent_from_row(agent_name, personality_desc, tool_names)

    print("--- Agent Population Complete ---")

if __name__ == "__main__":
    main() 