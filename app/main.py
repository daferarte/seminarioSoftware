from fastapi import FastAPI
from app.api.v1.routers import (
    staff_router,
    participants_router,
    events_router,
    registrations_router,
    attendances_router,
    auth_router,
)

app = FastAPI(title="Event Management API")

app.include_router(auth_router.router)
app.include_router(staff_router.router)
app.include_router(participants_router.router)
app.include_router(events_router.router)
app.include_router(registrations_router.router)
app.include_router(attendances_router.router)
