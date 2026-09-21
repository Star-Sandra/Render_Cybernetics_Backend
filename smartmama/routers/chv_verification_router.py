# from fastapi import APIRouter, Body, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from uuid import UUID
# from database import get_db
# from smartmama.models.chv import CHV
# from smartmama.security import require_chv, TokenPayload
# from smartmama.services.id_analyzer_service import id_analyzer_service
# from smartmama.services.attachment_scanner_service import attachment_scanner_service
# from smartmama.services.chv_verification_service import (
#     mark_chv_pending_verification,
#     apply_docupass_result_to_chv,
# )

# router = APIRouter(
#     prefix="/chv-verification",
#     tags=["CHV Verification"]
# )

# @router.post("/start-docupass")
# async def start_docupass(current_chv: TokenPayload = Depends(require_chv), db: Session = Depends(get_db)):
#     chv = db.query(CHV).filter(CHV.user_id == current_chv.user_id).first()
#     if not chv:
#         raise HTTPException(404, "CHV profile not found")

#     callback_url = "https://api2-eu.idanalyzer.com/docupass"

#     session = await id_analyzer_service.create_docupass_session(str(chv.chv_id), callback_url)

#     return {
#         "docupass_url": session.get("url"),
#         "reference": session.get("reference"),
#     }


# @router.post("/docupass-callback")
# async def docupass_callback(request: Request, db: Session = Depends(get_db)):
#     payload = await request.json()
#     reference = payload.get("reference")

#     if not reference:
#         raise HTTPException(400, "Missing reference")

#     chv = db.query(CHV).filter(CHV.chv_id == UUID(reference)).first()
#     if not chv:
#         raise HTTPException(404, "CHV not found")

#     parsed = id_analyzer_service.parse_docupass_result(payload)
#     apply_docupass_result_to_chv(db, chv, parsed)

#     return {"message": "DocuPass verification stored", "chv_id": str(chv.chv_id)}


# @router.post("/submit-certificate")
# async def submit_certificate(
#     document_url: str = Body(..., embed=True),
#     certificate_number: str | None = Body(None, embed=True),
#     current_chv: TokenPayload = Depends(require_chv),
#     db: Session = Depends(get_db),
# ):
#     chv = db.query(CHV).filter(CHV.user_id == current_chv.user_id).first()
#     if not chv:
#         raise HTTPException(status_code=404, detail="CHV profile not found.")

#     try:
#         scan_result = await attachment_scanner_service.scan_file_url(document_url)
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"Attachment scan failed: {e}")

#     is_safe = attachment_scanner_service.is_file_safe(scan_result)
#     if not is_safe:
#         chv.certificate_status = "Rejected"
#         chv.rejection_notes = "Certificate file failed security scan."
#         db.commit()
#         db.refresh(chv)
#         raise HTTPException(
#             status_code=400,
#             detail="Certificate file is unsafe or malicious. Upload a clean document.",
#         )

#     updated = mark_chv_pending_verification(
#         db=db,
#         chv=chv,
#         document_url=document_url,
#         certificate_number=certificate_number,
#     )

#     return {
#         "message": "Certificate submitted and passed security scan.",
#         "certificate_status": updated.certificate_status,
#         "chv_id": str(updated.chv_id),
#     }



import os
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from smartmama.models.chv import CHV
from smartmama.security import require_chv, TokenPayload
from smartmama.services.id_analyzer_service import id_analyzer_service
from smartmama.services.attachment_scanner_service import attachment_scanner_service
from smartmama.services.chv_verification_service import (
    mark_chv_pending_verification,
    apply_docupass_result_to_chv,
)

router = APIRouter(
    prefix="/chv-verification",
    tags=["CHV Verification"]
)

# ---- Demo switch: set DEMO_AUTO_APPROVE_CHV=true in Render to enable ----
DEMO_AUTO_APPROVE = os.getenv("DEMO_AUTO_APPROVE_CHV", "false").strip().lower() == "true"
APPROVED_STATUS = "Verified"  # must match what approve_certificate sets

DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "storage", "chv_documents"
)
ALLOWED_EXTS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_BYTES = 10 * 1024 * 1024


async def _save_document(file: UploadFile, user_id, kind: str) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, "Invalid file type. Only PDF, JPG and PNG allowed.")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(400, "File size must be under 10MB")
    os.makedirs(DOCS_DIR, exist_ok=True)
    filename = f"{user_id}_{kind}{ext}"
    with open(os.path.join(DOCS_DIR, filename), "wb") as f:
        f.write(content)
    return f"/api/v1/chv-verification/documents/{filename}"


@router.post("/upload-certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    current_chv: TokenPayload = Depends(require_chv),
):
    url = await _save_document(file, current_chv.user_id, "certificate")
    return {"message": "Certificate uploaded.", "document_url": url}


@router.post("/upload-id-proof")
async def upload_id_proof(
    file: UploadFile = File(...),
    current_chv: TokenPayload = Depends(require_chv),
):
    url = await _save_document(file, current_chv.user_id, "id_proof")
    return {"message": "ID proof uploaded.", "document_url": url}


@router.get("/documents/{filename}")
def get_document(filename: str):
    path = os.path.join(DOCS_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        raise HTTPException(404, "Document not found")
    return FileResponse(path)

@router.get("/verification-status")
def verification_status(
    current_chv: TokenPayload = Depends(require_chv),
    db: Session = Depends(get_db),
):
    chv = db.query(CHV).filter(CHV.user_id == current_chv.user_id).first()
    if not chv:
        raise HTTPException(404, "CHV profile not found")
    return {
        "chv_id": str(chv.chv_id),
        "certificate_status": chv.certificate_status,
        "has_id_proof": DEMO_AUTO_APPROVE,
    }


@router.post("/start-docupass")
async def start_docupass(current_chv: TokenPayload = Depends(require_chv), db: Session = Depends(get_db)):
    chv = db.query(CHV).filter(CHV.user_id == current_chv.user_id).first()
    if not chv:
        raise HTTPException(404, "CHV profile not found")

    callback_url = "https://api2-eu.idanalyzer.com/docupass"

    session = await id_analyzer_service.create_docupass_session(str(chv.chv_id), callback_url)

    return {
        "docupass_url": session.get("url"),
        "reference": session.get("reference"),
    }


@router.post("/docupass-callback")
async def docupass_callback(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    reference = payload.get("reference")

    if not reference:
        raise HTTPException(400, "Missing reference")

    chv = db.query(CHV).filter(CHV.chv_id == UUID(reference)).first()
    if not chv:
        raise HTTPException(404, "CHV not found")

    parsed = id_analyzer_service.parse_docupass_result(payload)
    apply_docupass_result_to_chv(db, chv, parsed)

    return {"message": "DocuPass verification stored", "chv_id": str(chv.chv_id)}


@router.post("/submit-certificate")
async def submit_certificate(
    document_url: str = Body(..., embed=True),
    certificate_number: str | None = Body(None, embed=True),
    current_chv: TokenPayload = Depends(require_chv),
    db: Session = Depends(get_db),
):
    chv = db.query(CHV).filter(CHV.user_id == current_chv.user_id).first()
    if not chv:
        raise HTTPException(status_code=404, detail="CHV profile not found.")

    if not DEMO_AUTO_APPROVE:
        try:
            scan_result = await attachment_scanner_service.scan_file_url(document_url)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Attachment scan failed: {e}")

        is_safe = attachment_scanner_service.is_file_safe(scan_result)
        if not is_safe:
            chv.certificate_status = "Rejected"
            chv.rejection_notes = "Certificate file failed security scan."
            db.commit()
            db.refresh(chv)
            raise HTTPException(
                status_code=400,
                detail="Certificate file is unsafe or malicious. Upload a clean document.",
            )

    updated = mark_chv_pending_verification(
        db=db,
        chv=chv,
        document_url=document_url,
        certificate_number=certificate_number,
    )

    if DEMO_AUTO_APPROVE:
        updated.certificate_status = APPROVED_STATUS
        db.commit()
        db.refresh(updated)

    return {
        "message": "Certificate submitted.",
        "certificate_status": updated.certificate_status,
        "chv_id": str(updated.chv_id),
    }