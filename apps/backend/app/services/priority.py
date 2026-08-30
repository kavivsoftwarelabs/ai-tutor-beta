def calculate_priority(weakness: float, prerequisite_importance: float, review_due: float, exam_importance: float) -> float:
    return (weakness * 0.40) + (prerequisite_importance * 0.25) + (review_due * 0.20) + (exam_importance * 0.15)
