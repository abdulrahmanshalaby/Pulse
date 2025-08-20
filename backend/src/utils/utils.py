from http.client import HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from Models.models import User
from authorization.auth import SECRET_KEY
import re



def _get_current_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

def extract_mentions(content: str) -> list[str]:
    """
    Extracts mentions like @username anywhere in text, even without spaces.
    Avoids simple email patterns by not matching @ followed by domain-like text.
    """
    # Match @ followed by 1+ letters/numbers/underscores
    pattern = r"@([A-Za-z0-9_]{1,15})"
    matches = re.findall(pattern, content)
    return matches

