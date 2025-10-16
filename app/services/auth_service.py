from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.staff import Staff
from app.core.security import verify_password
from app.core.jwt import create_access_token
from datetime import timedelta

class AuthService:
    def login(self, db: Session, username: str, password: str):
        staff = db.query(Staff).filter(Staff.username == username).first()
        if not staff:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not verify_password(password, staff.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(data={"sub": str(staff.id)}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
