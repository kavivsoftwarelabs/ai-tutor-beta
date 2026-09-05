# pipelines/content_seeding/seed.py

import csv
import sys
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


EXPECTED_COLUMNS = {
    "Topic ID",
    "Category",
    "Topic Name",
    "Prerequisite ID(s)",
    "Mastery Threshold (%)",
    "Resource Title",
    "Video ID",
    "Channel",
    "Start Time",
    "End Time",
    "Start Time (seconds)",
    "End Time (seconds)",
    "Timestamp Link",
    "Resource Type",
    "Verification Status",
}


class CuratedResourceDTO(BaseModel):
    topic_id: str = Field(..., min_length=3)
    category: str = Field(..., min_length=2)
    topic_name: str = Field(..., min_length=2)
    prerequisite_ids: list[str] = Field(default_factory=list)
    mastery_threshold: float = Field(..., ge=0, le=100)

    resource_title: str = Field(..., min_length=3)
    video_id: str | None = None
    channel: str | None = None

    start_time: str | None = None
    end_time: str | None = None
    start_time_seconds: int | None = Field(default=None, ge=0)
    end_time_seconds: int | None = Field(default=None, ge=1)

    timestamp_link: str | None = None
    resource_type: str | None = None
    verification_status: str = Field(..., min_length=3)

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, value):
        if value in (None, ""):
            return None

        if len(value) != 11:
            raise ValueError(
                "YouTube video ID must contain exactly 11 characters"
            )

        return value

    @field_validator("end_time_seconds")
    @classmethod
    def verify_timestamps(cls, value, info):
        start = info.data.get("start_time_seconds")

        if value is not None and start is not None and value <= start:
            raise ValueError(
                "end_time_seconds must be greater than "
                "start_time_seconds"
            )

        return value


def parse_prerequisites(value: str) -> list[str]:
    """
    Converts prerequisite notation into individual Topic IDs.

    Supported formats:
        Q01
        Q01,Q05
        Q01-Q12
        Q01, Q05
        Q01-Q12, L01
    """
    if not value or not value.strip():
        return []

    prerequisites = []

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        if "-" not in item:
            prerequisites.append(item)
            continue

        start_id, end_id = [
            part.strip()
            for part in item.split("-", 1)
        ]

        prefix_start = "".join(
            char for char in start_id if char.isalpha()
        )
        prefix_end = "".join(
            char for char in end_id if char.isalpha()
        )

        number_start = "".join(
            char for char in start_id if char.isdigit()
        )
        number_end = "".join(
            char for char in end_id if char.isdigit()
        )

        if (
            not prefix_start
            or not prefix_end
            or prefix_start != prefix_end
            or not number_start
            or not number_end
        ):
            raise ValueError(
                f"Invalid prerequisite range: {item}"
            )

        start_number = int(number_start)
        end_number = int(number_end)

        if end_number < start_number:
            raise ValueError(
                f"Prerequisite range is reversed: {item}"
            )

        for number in range(start_number, end_number + 1):
            prerequisites.append(
                f"{prefix_start}{number:02d}"
            )

    return prerequisites


def parse_optional_int(value: str):
    if not value or not value.strip():
        return None

    cleaned = value.strip()

    try:
        numeric_value = float(cleaned)

        if not numeric_value.is_integer():
            raise ValueError(
                f"Expected a whole number, got '{cleaned}'"
            )

        return int(numeric_value)

    except ValueError:
        raise ValueError(
            f"Invalid integer value: '{cleaned}'"
        )


def parse_and_validate_csv(file_path: str):
    validated_records = []

    try:
        with open(
            file_path,
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print("❌ CSV has no header row.")
                sys.exit(1)

            actual_columns = set(reader.fieldnames)
            missing_columns = EXPECTED_COLUMNS - actual_columns

            if missing_columns:
                print("❌ CSV is missing required columns:")

                for column in sorted(missing_columns):
                    print(f"   - {column}")

                sys.exit(1)

            print("✅ CSV column structure is valid.")

            topic_ids = set()
            rows = list(reader)

            for row_idx, row in enumerate(rows, start=2):

                try:
                    topic_id = row["Topic ID"].strip()

                    if not topic_id:
                        raise ValueError("Topic ID cannot be empty")

                    if topic_id in topic_ids:
                        raise ValueError(
                            f"Duplicate Topic ID: {topic_id}"
                        )

                    topic_ids.add(topic_id)

                    prerequisites = parse_prerequisites(
                        row["Prerequisite ID(s)"]
                    )

                    resource_title = row["Resource Title"].strip()

                    if not resource_title:
                        raise ValueError(
                            "Resource Title cannot be empty"
                        )

                    video_id = row["Video ID"].strip() or None

                    start_seconds = parse_optional_int(
                        row["Start Time (seconds)"]
                    )

                    end_seconds = parse_optional_int(
                        row["End Time (seconds)"]
                    )

                    if video_id is not None and start_seconds is None:
                        raise ValueError(
                            "A video resource must have "
                            "Start Time (seconds)"
                        )

                    if (
                        start_seconds is not None
                        and end_seconds is not None
                        and end_seconds <= start_seconds
                    ):
                        raise ValueError(
                            "End timestamp must be greater than "
                            "start timestamp"
                        )

                    record = CuratedResourceDTO(
                        topic_id=topic_id,
                        category=row["Category"].strip(),
                        topic_name=row["Topic Name"].strip(),
                        prerequisite_ids=prerequisites,
                        mastery_threshold=float(
                            row["Mastery Threshold (%)"]
                        ),
                        resource_title=resource_title,
                        video_id=video_id,
                        channel=row["Channel"].strip() or None,
                        start_time=row["Start Time"].strip() or None,
                        end_time=row["End Time"].strip() or None,
                        start_time_seconds=start_seconds,
                        end_time_seconds=end_seconds,
                        timestamp_link=(
                            row["Timestamp Link"].strip() or None
                        ),
                        resource_type=(
                            row["Resource Type"].strip() or None
                        ),
                        verification_status=(
                            row["Verification Status"].strip()
                        ),
                    )

                    validated_records.append(record.model_dump())

                except Exception as err:
                    print(
                        f"❌ Validation error at CSV line "
                        f"{row_idx}: {err}"
                    )
                    sys.exit(1)

            unknown_prerequisites = []

            for record in validated_records:
                for prerequisite in record["prerequisite_ids"]:

                    if prerequisite not in topic_ids:
                        unknown_prerequisites.append(
                            (
                                record["topic_id"],
                                prerequisite,
                            )
                        )

            if unknown_prerequisites:
                print(
                    "❌ Unknown prerequisite Topic IDs found:"
                )

                for topic_id, prerequisite in unknown_prerequisites:
                    print(
                        f"   {topic_id} → {prerequisite}"
                    )

                sys.exit(1)

            if len(validated_records) != 26:
                print(
                    "⚠️ Warning: expected 26 topic rows, "
                    f"but found {len(validated_records)}."
                )
            else:
                print("✅ Found all 26 topic rows.")

            manual_verification = [
                record
                for record in validated_records
                if (
                    "MANUAL_VERIFY" in record["verification_status"]
                    or "MANUAL_TIMESTAMP" in record["verification_status"]
                )
            ]

            if manual_verification:
                print()
                print(
                    "⚠️ Resources requiring manual verification:"
                )

                for record in manual_verification:
                    print(
                        f"   {record['topic_id']} - "
                        f"{record['topic_name']}"
                    )

            print()
            print(
                f"✅ Successfully validated "
                f"{len(validated_records)} resources."
            )

            return validated_records

    except FileNotFoundError:
        print(f"❌ Target data file missing: {file_path}")
        sys.exit(1)

    except ValueError as err:
        print(f"❌ CSV parsing error: {err}")
        sys.exit(1)


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    csv_path = (
        project_root
        / "pipelines"
        / "content_seeding"
        / "data"
        / "curated_videos.csv"
    )

    print("==============================================")
    print(" CUET GAT CURATED RESOURCE VALIDATOR")
    print("==============================================")
    print()
    print(f"Reading: {csv_path}")
    print()

    parse_and_validate_csv(str(csv_path))
