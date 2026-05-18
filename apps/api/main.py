"""FastAPI backend for Agent Platform."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta
import jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session as DBSession

from .models import (
    User, Agent, Conversation, Message, Tool, Workflow, WorkflowRun, Job, UsageLog,
    get_session, init_db
)


# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Pydantic models


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_provider: Optional[str] = "ollama"
    model_name: Optional[str] = "llama3"
    temperature: float = 0.7
    max_tokens: int = 4096
    memory_type: str = "buffer"
    tools: List[str] = []
    is_public: bool = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    memory_type: Optional[str] = None
    tools: Optional[List[str]] = None
    is_public: Optional[bool] = None


class AgentResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    system_prompt: Optional[str]
    model_provider: Optional[str]
    model_name: Optional[str]
    temperature: float
    max_tokens: int
    memory_type: str
    tools: List[str]
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls: Optional[List[Dict]]
    tool_results: Optional[List[Dict]] = None
    token_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    agent_id: str
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None
    stream: bool = True


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    tool_calls: Optional[List[Dict]] = None


class ToolCreate(BaseModel):
    name: str
    description: Optional[str] = None
    schema: Dict[str, Any]
    handler: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}


class ToolResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    schema: Dict[str, Any]
    handler: Optional[str]
    is_global: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowCreate(BaseModel):
    name: str
    agent_id: Optional[str] = None
    definition: Dict[str, Any]


class WorkflowRunResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Validate JWT token and return current user."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = get_session()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_token(user_id: str, expires_delta: timedelta = timedelta(days=7)) -> str:
    """Create JWT token for user."""
    expires = datetime.utcnow() + expires_delta
    payload = {"sub": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Application


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown."""
    # Startup
    try:
        init_db()
    except Exception:
        pass  # Database may not be available
    yield
    # Shutdown


app = FastAPI(
    title="Agent Platform API",
    description="AI Agent Platform with LangGraph orchestration",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth endpoints


@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user."""
    db = get_session()
    
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = bcrypt.hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=password_hash,
        name=user.name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    
    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        created_at=new_user.created_at,
    )


@app.post("/api/auth/login")
async def login(email: str, password: str):
    """Login and get JWT token."""
    db = get_session()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(str(user.id))
    return {"token": token, "user": UserResponse.from_orm(user)}


# Agent endpoints


@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents(current_user: User = Depends(get_current_user)):
    """List all agents for current user."""
    db = get_session()
    agents = db.query(Agent).filter(
        (Agent.user_id == current_user.id) | (Agent.is_public == True)
    ).all()
    db.close()
    return [AgentResponse.from_orm(a) for a in agents]


@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new agent."""
    db = get_session()
    new_agent = Agent(
        user_id=str(current_user.id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_name=agent.model_name,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        memory_type=agent.memory_type,
        tools=agent.tools,
        is_public=agent.is_public,
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    db.close()
    return AgentResponse.from_orm(new_agent)


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    """Get agent by ID."""
    db = get_session()
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    db.close()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.from_orm(agent)


@app.patch("/api/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent: AgentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update agent."""
    db = get_session()
    db_agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == str(current_user.id)
    ).first()
    
    if not db_agent:
        db.close()
        raise HTTPException(status_code=404, detail="Agent not found")
    
    for key, value in agent.model_dump(exclude_unset=True).items():
        setattr(db_agent, key, value)
    
    db.commit()
    db.refresh(db_agent)
    db.close()
    return AgentResponse.from_orm(db_agent)


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    """Delete agent."""
    db = get_session()
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == str(current_user.id)
    ).first()
    
    if not agent:
        db.close()
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    db.close()
    return {"message": "Agent deleted"}


# Conversation endpoints


@app.get("/api/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    agent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List conversations."""
    db = get_session()
    query = db.query(Conversation).filter(Conversation.user_id == str(current_user.id))
    
    if agent_id:
        query = query.filter(Conversation.agent_id == agent_id)
    
    conversations = query.order_by(Conversation.updated_at.desc()).all()
    db.close()
    return [ConversationResponse.from_orm(c) for c in conversations]


@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conv: ConversationCreate,
    current_user: User = Depends(get_current_user)
):
    """Create conversation."""
    db = get_session()
    new_conv = Conversation(
        agent_id=conv.agent_id,
        user_id=str(current_user.id),
        title=conv.title or "New Conversation",
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    db.close()
    return ConversationResponse.from_orm(new_conv)


# Message endpoints


@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation messages."""
    db = get_session()
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    db.close()
    return [MessageResponse.from_orm(m) for m in messages]


# Chat endpoint


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with agent."""
    from .agents.runner import run_agent
    
    # Get or create conversation
    db = get_session()
    
    if request.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        if not conv:
            db.close()
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        if not request.agent_id:
            db.close()
            raise HTTPException(status_code=400, detail="agent_id required")
        
        conv = Conversation(
            agent_id=request.agent_id,
            user_id=str(current_user.id),
            title=request.message[:50],
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # Save user message
    user_message = Message(
        conversation_id=str(conv.id),
        role="user",
        content=request.message,
    )
    db.add(user_message)
    db.commit()
    db.close()
    
    # Run agent
    response, tool_calls = await run_agent(
        conversation_id=str(conv.id),
        message=request.message,
    )
    
    # Save assistant message
    db = get_session()
    assistant_message = Message(
        conversation_id=str(conv.id),
        role="assistant",
        content=response,
        tool_calls=tool_calls,
    )
    db.add(assistant_message)
    db.commit()
    db.close()
    
    return ChatResponse(
        message=response,
        conversation_id=str(conv.id),
        tool_calls=tool_calls,
    )


# Tools endpoints


@app.get("/api/tools", response_model=List[ToolResponse])
async def list_tools():
    """List available tools."""
    db = get_session()
    tools = db.query(Tool).all()
    db.close()
    return [ToolResponse.from_orm(t) for t in tools]


@app.post("/api/tools", response_model=ToolResponse)
async def create_tool(
    tool: ToolCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new tool."""
    db = get_session()
    new_tool = Tool(
        name=tool.name,
        description=tool.description,
        schema=tool.schema,
        handler=tool.handler,
        config=tool.config,
    )
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    db.close()
    return ToolResponse.from_orm(new_tool)


# Workflow endpoints


@app.post("/api/workflows/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: str,
    input: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Run workflow."""
    from .agents.workflow import execute_workflow
    
    db = get_session()
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.user_id == str(current_user.id)
    ).first()
    
    if not workflow:
        db.close()
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    run = WorkflowRun(
        workflow_id=workflow_id,
        status="running",
        input=input,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    try:
        result = await execute_workflow(workflow.definition, input)
        run.status = "completed"
        run.output = result
        run.completed_at = datetime.utcnow()
    except Exception as e:
        run.status = "failed"
        run.error = str(e)
        run.completed_at = datetime.utcnow()
    
    db.commit()
    db.close()
    return WorkflowRunResponse.from_orm(run)


# Health check


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)