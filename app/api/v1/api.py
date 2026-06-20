from fastapi import APIRouter

from app.api.v1.endpoints import auth, sequence, mutation, restriction, codon, pipeline, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(sequence.router)
api_router.include_router(mutation.router)
api_router.include_router(restriction.router)
api_router.include_router(codon.router)
api_router.include_router(pipeline.router)
api_router.include_router(ws.router)
