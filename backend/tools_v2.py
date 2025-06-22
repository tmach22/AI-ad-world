import os
import json

def agent_like_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to express a 'like' for an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being liked.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "like", "agent": agent_id, "ad": ad_id})

def agent_dislike_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to express a 'dislike' for an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being disliked.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "dislike", "agent": agent_id, "ad": ad_id})

def agent_comment_ad(agent_id: str, ad_id: str, comment_text: str, **kwargs) -> str:
    """
    Use this tool to post a comment on an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad for the comment.
        comment_text (str): The content of the comment.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "comment", "agent": agent_id, "ad": ad_id, "comment": comment_text})

def agent_repost_ad(agent_id: str, ad_id: str, repost_reason: str, **kwargs) -> str:
    """
    Use this tool to repost an advertisement, similar to a retweet.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being reposted.
        repost_reason (str): The reason or commentary for the repost.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "repost", "agent": agent_id, "ad": ad_id, "reason": repost_reason})

def agent_ignore_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to ignore an advertisement without any engagement.
    This represents scrolling past or dismissing an ad without interaction.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being ignored.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "ignore", "agent": agent_id, "ad": ad_id})

def read_shared_knowledge(**kwargs) -> str:
    """
    Reads the shared knowledge base accessible to all agents.
    Use this to understand collective trends or shared personality traits.

    Returns:
        str: The content of the shared knowledge file.
    """
    SHARED_KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'shared_knowledge.txt')
    try:
        with open(SHARED_KNOWLEDGE_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No shared knowledge found."

def write_shared_knowledge(content: str, **kwargs) -> str:
    """
    Writes or appends content to the shared knowledge base.
    Use this to contribute to the collective memory or shared personality.

    Args:
        content (str): The information to add to the shared knowledge base.

    Returns:
        str: A confirmation message.
    """
    SHARED_KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'shared_knowledge.txt')
    with open(SHARED_KNOWLEDGE_PATH, 'a') as f:
        f.write(f"\n{content}")
    return "Shared knowledge updated successfully."

# A list of all tool functions for easy registration
ALL_TOOLS_V2 = [
    agent_like_ad,
    agent_dislike_ad,
    agent_comment_ad,
    agent_repost_ad,
    agent_ignore_ad,
    read_shared_knowledge,
    write_shared_knowledge
] 