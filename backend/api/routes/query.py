from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import Optional, Dict, Any

from agent.nexus_agent import NexusAgent
from agent.playbooks import PLAYBOOKS

router = APIRouter()
agent = NexusAgent()

class QueryRequest(BaseModel):
    question: str
    context: Dict[str, Any] = {}
    playbook: Optional[str] = None

@router.post("/query")
async def run_query(request: QueryRequest):
    """
    Streaming endpoint. Returns Server-Sent Events.
    Each event is a JSON object with a 'type' field.
    """
    
    async def event_stream():
        try:
            async for event in agent.investigate(
                question=request.question,
                context=request.context
            ):
                yield f"data: {json.dumps(event)}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", 
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/playbooks")
async def list_playbooks():
    """Return the available canonical cross-source queries."""
    return PLAYBOOKS
