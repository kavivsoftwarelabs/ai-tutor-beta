from app.services.priority import (
    calculate_weakness,
    calculate_priority,
)


def test_weakness_from_mastery():
    """Verify mastery is correctly converted into weakness."""

    test_cases = [
        (0.0, 1.0),
        (25.0, 0.75),
        (50.0, 0.50),
        (75.0, 0.25),
        (100.0, 0.0),
    ]

    print("\n--- Weakness Calculation ---")

    for mastery, expected in test_cases:
        result = calculate_weakness(mastery)

        print(
            f"Mastery {mastery:>5.1f}% "
            f"-> Weakness {result:.2f} "
            f"(expected {expected:.2f})"
        )

        assert result == expected


def test_priority_formula():
    """Verify the exact 4-factor priority formula."""

    weakness = 0.70
    prerequisite_importance = 0.80
    review_due = 0.50
    exam_importance = 0.15

    result = calculate_priority(
        weakness=weakness,
        prerequisite_importance=prerequisite_importance,
        review_due=review_due,
        exam_importance=exam_importance,
    )

    expected = (
        weakness * 0.40
        + prerequisite_importance * 0.25
        + review_due * 0.20
        + exam_importance * 0.15
    )

    print("\n--- Priority Formula ---")
    print(f"Weakness:                {weakness:.2f} × 0.40")
    print(
        f"Prerequisite Importance: {prerequisite_importance:.2f} × 0.25"
    )
    print(f"Review Due:              {review_due:.2f} × 0.20")
    print(f"Exam Importance:        {exam_importance:.2f} × 0.15")
    print(f"Expected:               {expected:.4f}")
    print(f"Actual:                 {result:.4f}")

    assert result == expected


def test_priority_zero_inputs():
    """All zero factors should produce zero priority."""

    result = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    print("\n--- Zero Priority Test ---")
    print(f"Priority with all factors = 0: {result}")

    assert result == 0.0


def test_priority_maximum_inputs():
    """All factors at 1.0 should produce a priority of 1.0."""

    result = calculate_priority(
        weakness=1.0,
        prerequisite_importance=1.0,
        review_due=1.0,
        exam_importance=1.0,
    )

    print("\n--- Maximum Priority Test ---")
    print(f"Priority with all factors = 1: {result}")

    assert result == 1.0


def test_weakness_increases_as_mastery_decreases():
    """Lower mastery should produce higher weakness."""

    high_mastery = calculate_weakness(80.0)
    low_mastery = calculate_weakness(20.0)

    print("\n--- Mastery vs Weakness ---")
    print(f"80% mastery -> weakness {high_mastery:.2f}")
    print(f"20% mastery -> weakness {low_mastery:.2f}")

    assert low_mastery > high_mastery


def test_each_priority_factor_increases_score():
    """
    Verify that increasing each individual factor
    increases the overall priority score.
    """

    baseline = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    weakness_score = calculate_priority(
        weakness=1.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    prereq_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=1.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    review_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=1.0,
        exam_importance=0.0,
    )

    exam_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=1.0,
    )

    print("\n--- Individual Priority Factors ---")
    print(f"Baseline:               {baseline:.2f}")
    print(f"Weakness only:          {weakness_score:.2f}")
    print(f"Prerequisite only:      {prereq_score:.2f}")
    print(f"Review Due only:        {review_score:.2f}")
    print(f"Exam Importance only:   {exam_score:.2f}")

    assert weakness_score > baseline
    assert prereq_score > baseline
    assert review_score > baseline
    assert exam_score > baseline


def test_priority_weights_have_expected_order():
    """
    Verify the relative weights:
    Weakness > Prerequisite Importance > Review Due > Exam Importance.
    """

    weakness_score = calculate_priority(
        weakness=1.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    prereq_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=1.0,
        review_due=0.0,
        exam_importance=0.0,
    )

    review_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=1.0,
        exam_importance=0.0,
    )

    exam_score = calculate_priority(
        weakness=0.0,
        prerequisite_importance=0.0,
        review_due=0.0,
        exam_importance=1.0,
    )

    print("\n--- Priority Weight Ordering ---")
    print(f"Weakness:               {weakness_score:.2f}")
    print(f"Prerequisite Importance:{prereq_score:.2f}")
    print(f"Review Due:             {review_score:.2f}")
    print(f"Exam Importance:        {exam_score:.2f}")

    assert weakness_score > prereq_score
    assert prereq_score > review_score
    assert review_score > exam_score