from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import database, models

app = FastAPI()

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates directory
templates = Jinja2Templates(directory="templates")


# Route to render index.html
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(user: models.User):
    # Check if username or email already exists
    existing_user = await database.db.users.find_one(
        {"$or": [{"username": user.username}, {"email": user.email}]}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    # Insert user into the database
    result = await database.db.users.insert_one(user.dict())
    return {"message": "User registered successfully", "id": str(result.inserted_id)}


@app.get("/users")
async def get_all_users():
    users = await database.db.users.find().to_list(100)
    for user in users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for JSON serialization
    return users
