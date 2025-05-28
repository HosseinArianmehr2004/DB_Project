from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import OperationFailure
from config import templates
import database

# Security Parts
from routes.auth import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from security_config import ACCESS_TOKEN_EXPIRE_MINUTES

# Routers
from routes.auth import router as auth_router
from routes.profile import router as profile_router
from routes.add_playlist import router as add_playlist_router
from routes.playlist import router as playlist_router


app = FastAPI()
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Too many requests. Try again in {ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
        },
    )


# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def setup_indexes():
    try:
        await database.db.users.drop_index("username_1")
    except OperationFailure:
        pass

    await database.db.users.create_index(
        [("username", 1)],
        unique=True,
        partialFilterExpression={"username": {"$type": "string"}},
    )


# Route to render index.html
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(add_playlist_router)
app.include_router(playlist_router)
