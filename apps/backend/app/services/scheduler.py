# apps/backend/app/services/scheduler.py
from typing import Any, Dict, List


class HeuristicPriorityScheduler:
    """
    Implements the 4-factor deterministic scoring engine for AI Tutor Beta:
    Priority = (Weakness * 0.40) + (PrerequisiteImportance * 0.25) +
    (ReviewDue * 0.20) + (ExamImportance * 0.15)
    """

    @staticmethod
    def calculate_priority_score(
        mastery_score: float,
        prereq_importance: float,
        review_due_factor: float,
        exam_importance: float,
    ) -> float:
        # Step A: Invert mastery to calculate the Weakness Factor.
        # A lower score indicates a higher weakness value, maximizing the
        # learning gain.
        weakness_factor = (100.0 - mastery_score) / 100.0

        # Step B: Compute the linear weighted score matrix.
        score = (
            (weakness_factor * 0.40)
            + (prereq_importance * 0.25)
            + (review_due_factor * 0.20)
            + (exam_importance * 0.15)
        )
        return round(score, 4)

    @classmethod
    def generate_daily_agenda(
        cls,
        user_available_minutes: int,
        all_concepts: List[Dict[str, Any]],
        user_states: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        all_concepts: list of dicts representing all entries in the concepts
        table.
        user_states: dictionary mapping concept_id string -> user knowledge
        tracking payload rows.
        """
        eligible_pool: List[Dict[str, Any]] = []

        # Step 1: Pre-calculate the out-degree importance for every
        # prerequisite node dynamically.
        prereq_counts: Dict[str, int] = {}
        for concept in all_concepts:
            # Safely check raw database json array types.
            prereqs = concept.get("prerequisites", []) or []
            for parent_id in prereqs:
                prereq_counts[parent_id] = prereq_counts.get(parent_id, 0) + 1

        # Step 2: Evaluate eligibility constraints for every node option.
        for concept in all_concepts:
            cid = concept["id"]
            prereqs = concept.get("prerequisites", []) or []

            # Prerequisite Check: if any prerequisite is weak (< 60% mastery),
            # block this concept.
            prereqs_satisfied = True
            for parent_id in prereqs:
                parent_state = user_states.get(
                    parent_id,
                    {"mastery_score": 50.0},
                )
                if parent_state["mastery_score"] < 60.0:
                    prereqs_satisfied = False
                    break

            if not prereqs_satisfied:
                continue

            # Fetch the student's metrics, or use defaults for a fresh node.
            state = user_states.get(
                cid,
                {"mastery_score": 50.0, "review_due_factor": 0.0},
            )

            # Map structural weights to normalized inputs.
            max_possible_prereqs = (
                max(prereq_counts.values()) if prereq_counts else 1
            )
            current_prereq_importance = (
                prereq_counts.get(cid, 0) / max_possible_prereqs
            )

            # Calculate final numeric score for ranking priority.
            priority_score = cls.calculate_priority_score(
                mastery_score=state["mastery_score"],
                prereq_importance=current_prereq_importance,
                review_due_factor=state["review_due_factor"],
                exam_importance=concept.get("exam_importance", 0.15),
            )

            eligible_pool.append(
                {
                    "concept_id": cid,
                    "name": concept["name"],
                    "priority_score": priority_score,
                    # Assume a fixed 25-minute module duration budget for
                    # the lean MVP.
                    "estimated_minutes": 25,
                }
            )

        # Step 3: Sort eligible nodes by highest priority weight.
        eligible_pool.sort(key=lambda x: x["priority_score"], reverse=True)

        # Step 4: Pack the daily schedule within the user's available time
        # budget.
        daily_plan: List[Dict[str, Any]] = []
        time_used = 0

        for item in eligible_pool:
            if time_used + item["estimated_minutes"] <= user_available_minutes:
                daily_plan.append(item)
                time_used += item["estimated_minutes"]

        return daily_plan
