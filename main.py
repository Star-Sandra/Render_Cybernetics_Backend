# import os
# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from database import engine, Base
# from smartmama.models.chv import CHV
# from smartmama.models.mother_model import Mother
# from smartmama.models.visit_log_model import VisitLog
# from smartmama.models.location_model import Location as location_model
# from smartmama.routers.chv_router import router as chv_router
# from smartmama.routers.mother_router import router as mother_router
# from smartmama.routers.visit_router import router as visit_router
# from smartmama.routers.location_router import router as location_router
# from smartmama.routers.pregnancy_tracking_router import router as pregnancy_tracking_router
# from smartmama.routers.risk_assessment_router import router as risk_assessment_router
# from smartmama.routers.portal import router as portal_router
# from smartmama.routers.pdf import router as pdf_router
# from smartmama.routers.auth_router import router as auth_router
# from smartmama.routers.supervisor_router import router as supervisor_router
# from smartmama.routers.admin_router import router as admin_router
# from smartmama.routers.chv_verification_router import router as chv_verification_router
# from smartmama.routers.ticket_router import router as ticket_router
# from smartmama.routers.audit_log_router import router as audit_log_router
# from fastapi import Request
# from fastapi.responses import JSONResponse
# import logging

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#    # Base.metadata.create_all(bind=engine)
#     yield

# app = FastAPI(
#     title="SmartMama API",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# ALLOWED_ORIGINS = [
#     origin.strip()
#     for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
#     if origin.strip()
# ] or ["http://localhost:3000"]

# app.add_middleware(
#     "http",
#     CORSMiddleware,
#     allow_origins=ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PATCH", "OPTIONS", "DELETE"],
#     allow_headers=["Content-Type", "Authorization"],
# )
# async def log_errors_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as e:
#         # This forces the full python error backtrace to display on your screen
#         logging.error(f"SANDBOX CRASH LOG: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={"detail": f"Internal Error: {str(e)}"}
#         )


# app.include_router(visit_router, prefix="/api/v1")
# app.include_router(location_router, prefix="/api/v1")
# app.include_router(chv_router, prefix="/api/v1")
# app.include_router(mother_router, prefix="/api/v1")
# app.include_router(pregnancy_tracking_router, prefix="/api/v1")
# app.include_router(risk_assessment_router, prefix="/api/v1")
# app.include_router(portal_router, prefix="/api/v1")
# app.include_router(pdf_router, prefix="/api/v1")
# app.include_router(auth_router, prefix="/api/v1")
# app.include_router(supervisor_router, prefix="/api/v1")
# app.include_router(admin_router, prefix= "/api/v1")
# app.include_router(chv_verification_router)
# app.include_router(ticket_router, prefix="/api/v1")
# app.include_router(audit_log_router, prefix="/api/v1")

# @app.get("/", tags=["System Status"])
# def read_root():
#     return {
#         "status": "online",
#         "service": "SmartMama Core Framework",
#     }

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#     )





import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from database import engine, Base
from smartmama.models.chv import CHV
from smartmama.models.mother_model import Mother
from smartmama.models.visit_log_model import VisitLog
from smartmama.models.location_model import Location as location_model

from smartmama.routers.chv_router import router as chv_router
from smartmama.routers.mother_router import router as mother_router
from smartmama.routers.visit_router import router as visit_router
from smartmama.routers.location_router import router as location_router
from smartmama.routers.pregnancy_tracking_router import router as pregnancy_tracking_router
from smartmama.routers.risk_assessment_router import router as risk_assessment_router
from smartmama.routers.portal import router as portal_router
from smartmama.routers.pdf import router as pdf_router
from smartmama.routers.auth_router import router as auth_router
from smartmama.routers.supervisor_router import router as supervisor_router
from smartmama.routers.admin_router import router as admin_router
from smartmama.routers.chv_verification_router import router as chv_verification_router
from smartmama.routers.ticket_router import router as ticket_router
from smartmama.routers.audit_log_router import router as audit_log_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="SmartMama API",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
] or ["http://localhost:3000"]

# FIXED: Cleaned up CORSMiddleware configuration registration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# FIXED: Added the required interceptor decorator registration tag
@app.middleware("http")
async def log_errors_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # This forces the full python error backtrace to display on your screen
        logging.error(f"SANDBOX CRASH LOG: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Error: {str(e)}"}
        )

app.include_router(visit_router, prefix="/api/v1")
app.include_router(location_router, prefix="/api/v1")
app.include_router(chv_router, prefix="/api/v1")
app.include_router(mother_router, prefix="/api/v1")
app.include_router(pregnancy_tracking_router, prefix="/api/v1")
app.include_router(risk_assessment_router, prefix="/api/v1")
app.include_router(portal_router, prefix="/api/v1")
app.include_router(pdf_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(supervisor_router, prefix="/api/v1")
app.include_router(admin_router, prefix= "/api/v1")
app.include_router(chv_verification_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")
app.include_router(audit_log_router, prefix="/api/v1")

@app.get("/", tags=["System Status"])
def read_root():
    return {
        "status": "online",
        "service": "SmartMama Core Framework",
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
