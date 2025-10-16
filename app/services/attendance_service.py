from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.schemas.attendance_schema import AttendanceCreate
from app.repositories.attendance_repository import AttendanceRepository
from datetime import datetime

class AttendanceService:
    def __init__(self):
        self.repo = AttendanceRepository()

    def create_attendance(self, db: Session, data: AttendanceCreate):
        attendance = Attendance(
            registration_id=data.registration_id,
            session_number=data.session_number,
            entry_timestamp=data.entry_timestamp or datetime.utcnow(),
            exit_timestamp=data.exit_timestamp,
            scanned_by_staff_id=data.scanned_by_staff_id,
        )
        return self.repo.create(db, attendance)

    def list_attendance(self, db: Session):
        return self.repo.get_all(db)

    def get_attendance(self, db: Session, attendance_id: int):
        return self.repo.get_by_id(db, attendance_id)
