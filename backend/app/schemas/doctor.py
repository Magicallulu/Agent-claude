from pydantic import BaseModel


class PatientRecordResponse(BaseModel):
    patient_id: int
    patient_name: str | None = None
    patient_role: str | None = None
    cases: list[dict] = []
    visits: list[dict] = []
    prescriptions: list[dict] = []
