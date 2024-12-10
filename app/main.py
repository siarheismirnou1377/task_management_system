from datetime import datetime
from fastapi import Cookie, FastAPI, Request, Depends, HTTPException, status, Query
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

def get_current_user(session_token: str = Cookie(None), db: Session = Depends(get_db)) -> models.User:
    if session_token is None:
        return None
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    session = crud.get_session(db, session_token)
    if session is None or session.expires_at < datetime.utcnow():
        return None
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    
    return session.user

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    session = crud.create_session(db, user.id)
    response = RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session.session_token, httponly=True)
    return response

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if session_token:
        crud.delete_session(db, session_token)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_token")
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

@app.get("/update_password", response_class=HTMLResponse)
async def update_password_page(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    return templates.TemplateResponse("update_password.html", {
        "request": request,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks,
        "errors": {}  # Передаём пустой словарь, чтобы избежать ошибки
    })

@app.post("/update_password", response_class=HTMLResponse)
async def update_password(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    form = await request.form()
    old_password = form.get("old_password")
    new_password = form.get("new_password")
    confirm_password = form.get("confirm_password")
    errors = {}  # Словарь для хранения ошибок

    # Проверка старого пароля
    if not verify_password(old_password, current_user.hashed_password):
        errors["old_password"] = "Неверный старый пароль"
    
    # Проверка совпадения нового пароля и подтверждения пароля
    if new_password != confirm_password:
        errors["confirm_password"] = "Новый пароль и подтверждение не совпадают"
    
    # Если есть ошибки, возвращаем форму с сообщениями об ошибках
    if errors:
        return templates.TemplateResponse("update_password.html", {"request": request, "current_user": current_user, "errors": errors})
    
    # Хеширование нового пароля
    hashed_password = get_password_hash(new_password)
    
    # Обновление пароля в базе данных
    crud.update_user_password(db, current_user.id, hashed_password)
    
    # Перенаправление на главную страницу
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/search", response_class=HTMLResponse)
async def search_tasks_page(request: Request, query: str = Query(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return templates.TemplateResponse("search.html", {"request": request, "current_user": current_user})
    else:
        near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
        if query:
            tasks = crud.search_tasks(db, user_id=current_user.id, query=query)
        else:
            tasks = []
        return templates.TemplateResponse("search.html", {"request": request, "tasks": tasks, "query": query, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return templates.TemplateResponse("tasks.html", {"request": request, "current_user": current_user})
    else:
        tasks = crud.get_tasks(db, user_id=current_user.id)
        # Сортировка задач по приоритету
        tasks.sort(key=lambda task: {"низкий": 3, "средний": 2, "высокий": 1}[task.priority])
        near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

@app.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    return templates.TemplateResponse("create_task.html", {"request": request, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

@app.post("/tasks/create", response_class=HTMLResponse)
async def create_task(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    form = await request.form()
    
    if not form.get("deadline"):
        deadline = None
    else:
        deadline = form.get("deadline")
        
    task = schemas.TaskCreate(
        title=form.get("title"),
        description=form.get("description"),
        status=form.get("status"),
        priority=form.get("priority"),
        deadline=deadline
    )
    crud.create_task(db, task, user_id=current_user.id)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(request: Request, task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id=task_id)
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

@app.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    form = await request.form()
    task = schemas.TaskCreate(
        title=form.get("title"),
        description=form.get("description"),
        status=form.get("status"),
        priority=form.get("priority"),
        deadline=form.get("deadline")
    )

    existing_task = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this task")
    
    crud.update_task(db, task_id, task)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
async def delete_task(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    existing_task = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this task")
    
    crud.delete_task(db, task_id)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_page(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this task")
    return templates.TemplateResponse("task.html", {"request": request, "task": task, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

