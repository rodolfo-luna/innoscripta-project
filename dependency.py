from jose import jwt
from jose.exceptions import JOSEError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

async def has_access(credentials: HTTPAuthorizationCredentials= Depends(security)):
    """
        Function that is used to validate the token in the case that it requires it
    """
    token = credentials.credentials
    if token != "InnoREK2I8vlUtMHqBE6ko916ZvdHqdMT5rT2x":
        raise HTTPException(status_code=401, detail="Invalid token!")
    return True
    