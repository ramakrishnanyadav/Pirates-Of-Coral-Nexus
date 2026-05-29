from fastapi import APIRouter
from coral.client import CoralClient

router = APIRouter()

@router.get("/schema")
async def get_schema():
    """Return live Coral schema for the frontend's schema explorer."""
    coral = CoralClient()
    return {
        "health": coral.health_check(),
        "tables": coral.get_tables()
    }
