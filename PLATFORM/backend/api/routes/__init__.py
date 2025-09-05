from fastapi import APIRouter

from routes import (
    oauth,
    users,
    instruments,
    patients,
    pathologies,
    patient_models,
    patient_pathologies, 
    studies,
    chats,
    message,
    alarm
)

app_router = APIRouter()


app_router.include_router(
    oauth.router,
    tags = ['authentication']
)

app_router.include_router(
    users.router,
    tags = ['users']
)

app_router.include_router(
    instruments.router,
    tags = ['instruments']
)

app_router.include_router(
    patients.router,
    tags = ['patients']
)

app_router.include_router(
    pathologies.router,
    tags = ['pathologies']
)

app_router.include_router(
    patient_pathologies.router,
    tags = ['patient_pathology']
)

app_router.include_router(
    patient_models.router,
    tags = ['patient_models']
)

app_router.include_router(
    studies.router,
    tags=['studies']
)

app_router.include_router(
    chats.router,
    tags=['chats']
)

app_router.include_router(
    message.router,
    tags=['message']
)

app_router.include_router(
    alarm.router,
    tags=['alarm']
)

