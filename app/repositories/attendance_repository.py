from sqlalchemy.orm import Session
from app.models.attendance import Attendance

class AttendanceRepository:
    def get_all(self, db: Session):
        return db.query(Attendance).all()

    def get_by_id(self, db: Session, attendance_id: int):
        return db.query(Attendance).filter(Attendance.id == attendance_id).first()

    def create(self, db: Session, attendance: Attendance):
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance
