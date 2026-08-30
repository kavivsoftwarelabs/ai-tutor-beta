from fastapi import APIRouter

router = APIRouter()


@router.get("/quiz")
def get_quiz():
    return {
        "status": "ok",
        "message": "Quiz endpoint ready",
        "questions": [],
    }
