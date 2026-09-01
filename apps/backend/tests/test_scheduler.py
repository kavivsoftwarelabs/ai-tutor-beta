from app.services.scheduler import HeuristicPriorityScheduler


def get_concept_ids(result):
    """Helper to extract concept IDs from a daily plan."""
    return [item["concept_id"] for item in result]


def test_concept_is_eligible_when_prerequisite_is_above_60():
    """
    A concept should be allowed when its prerequisite
    has mastery >= 60%.
    """

    concepts = [
        {
            "id": "math_pct",
            "name": "Percentages",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "math_pl",
            "name": "Profit and Loss",
            "prerequisites": ["math_pct"],
            "exam_importance": 0.15,
        },
    ]

    user_states = {
        "math_pct": {
            "mastery_score": 90.0,
            "review_due_factor": 0.0,
        },
        "math_pl": {
            "mastery_score": 20.0,
            "review_due_factor": 0.0,
        },
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=30,
        all_concepts=concepts,
        user_states=user_states,
    )

    concept_ids = get_concept_ids(result)

    print("\n--- Prerequisite >= 60% ---")
    print("Percentages mastery: 90%")
    print("Required threshold: 60%")
    print(f"Daily plan: {result}")

    assert "math_pl" in concept_ids


def test_concept_is_blocked_when_prerequisite_is_below_60():
    """
    A concept must be blocked when its prerequisite
    has mastery below 60%.
    """

    concepts = [
        {
            "id": "math_pct",
            "name": "Percentages",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "math_pl",
            "name": "Profit and Loss",
            "prerequisites": ["math_pct"],
            "exam_importance": 0.15,
        },
    ]

    user_states = {
        "math_pct": {
            "mastery_score": 59.0,
            "review_due_factor": 0.0,
        }
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=30,
        all_concepts=concepts,
        user_states=user_states,
    )

    concept_ids = get_concept_ids(result)

    print("\n--- Prerequisite < 60% ---")
    print("Percentages mastery: 59%")
    print("Required threshold: 60%")
    print("Profit and Loss should be BLOCKED")
    print(f"Daily plan: {result}")

    assert "math_pl" not in concept_ids


def test_prerequisite_threshold_boundary():
    """
    Verify the exact boundary:
    <60% = blocked
    >=60% = eligible
    """

    concepts = [
        {
            "id": "math_pl",
            "name": "Profit and Loss",
            "prerequisites": ["math_pct"],
            "exam_importance": 0.15,
        }
    ]

    print("\n--- 60% Boundary Test ---")

    for mastery, expected_eligible in [
        (59.0, False),
        (59.9, False),
        (60.0, True),
        (60.1, True),
        (61.0, True),
    ]:

        user_states = {
            "math_pct": {
                "mastery_score": mastery,
                "review_due_factor": 0.0,
            }
        }

        result = HeuristicPriorityScheduler.generate_daily_agenda(
            user_available_minutes=30,
            all_concepts=concepts,
            user_states=user_states,
        )

        eligible = len(result) > 0

        print(
            f"Mastery {mastery:4.1f}% "
            f"-> Eligible: {eligible} "
            f"(expected: {expected_eligible})"
        )

        assert eligible == expected_eligible


def test_all_prerequisites_must_be_above_60():
    """
    If a concept has multiple prerequisites, every prerequisite
    must have mastery >= 60%.
    """

    concepts = [
        {
            "id": "math_si",
            "name": "Simple Interest",
            "prerequisites": [
                "math_pct",
                "math_ratio",
            ],
            "exam_importance": 0.10,
        }
    ]

    user_states = {
        "math_pct": {
            "mastery_score": 80.0,
            "review_due_factor": 0.0,
        },
        "math_ratio": {
            "mastery_score": 55.0,
            "review_due_factor": 0.0,
        },
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=30,
        all_concepts=concepts,
        user_states=user_states,
    )

    print("\n--- Multiple Prerequisite Test ---")
    print("Percentages: 80% -> PASS")
    print("Ratio:       55% -> FAIL")
    print("Simple Interest should be BLOCKED")
    print(f"Daily plan: {result}")

    assert result == []


def test_multiple_prerequisites_all_pass():
    """
    A concept with multiple prerequisites should be eligible
    when all prerequisites are >= 60%.
    """

    concepts = [
        {
            "id": "math_si",
            "name": "Simple Interest",
            "prerequisites": [
                "math_pct",
                "math_ratio",
            ],
            "exam_importance": 0.10,
        }
    ]

    user_states = {
        "math_pct": {
            "mastery_score": 80.0,
            "review_due_factor": 0.0,
        },
        "math_ratio": {
            "mastery_score": 75.0,
            "review_due_factor": 0.0,
        },
        "math_si": {
            "mastery_score": 20.0,
            "review_due_factor": 0.0,
        },
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=30,
        all_concepts=concepts,
        user_states=user_states,
    )

    print("\n--- Multiple Prerequisite Success ---")
    print("Percentages: 80% -> PASS")
    print("Ratio:       75% -> PASS")
    print("Simple Interest should be ELIGIBLE")
    print(f"Daily plan: {result}")

    assert "math_si" in get_concept_ids(result)


def test_missing_prerequisite_state_blocks_concept():
    """
    If a prerequisite has no student state, the scheduler
    should treat it as not ready rather than allowing the concept.
    """

    concepts = [
        {
            "id": "math_pl",
            "name": "Profit and Loss",
            "prerequisites": ["math_pct"],
            "exam_importance": 0.15,
        }
    ]

    user_states = {}

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=30,
        all_concepts=concepts,
        user_states=user_states,
    )

    print("\n--- Missing Prerequisite State ---")
    print("Percentages state: NOT FOUND")
    print("Expected: Profit and Loss BLOCKED")
    print(f"Daily plan: {result}")

    assert result == []


def test_concepts_are_sorted_by_priority():
    """
    A weaker concept should receive higher priority when
    the other factors are equal.
    """

    concepts = [
        {
            "id": "strong",
            "name": "Strong Concept",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "weak",
            "name": "Weak Concept",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
    ]

    user_states = {
        "strong": {
            "mastery_score": 90.0,
            "review_due_factor": 0.0,
        },
        "weak": {
            "mastery_score": 20.0,
            "review_due_factor": 0.0,
        },
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=100,
        all_concepts=concepts,
        user_states=user_states,
    )

    print("\n--- Priority Ordering ---")

    for position, item in enumerate(result, start=1):
        print(
            f"{position}. {item['name']} "
            f"-> Priority: {item['priority_score']}"
        )

    assert result[0]["concept_id"] == "weak"


def test_daily_plan_respects_time_budget():
    """
    The scheduler must never exceed the student's
    available study time.
    """

    concepts = [
        {
            "id": "concept_1",
            "name": "Concept 1",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "concept_2",
            "name": "Concept 2",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "concept_3",
            "name": "Concept 3",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
    ]

    available_minutes = 50

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=available_minutes,
        all_concepts=concepts,
        user_states={},
    )

    total_minutes = sum(
        item["estimated_minutes"]
        for item in result
    )

    print("\n--- Time Budget Test ---")
    print(f"Available: {available_minutes} minutes")
    print(f"Scheduled: {total_minutes} minutes")

    for item in result:
        print(
            f"  - {item['name']} "
            f"({item['estimated_minutes']} min)"
        )

    assert total_minutes <= available_minutes


def test_25_minutes_allows_one_concept():
    """
    Current MVP scheduler assigns 25 minutes per concept.
    Therefore 25 available minutes should allow exactly one.
    """

    concepts = [
        {
            "id": "concept_1",
            "name": "Concept 1",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "concept_2",
            "name": "Concept 2",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
    ]

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=25,
        all_concepts=concepts,
        user_states={},
    )

    print("\n--- 25-Minute Budget Test ---")
    print(f"Concepts selected: {len(result)}")
    print(f"Plan: {result}")

    assert len(result) == 1


def test_50_minutes_allows_two_concepts():
    """
    Current MVP scheduler assigns 25 minutes per concept.
    Therefore 50 available minutes should allow two.
    """

    concepts = [
        {
            "id": "concept_1",
            "name": "Concept 1",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "concept_2",
            "name": "Concept 2",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "concept_3",
            "name": "Concept 3",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
    ]

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=50,
        all_concepts=concepts,
        user_states={},
    )

    print("\n--- 50-Minute Budget Test ---")
    print(f"Concepts selected: {len(result)}")
    print(f"Plan: {result}")

    assert len(result) == 2


def test_realistic_cuet_concept_graph():
    """
    Test the scheduler against the current five-concept
    General Aptitude prerequisite structure.
    """

    concepts = [
        {
            "id": "math_pct",
            "name": "Percentages & Fractions",
            "prerequisites": [],
            "exam_importance": 0.15,
        },
        {
            "id": "math_pl",
            "name": "Profit and Loss",
            "prerequisites": ["math_pct"],
            "exam_importance": 0.15,
        },
        {
            "id": "math_ratio",
            "name": "Ratio and Proportion",
            "prerequisites": [],
            "exam_importance": 0.12,
        },
        {
            "id": "math_si",
            "name": "Simple Interest",
            "prerequisites": [
                "math_pct",
                "math_ratio",
            ],
            "exam_importance": 0.10,
        },
        {
            "id": "math_ci",
            "name": "Compound Interest",
            "prerequisites": ["math_si"],
            "exam_importance": 0.10,
        },
    ]

    user_states = {
        "math_pct": {
            "mastery_score": 80.0,
            "review_due_factor": 0.0,
        },
        "math_ratio": {
            "mastery_score": 55.0,
            "review_due_factor": 0.0,
        },
        "math_pl": {
            "mastery_score": 30.0,
            "review_due_factor": 0.0,
        },
        "math_si": {
            "mastery_score": 20.0,
            "review_due_factor": 0.0,
        },
        "math_ci": {
            "mastery_score": 10.0,
            "review_due_factor": 0.0,
        },
    }

    result = HeuristicPriorityScheduler.generate_daily_agenda(
        user_available_minutes=100,
        all_concepts=concepts,
        user_states=user_states,
    )

    concept_ids = get_concept_ids(result)

    print("\n--- Realistic CUET Concept Graph ---")
    print("Percentages: 80% -> READY")
    print("Ratio:       55% -> READY (no prerequisites)")
    print("Profit/Loss: requires Percentages -> ELIGIBLE")
    print("Simple Interest: Ratio 55% -> BLOCKED")
    print("Compound Interest: Simple Interest blocked -> BLOCKED")
    print(f"\nGenerated learning pool/plan: {result}")

    assert "math_pl" in concept_ids
    assert "math_si" not in concept_ids
    assert "math_ci" not in concept_ids
