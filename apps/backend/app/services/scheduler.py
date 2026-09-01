from typing import Any, Dict, List

from app.services.priority import (
    calculate_weakness,
    calculate_priority,
)


class HeuristicPriorityScheduler:

    @classmethod
    def generate_daily_agenda(
        cls,
        user_available_minutes: int,
        all_concepts: List[Dict[str, Any]],
        user_states: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        eligible_pool: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # 1. Calculate prerequisite importance
        # ---------------------------------------------------------

        prereq_counts: Dict[str, int] = {}

        for concept in all_concepts:
            prereqs = concept.get("prerequisites", []) or []

            for parent_id in prereqs:
                prereq_counts[parent_id] = (
                    prereq_counts.get(parent_id, 0) + 1
                )

        max_possible_prereqs = (
            max(prereq_counts.values())
            if prereq_counts
            else 1
        )

        # ---------------------------------------------------------
        # 2. Filter concepts by prerequisite mastery
        # ---------------------------------------------------------

        for concept in all_concepts:

            concept_id = concept["id"]

            prereqs = concept.get("prerequisites", []) or []

            prerequisites_satisfied = True

            for prerequisite_id in prereqs:

                state = user_states.get(
                    prerequisite_id,
                    {"mastery_score": 50.0},
                )

                if state["mastery_score"] < 60.0:
                    prerequisites_satisfied = False
                    break

            if not prerequisites_satisfied:
                continue

            # -----------------------------------------------------
            # 3. Get student's state
            # -----------------------------------------------------

            state = user_states.get(
                concept_id,
                {
                    "mastery_score": 50.0,
                    "review_due_factor": 0.0,
                },
            )

            mastery_score = state["mastery_score"]

            review_due_factor = state["review_due_factor"]

            # -----------------------------------------------------
            # 4. Calculate prerequisite importance
            # -----------------------------------------------------

            prerequisite_importance = (
                prereq_counts.get(concept_id, 0)
                / max_possible_prereqs
            )

            # -----------------------------------------------------
            # 5. Calculate weakness
            # -----------------------------------------------------

            weakness = calculate_weakness(
                mastery_score
            )

            # -----------------------------------------------------
            # 6. Calculate priority
            # -----------------------------------------------------

            priority_score = calculate_priority(
                weakness=weakness,
                prerequisite_importance=prerequisite_importance,
                review_due=review_due_factor,
                exam_importance=concept.get(
                    "exam_importance",
                    0.15,
                ),
            )

            eligible_pool.append(
                {
                    "concept_id": concept_id,
                    "name": concept["name"],
                    "priority_score": round(
                        priority_score,
                        4,
                    ),
                    "estimated_minutes": 25,
                }
            )

        # ---------------------------------------------------------
        # 7. Rank concepts
        # ---------------------------------------------------------

        eligible_pool.sort(
            key=lambda item: item["priority_score"],
            reverse=True,
        )

        # ---------------------------------------------------------
        # 8. Respect available study time
        # ---------------------------------------------------------

        daily_plan: List[Dict[str, Any]] = []

        time_used = 0

        for item in eligible_pool:

            if (
                time_used
                + item["estimated_minutes"]
                <= user_available_minutes
            ):
                daily_plan.append(item)

                time_used += item["estimated_minutes"]

        return daily_plan