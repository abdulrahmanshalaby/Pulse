import uuid
from sqlalchemy.orm import Session
import os
from Models.models import Media
from dotenv import load_dotenv
load_dotenv() 
try:
    import boto3  # type: ignore
    _HAS_BOTO3 = True
except Exception:
    _HAS_BOTO3 = False

def _make_object_key(file_name: str) -> str:
    # avoid collisions, add uuid prefix
    safe_name = file_name.replace(" ", "_")
    return f"uploads/{uuid.uuid4().hex}_{safe_name}"

class MediaService:
    def __init__(self,db:Session):
        self.db = db
    def generate_presigned_url(self, file_name: str, file_type: str):
     if not file_name:
        raise ValueError("file_name is required")
     if not file_type:
        raise ValueError("file_type is required")

     bucket = os.getenv("AWS_S3_BUCKET")
     media_base = os.getenv("MEDIA_BASE_URL", "").rstrip("/")
     region = "eu-north-1"
     print (bucket)
     print(_HAS_BOTO3)
     key = _make_object_key(file_name)
     expires_in = 3600  # seconds (1 hour), adjust as needed

    # S3 presigned PUT url mode
     if bucket and _HAS_BOTO3:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region)
        params = {"Bucket": bucket, "Key": key, "ContentType": file_type}
        presigned_put = s3.generate_presigned_url("put_object", Params=params, ExpiresIn=expires_in)
        # public file URL - depends on bucket policy; we assume standard S3 URL
        file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        return presigned_put, file_url

    # Fallback: local/static upload URL (no presign) -- client must PUT/POST to this URL if server supports it,
    # or use it as the final public file URL after uploading to whatever storage they use.
     if media_base:
        file_url = f"{media_base}/{key}"
        upload_url = file_url  # not presigned, but returned for client convenience
        return upload_url, file_url

    # Last resort: return a path-like URL and the file_url as-is
     file_url = f"/{key}"
     upload_url = file_url
     return upload_url, file_url
    def finalize_upload(self, file_url: str, file_type: str):
     if not file_url:
        raise ValueError("file_url is required")
     if not file_type:
        raise ValueError("file_type is required")
     if self.db is None:
        raise ValueError("db session is required")

     media = Media(file_url=file_url, file_type=file_type)
     self.db.add(media)
     self.db.commit()
     self.db.refresh(media)
     return media