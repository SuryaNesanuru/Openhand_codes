"""LangGraph agent runner."""
import os
from typing import List, Dict, Any, Optional, Tuple
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

from packages.db.models import Message, Agent, get_session
from ..tools.registry import get_tool_handler


class AgentState(dict):
    """Agent state for LangGraph."""
    messages: List[Any]
    tool_calls: List[Dict]
    tool_results: List[Dict]
    agent_config: Dict[str, Any]


def get_llm(provider: str, model: str, temperature: float = 0.7):
    """Get LLM client based on provider."""
    if provider == "ollama" and ChatOllama:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
    elif (provider == "openai" or provider == "openrouter") and ChatOpenAI:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if provider == "openrouter":
            base_url = "https://openrouter.ai/v1"
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
        )
    else:
        # Fallback to mock for demo
        return MockLLM()


class MockLLM:
    """Mock LLM for when no real LLM available."""
    async def ainvoke(self, messages):
        return MockResponse("This is a demo response. Configure an LLM provider to enable real AI responses.")


class MockResponse:
    content = ""


async def call_model(state: AgentState) -> AgentState:
    """Call LLM to process messages."""
    config = state.get("agent_config", {})
    provider = config.get("model_provider", "ollama")
    model = config.get("model_name", "llama3")
    temperature = config.get("temperature", 0.7)
    
    llm = get_llm(provider, model, temperature)
    
    system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
    
    messages = [SystemMessage(content=system_prompt)]
    for msg in state.get("messages", []):
        if hasattr(msg, 'role') and msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif hasattr(msg, 'role') and msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    response = await llm.ainvoke(messages)
    
    state["response"] = response.content if hasattr(response, 'content') else str(response)
    return state


async def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end."""
    if state.get("tool_calls"):
        return "execute_tools"
    return END


def create_agent_graph():
    """Create the agent workflow graph."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("call_model", call_model)
    
    workflow.set_entry_point("call_model")
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "execute_tools": "execute_tools",
            END: END,
        }
    )
    
    return workflow.compile()


async def run_agent(
    conversation_id: str,
    message: str,
    agent_id: Optional[str] = None,
) -> Tuple[str, List[Dict]]:
    """Run the agent with a message."""
    from packages.db.models import Agent, Conversation
    
    db = get_session()
    
    # Get agent config
    if agent_id:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            db.close()
            return "Agent not found", []
        
        config = {
            "system_prompt": agent.system_prompt,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
            "memory_type": agent.memory_type,
            "tools": agent.tools or [],
        }
    else:
        config = {
            "system_prompt": "You are a helpful AI assistant.",
            "model_provider": "ollama",
            "model_name": "llama3",
            "temperature": 0.7,
            "tools": [],
        }
    
    # Get conversation history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    db.close()
    
    # Build state
    state = AgentState(
        messages=messages,
        tool_calls=[],
        tool_results=[],
        agent_config=config,
    )
    
    # Run graph
    try:
        graph = create_agent_graph()
        result = await graph.ainvoke(state)
    except Exception as e:
        return f"Error: {str(e)}", []
    
    return result.get("response", ""), result.get("tool_calls", [])