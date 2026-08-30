from __future__ import annotations

from app.models.schemas import QuizItem


def update_quiz_result(
    current_quiz: list[QuizItem],
    answered_correctly: bool,
    item_id: str,
) -> list[QuizItem]:
    updated = []
    for item in current_quiz:
        if item.id == item_id:
            item_dict = item.model_dump()
            item_dict["last_result"] = answered_correctly
            updated.append(item_dict)
        else:
            updated.append(item.model_dump())
    return [QuizItem(**payload) for payload in updated]
