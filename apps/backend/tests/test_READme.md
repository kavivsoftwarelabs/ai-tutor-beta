# Backend Test Suite

This directory contains the automated tests for the **Heuristic Priority Engine** used by the adaptive learning scheduler.

The purpose of these tests is to verify that the engine follows the rules defined for the current MVP implementation when deciding:

1. How weak a student is in a concept.
2. How a concept's priority score is calculated.
3. Whether a concept is eligible based on its prerequisites.
4. How multiple prerequisites are handled.
5. How concepts are ranked by priority.
6. How the student's available study time limits the daily plan.

These tests currently use controlled Python data rather than PostgreSQL. This allows the core scheduling logic to be tested independently from the database, Docker, FastAPI, and other application components.

---

## Test Files

```text
tests/
├── README.md
├── test_priority.py
└── test_scheduler.py
```

### `test_priority.py`

Tests the mathematical logic used by the priority engine.

It verifies:

* Weakness calculation
* Priority calculation
* Zero-value behavior
* Maximum-value behavior
* Relationship between mastery and weakness
* Influence of each priority factor
* Relative weighting of the four priority factors

### `test_scheduler.py`

Tests the behavior of the learning scheduler.

It verifies:

* Prerequisite eligibility
* Prerequisite blocking
* The exact 60% mastery boundary
* Multiple prerequisites
* Missing prerequisite state
* Priority-based ordering
* Study-time constraints
* The complete seeded CUET concept dependency graph

---

# 1. Weakness Calculation

The engine converts a student's mastery score into a weakness factor.

The formula is:

```text
Weakness = (100 - mastery_score) / 100
```

Therefore:

```text
Mastery       Weakness
----------------------
0%              1.00
25%             0.75
50%             0.50
75%             0.25
100%            0.00
```

### What we are testing

The tests verify that:

* Lower mastery produces higher weakness.
* Higher mastery produces lower weakness.
* 0% mastery produces maximum weakness.
* 100% mastery produces zero weakness.

This ensures that the priority engine correctly interprets a student's current mastery level.

---

# 2. Priority Score Calculation

The engine calculates concept priority using four factors:

```text
Priority =
    (Weakness × 0.40)
  + (PrerequisiteImportance × 0.25)
  + (ReviewDue × 0.20)
  + (ExamImportance × 0.15)
```

The current MVP weights are:

| Factor                  | Weight |
| ----------------------- | -----: |
| Weakness                |   0.40 |
| Prerequisite Importance |   0.25 |
| Review Due              |   0.20 |
| Exam Importance         |   0.15 |

### Example

Given:

```text
Weakness                = 0.70
Prerequisite Importance = 0.80
Review Due              = 0.50
Exam Importance         = 0.15
```

The expected result is:

```text
(0.70 × 0.40)
+ (0.80 × 0.25)
+ (0.50 × 0.20)
+ (0.15 × 0.15)

= 0.2800
+ 0.2000
+ 0.1000
+ 0.0225

= 0.6025
```

The test verifies that the implementation returns exactly this result.

---

# 3. Priority Edge Cases

The engine is also tested with extreme inputs.

### All factors are zero

```text
Weakness                = 0
Prerequisite Importance = 0
Review Due              = 0
Exam Importance         = 0
```

Expected:

```text
Priority = 0
```

### All factors are maximum

```text
Weakness                = 1
Prerequisite Importance = 1
Review Due              = 1
Exam Importance         = 1
```

Because the weights sum to 1:

```text
0.40 + 0.25 + 0.20 + 0.15 = 1.00
```

Expected:

```text
Priority = 1
```

These tests make sure the formula behaves correctly at its boundaries.

---

# 4. Individual Priority Factors

The tests verify that each factor actually affects the priority score.

Starting from:

```text
Weakness                = 0
Prerequisite Importance = 0
Review Due              = 0
Exam Importance         = 0
```

we increase one factor at a time.

Expected behavior:

```text
Increase Weakness
        ↓
Priority increases

Increase Prerequisite Importance
        ↓
Priority increases

Increase Review Due
        ↓
Priority increases

Increase Exam Importance
        ↓
Priority increases
```

This ensures that no factor has accidentally been ignored or disconnected from the calculation.

---

# 5. Priority Weight Ordering

The tests also verify the relative importance of the four factors.

The current weights are:

```text
Weakness                 0.40
Prerequisite Importance  0.25
Review Due               0.20
Exam Importance         0.15
```

Therefore:

```text
Weakness
    >
Prerequisite Importance
    >
Review Due
    >
Exam Importance
```

The test isolates each factor by setting it to `1.0` while keeping the others at `0`.

Expected:

```text
Weakness only              → 0.40
Prerequisite only          → 0.25
Review Due only            → 0.20
Exam Importance only       → 0.15
```

This verifies that the implemented weights match the intended formula.

---

# 6. Prerequisite Eligibility

The scheduler maintains an eligible learning pool.

A concept can enter this pool only when its prerequisites satisfy the mastery requirement.

The rule is:

```text
Any prerequisite < 60%
        ↓
     BLOCKED

All prerequisites >= 60%
        ↓
     ELIGIBLE
```

### Example

```text
Profit & Loss
    └── requires → Percentages
```

If:

```text
Percentages = 90%
```

then:

```text
Profit & Loss → ELIGIBLE
```

If:

```text
Percentages = 59%
```

then:

```text
Profit & Loss → BLOCKED
```

The tests verify both cases.

---

# 7. The 60% Boundary

The exact boundary is important because the rule uses:

```text
mastery < 60% → blocked
mastery >= 60% → eligible
```

The test checks:

```text
59.0%  → BLOCKED
59.9%  → BLOCKED
60.0%  → ELIGIBLE
60.1%  → ELIGIBLE
61.0%  → ELIGIBLE
```

This is called boundary-value testing.

It ensures that the implementation has not accidentally used:

```text
<= 60
```

instead of:

```text
< 60
```

---

# 8. Multiple Prerequisites

Some concepts require more than one prerequisite.

The current concept graph includes:

```text
Simple Interest
    ├── Percentages
    └── Ratio
```

The scheduler requires **every prerequisite** to meet the 60% threshold.

For example:

```text
Percentages = 80%  → PASS
Ratio       = 55%  → FAIL
```

Therefore:

```text
Simple Interest → BLOCKED
```

The test also verifies the opposite case:

```text
Percentages = 80% → PASS
Ratio       = 75% → PASS
```

Therefore:

```text
Simple Interest → ELIGIBLE
```

This confirms that the scheduler does not incorrectly allow a concept when only some of its prerequisites are ready.

---

# 9. Missing Prerequisite State

The scheduler also handles a situation where a prerequisite exists in the concept graph but the student has no recorded knowledge state for it.

For example:

```text
Profit & Loss
    └── requires → Percentages

Student state:
    Percentages → NOT FOUND
```

The scheduler treats the missing state as not sufficiently mastered and blocks the dependent concept.

Expected:

```text
Profit & Loss → BLOCKED
```

This prevents the system from assuming that an unknown prerequisite is already mastered.

---

# 10. Priority-Based Ordering

After prerequisite filtering, eligible concepts are ranked according to their priority score.

For example:

```text
Concept A
Mastery = 90%
Weakness = 0.10
```

versus:

```text
Concept B
Mastery = 20%
Weakness = 0.80
```

When the other factors are equal:

```text
Concept B
    ↓
Higher weakness
    ↓
Higher priority
    ↓
Appears earlier in the plan
```

The scheduler test verifies that the weaker concept is ranked first.

---

# 11. Study-Time Constraint

The scheduler must respect the student's available study time.

The current MVP scheduler assigns:

```text
25 minutes per concept
```

Therefore:

```text
Available Time    Maximum Concepts
----------------------------------
25 minutes             1
50 minutes             2
75 minutes             3
```

The tests verify that the generated plan never exceeds the available time.

For example:

```text
Available = 50 minutes

Concept 1 = 25 min
Concept 2 = 25 min
Concept 3 = 25 min
```

The scheduler should produce:

```text
Concept 1
Concept 2

Total = 50 minutes
```

and exclude the third concept because it would exceed the available time.

---

# 12. Realistic CUET Concept Graph

The test suite also verifies the scheduler using the current seeded concept structure.

```text
Percentages & Fractions
        │
        ├──────────────→ Profit & Loss
        │
        │
        └──────────────┐
                       ↓
Ratio & Proportion → Simple Interest
                            │
                            ↓
                    Compound Interest
```

The test uses student states such as:

```text
Percentages = 80%
Ratio       = 55%
Profit/Loss = 30%
Simple Int. = 20%
Compound    = 10%
```

The scheduler should reason as follows:

```text
Percentages
80%
→ Ready

Ratio
55%
→ No prerequisites, therefore available

Profit & Loss
requires Percentages
Percentages = 80%
→ Eligible

Simple Interest
requires Percentages + Ratio
Ratio = 55%
→ Blocked

Compound Interest
requires Simple Interest
Simple Interest is blocked
→ Blocked
```

This verifies that the individual prerequisite rules work together correctly on a realistic dependency graph.

---

# 13. What These Tests Do Not Test

The current test suite focuses on the deterministic scheduling logic.

It does **not** currently test:

```text
PostgreSQL connectivity
Database queries
Docker configuration
FastAPI endpoints
Authentication
LLM responses
YouTube/resource retrieval
Quiz persistence
Production database state
```

Those should be covered by integration or end-to-end tests later.

The current test flow is:

```text
Controlled test data
        ↓
priority.py / scheduler.py
        ↓
Expected behavior
```

The future integration flow will be:

```text
PostgreSQL
        ↓
Database layer
        ↓
Student + concept data
        ↓
Scheduler
        ↓
Priority Engine
        ↓
Daily Learning Plan
```

---

# 14. Running the Tests

From:

```text
apps/backend/
```

activate the virtual environment:

```bash
source .venv/bin/activate
```

Run all tests:

```bash
python3 -m pytest -v
```

To display the verification messages printed by the tests:

```bash
python3 -m pytest -v -s
```

The `-s` option allows the diagnostic `print()` output to appear in the terminal.

---

# 15. Expected Result

The current suite contains **18 tests**.

A successful run should end with something similar to:

```text
============================= test session starts =============================

collected 18 items

tests/test_priority.py::test_weakness_from_mastery PASSED
tests/test_priority.py::test_priority_formula PASSED
tests/test_priority.py::test_priority_zero_inputs PASSED
tests/test_priority.py::test_priority_maximum_inputs PASSED
...
tests/test_scheduler.py::test_realistic_cuet_concept_graph PASSED

============================== 18 passed ==============================
```

The exact Python and pytest versions may differ.

The important condition is:

```text
18 passed
0 failed
0 errors
```

---

# 16. Definition of Done

The current heuristic engine test suite is considered complete for this stage when it verifies:

```text
[✓] Weakness calculation
[✓] Priority formula
[✓] Zero-value behavior
[✓] Maximum-value behavior
[✓] Relationship between mastery and weakness
[✓] Influence of all priority factors
[✓] Correct priority weights
[✓] Prerequisite >= 60% eligibility
[✓] Prerequisite < 60% blocking
[✓] Exact 60% boundary
[✓] Multiple prerequisite blocking
[✓] Multiple prerequisite success
[✓] Missing prerequisite state
[✓] Priority-based ordering
[✓] Study-time limit
[✓] 25-minute budget behavior
[✓] 50-minute budget behavior
[✓] Realistic CUET dependency graph
```

Current verification status:

```text
18 / 18 tests passing
```

This establishes that the current implementation follows the defined MVP scheduling rules for the tested scenarios. It does not establish that the heuristic weights are pedagogically optimal; those weights can be evaluated and calibrated later using real learning outcomes.
