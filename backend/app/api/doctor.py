import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.identity_router import get_request_context, RequestContext
from app.models.user import User, UserRole
from app.core.mcp.patient_record import PatientRecordModule
from app.schemas.doctor import PatientRecordResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/doctor", tags=["doctor"])
patient_record_module = PatientRecordModule()


@router.get("/patient/{patient_id}", response_model=PatientRecordResponse)
async def get_patient_record(
    patient_id: int,
    ctx: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db),
):
    if ctx.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access patient records",
        )

    result = await db.execute(select(User).where(User.id == patient_id))
    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {patient_id}",
        )

    if patient.role != UserRole.patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {patient_id} is not a patient",
        )

    case_result = await patient_record_module.execute(
        "patient_record.query_case", {"patient_name": patient.name}
    )
    visit_result = await patient_record_module.execute(
        "patient_record.query_visit", {"patient_name": patient.name}
    )
    prescription_result = await patient_record_module.execute(
        "patient_record.query_prescription", {"patient_name": patient.name}
    )

    return PatientRecordResponse(
        patient_id=patient.id,
        patient_name=patient.name,
        patient_role=patient.role.value,
        cases=case_result.data.get("cases", []) if case_result.data else [],
        visits=visit_result.data.get("visits", []) if visit_result.data else [],
        prescriptions=prescription_result.data.get("prescriptions", []) if prescription_result.data else [],
    )
