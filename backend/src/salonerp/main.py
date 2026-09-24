"""App factory.

Using a factory (rather than a module-level `app = FastAPI()`) means tests
can spin up fresh app instances with different settings/overrides instead of
importing one shared global — see tests/conftest.py.
"""

from fastapi import FastAPI

from salonerp.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="SalonERP", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.env}

    # TODO(dev): mount module routers here as they're built, e.g.
    #   from salonerp.modules.booking.api import router as booking_router
    #   app.include_router(booking_router, prefix="/api/booking", tags=["booking"])

    return app


app = create_app()
