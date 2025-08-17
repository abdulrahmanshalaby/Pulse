
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from schemas.schemas import FinalizeUploadRequest, FinalizeUploadResponse, PresignRequest, PresignResponse
from services.media import MediaService
router= APIRouter(prefix="/api/media",tags=["media"])

@router.post("/presign", response_model=PresignResponse)
def get_presigned_url(req: PresignRequest,db:Session=Depends(get_db)):
    media_service = MediaService(db)
    upload_url, file_url = media_service.generate_presigned_url(req.file_name, req.file_type)
    return {"upload_url": upload_url, "file_url": file_url}

@router.post("/finalize", response_model=FinalizeUploadResponse)
def finalize_upload(req: FinalizeUploadRequest, db: Session = Depends(get_db)):
    media_service = MediaService(db)
    try:
        media = media_service.finalize_upload(req.file_url, req.file_type)
        return {"media_id": media.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")