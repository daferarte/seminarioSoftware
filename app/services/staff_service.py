from sqlalchemy.orm import Session
from app.models.staff import Staff
from app.schemas.staff_schema import StaffCreate
from app.repositories.staff_repository import StaffRepository
from app.core.security import hash_password

class StaffService:
    def __init__(self):
        self.repo = StaffRepository()

    def create_staff(self, db: Session, data: StaffCreate):
        hashed_pw = hash_password(data.password)
        staff = Staff(
            username=data.username,
            full_name=data.full_name,
            email=data.email,
            role=data.role,
            password=hashed_pw,
        )
        return self.repo.create(db, staff)

    def list_staff(self, db: Session):
        return self.repo.get_all(db)
