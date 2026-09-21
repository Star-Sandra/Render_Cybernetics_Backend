from uuid import UUID
from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from smartmama.repositories.visit_log_repository import get_active_pregnancy_id, create_visit_log, get_visits_by_chv, get_visits_by_mother
from smartmama.schemas.visit_log_schema import VisitLogCreate, Symptom, VisitLogResponse
from smartmama.models.visit_log_model import VisitLog
from smartmama.models.mother_model import Mother
from smartmama.models.pregnancy_tracking_model import Pregnancy
from smartmama.services.risk_model_service import predict_risk, RISK_RECOMMENDATIONS
import logging

logger = logging.getLogger(__name__)


def _validate_mother_and_chv(db: Session, mother_id: UUID, chv_id: UUID) -> Mother:
    """Validates mother existence and CHV authorization."""
    mother = db.query(Mother).filter(Mother.mother_id == mother_id).first()
    if not mother:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mother record not found"
        )

    if mother.chv_id != chv_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization Denied: You are not assigned to this mother."
        )
    return mother

def log_routine_visit(db: Session, visit_data: VisitLogCreate, chv_id: UUID) -> VisitLogResponse:
    """Resolves the mother's active pregnancy, scores risk, and saves the visit."""
    mother = _validate_mother_and_chv(db, visit_data.mother_id, chv_id)
    pregnancy_id = get_active_pregnancy_id(db, visit_data.mother_id)
    if pregnancy_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active pregnancy found for mother_id={visit_data.mother_id}"
        )
        
    risk_level, confidence_score, _ = calculate_risk(visit_data, mother)
    
    visit_log = create_visit_log(
        db=db,
        visit_data=visit_data,
        pregnancy_id=pregnancy_id,
        chv_id=chv_id,
        risk_level=risk_level,
        confidence_score=confidence_score,
    )

    return VisitLogResponse.model_validate(visit_log, from_attributes=True)

def calculate_risk(visit_data: VisitLogCreate, mother: Mother) -> tuple[str, float, str]:
    try:
        age = (visit_data.visit_date - mother.date_of_birth.date()).days // 365
        risk_level, confidence = predict_risk(
            age=age,
            systolic_bp=visit_data.systolic_bp,
            diastolic_bp=visit_data.diastolic_bp,
            blood_sugar=visit_data.blood_sugar,
            body_temp=visit_data.body_temp,
        )
        logger.info(f"Risk calculated via RF model: {risk_level} ({confidence})")
    except Exception as e:
        risk_level, confidence = _calculate_risk_rule_based(visit_data)
        logger.warning(f"RF model failed ({e}), fell back to rule-based: {risk_level} ({confidence})")
 
    recommendation = RISK_RECOMMENDATIONS[risk_level]
    return risk_level, confidence, recommendation

def _calculate_risk_rule_based(visit_data: VisitLogCreate) -> tuple[str, float]:
    selected = visit_data.logged_symptoms.selected
    other = visit_data.logged_symptoms.other

    bp_high = visit_data.systolic_bp >= 140 or visit_data.diastolic_bp >= 90
    bp_borderline = visit_data.systolic_bp >= 130 or visit_data.diastolic_bp >= 85
    bs_high = visit_data.blood_sugar >= 7.0
    bs_borderline = visit_data.blood_sugar >= 5.1
    fever = visit_data.body_temp >= 38.0

    bleeding = Symptom.BLEEDING in selected
    headache = Symptom.HEADACHE in selected
    swelling = Symptom.SWELLING in selected

    danger_signs = sum([bleeding, bp_high, bs_high])
    warning_signs = sum([headache, swelling, bp_borderline, bs_borderline, fever, bool(other)])

    if bleeding or bp_high or bs_high:
        risk_level = "High"
        confidence = min(0.75 + 0.05 * danger_signs + 0.03 * warning_signs, 0.95)
    elif warning_signs >= 1:
        risk_level = "Medium"
        confidence = min(0.6 + 0.05 * warning_signs, 0.85)
    else:
        risk_level = "Low"
        confidence = 0.6

    return risk_level, round(confidence, 2)


def get_chv_visit_history(db: Session, chv_id: UUID) -> list[VisitLog]:
    """All visits this CHV has personally logged."""
    return get_visits_by_chv(db, chv_id)


def get_mother_visit_history(db: Session, mother_id: UUID, chv_id: UUID) -> list[VisitLog]:
    """A mother's visit history, most recent first."""
    _validate_mother_and_chv(db, mother_id, chv_id)
    return list(reversed(get_visits_by_mother(db, mother_id, chv_id)))


def get_mother_risk_trend(db: Session, mother_id: UUID, chv_id: UUID) -> list[VisitLog]:
    """A mother's visits in chronological order, for graphing."""
    _validate_mother_and_chv(db, mother_id, chv_id)
    return get_visits_by_mother(db, mother_id, chv_id)