from fastapi import APIRouter

router = APIRouter()


@router.get("/diagnostic")
def get_diagnostic():
    return {
        "status": "ok",
        "message": "Diagnostic endpoint ready",
        "topics": ["mathematics", "science", "english"],
    }
