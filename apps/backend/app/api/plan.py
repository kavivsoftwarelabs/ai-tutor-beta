from fastapi import APIRouter

router = APIRouter()


@router.get("/plan")
def get_plan():
    return {
        "status": "ok",
        "message": "Study plan endpoint ready",
        "plan": ["Warm-up review", "Targeted drill", "Timed quiz"],
    }
