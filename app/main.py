from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from .auth import verify_password, get_password_hash

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    print(f"Username: {username}, Password: {password}")
    user = crud.get_user_by_username(db, username=username)
    if not user:
        print("User not found")
    else:
        print(f"User found: {user.username}, Hashed Password: {user.hashed_password}")
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    
    response = RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    
    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(password)
    user = schemas.UserCreate(username=username, password=hashed_password)
    db_user = crud.create_user(db, user, hashed_password)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tasks = crud.get_tasks(db, user_id=int(user_id)) 
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

@app.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request):
    return templates.TemplateResponse("create_task.html", {"request": request})

@app.post("/tasks/create", response_class=HTMLResponse)
async def create_task(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    task = schemas.TaskCreate(
        title=form.get("title"),
        description=form.get("description"),
        status=form.get("status"),
        priority=form.get("priority"),
        deadline=form.get("deadline")
    )
    crud.create_task(db, task, user_id=int(user_id))
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})

@app.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    form = await request.form()
    task = schemas.TaskCreate(
        title=form.get("title"),
        description=form.get("description"),
        status=form.get("status"),
        priority=form.get("priority"),
        deadline=form.get("deadline")
    )
    crud.update_task(db, task_id, task)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
async def delete_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)