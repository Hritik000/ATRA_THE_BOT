"""Agents Endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def agents_info():
    """Agents module information."""
    return {"message": "Agents endpoints placeholder"}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent information (placeholder)."""
    return {"message": f"Agent {agent_id} info placeholder"}


@router.post("/{agent_id}/run")
async def run_agent(agent_id: str):
    """Run an agent (placeholder)."""
    return {"message": f"Running agent {agent_id} placeholder"}