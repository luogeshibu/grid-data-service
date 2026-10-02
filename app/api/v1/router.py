from fastapi import APIRouter

from app.api.v1.endpoints import catalog, directory, equipment, health, profiles, realtime, topology

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(profiles.router)
api_v1_router.include_router(realtime.router)
api_v1_router.include_router(catalog.router)
api_v1_router.include_router(directory.router)
api_v1_router.include_router(equipment.router)
api_v1_router.include_router(topology.router)
