import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, async_session_factory
from routers import auth, patients, dsm5, kindcheck, locks, audit, websocket
from services.lock_service import cleanup_expired_locks, release_all_user_locks
from websocket.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    async def cleanup_locks_on_disconnect(user_id: int):
        async with async_session_factory() as db:
            released = await release_all_user_locks(db, user_id)
            for lock in released:
                await manager.notify_lock_changed(
                    lock["table_name"], lock["record_id"], None, None
                )

    manager.on_user_gone = cleanup_locks_on_disconnect

    task = asyncio.create_task(lock_cleanup_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def lock_cleanup_loop():
    while True:
        await asyncio.sleep(60)
        async with async_session_factory() as db:
            await cleanup_expired_locks(db)


app = FastAPI(title="Patiëntenbeheer API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(dsm5.router)
app.include_router(kindcheck.router)
app.include_router(locks.router)
app.include_router(audit.router)
app.include_router(websocket.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}

frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(str(frontend_dist / "index.html"))
