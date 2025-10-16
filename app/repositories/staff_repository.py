from sqlalchemy.orm import Session
from app.models.staff import Staff

class StaffRepository:
    def get_all(self, db: Session):
        return db.query(Staff).all()

    def create(self, db: Session, staff: Staff):
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff
