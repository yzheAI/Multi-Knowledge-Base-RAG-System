from sqlalchemy.orm import Session
from app.schemas.agent_schema import AgentRequest
from agent.agent import run_agent
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.database.session import get_db

agent_router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)


@agent_router.post("/")
async def use_agent(
        request: AgentRequest,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    return run_agent(
        db,
        request.query,
        user.id,
        request.kb_name,
        request.filters
    )
