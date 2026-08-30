# pipelines/content_seeding/seed.py
import csv
import sys
from pydantic import BaseModel, Field, field_validator

# Strict data mapping validation contract matching Postgres exactly
class CuratedResourceDTO(BaseModel):
    concept_id: str = Field(..., min_length=3)
    video_id: str = Field(..., min_length=11, max_length=11)
    start_time_seconds: int = Field(..., ge=0)
    end_time_seconds: int = Field(..., ge=1)
    title: str = Field(..., min_length=3)

    @field_validator('end_time_seconds')
    @classmethod
    def verify_timestamps(cls, v: int, info) -> int:
        if 'start_time_seconds' in info.data and v <= info.data['start_time_seconds']:
            raise ValueError("end_time_seconds must be strictly greater than start_time_seconds")
        return v

def parse_and_validate_csv(file_path: str):
    """
    Parses local curated file mapping and reports structural validation defects before SQL insertion.
    """
    validated_records = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_idx, row in enumerate(reader, start=1):
                try:
                    record = CuratedResourceDTO(
                        concept_id=row['concept_id'].strip(),
                        video_id=row['video_id'].strip(),
                        start_time_seconds=int(row['start_time_seconds']),
                        end_time_seconds=int(row['end_time_seconds']),
                        title=row['title'].strip()
                    )
                    validated_records.append(record.model_dump())
                except Exception as err:
                    print(f"❌ Structural CSV Schema Error at line {row_idx}: {err}")
                    sys.exit(1)
        print(f"✅ Successfully validated {len(validated_records)} curated resources.")
        return validated_records
    except FileNotFoundError:
        print(f"❌ Target data file missing at: {file_path}")
