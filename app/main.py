from datetime import datetime
import re
from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine
from .auth import verify_password, get_password_hash
from .api import api_router
from app.dependencies import get_current_user, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router, prefix="/api", tags=["tasks"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    errors = {}

    if not current_user:
        errors["auth"] = "Вы не авторизованы. Пожалуйста, войдите или зарегистрируйтесь."

    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id) if current_user else []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks,
        "errors": errors
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "errors": {}})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    errors = {}

    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        errors["login"] = "Неверное имя пользователя или пароль"

    if not username:
        errors["username"] = "Имя пользователя не может быть пустым"
    if not password:
        errors["password"] = "Пароль не может быть пустым"

    if errors:
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})

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
    errors = {}

    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        errors["username"] = "Имя пользователя уже занято"

    if not username:
        errors["username"] = "Имя пользователя не может быть пустым"
    elif not re.match(r"^[a-zA-Z0-9_-]{1,8}$", username):
        errors["username"] = "Логин должен содержать только буквы, цифры, дефисы и подчеркивания, не более 8 символов"

    if not password:
        errors["password"] = "Пароль не может быть пустым"
    elif len(password) < 4:
        errors["password"] = "Пароль должен быть не менее 4 символов"


    if errors:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

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
        "errors": {}
    })

@app.post("/update_password", response_class=HTMLResponse)
async def update_password(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    form = await request.form()
    old_password = form.get("old_password")
    new_password = form.get("new_password")
    confirm_password = form.get("confirm_password")
    errors = {}

    if not verify_password(old_password, current_user.hashed_password):
        errors["old_password"] = "Неверный старый пароль"
    
    if new_password != confirm_password:
        errors["confirm_password"] = "Новый пароль и подтверждение не совпадают"
    
    if errors:
        return templates.TemplateResponse("update_password.html", {"request": request, "current_user": current_user, "errors": errors})

    hashed_password = get_password_hash(new_password)
    
    crud.update_user_password(db, current_user.id, hashed_password)
    
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/search", response_class=HTMLResponse)
async def search_tasks_page(request: Request, query: str = Query(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    errors = {}

    if not current_user:
        errors["auth"] = "Вы не авторизованы. Пожалуйста, войдите или зарегистрируйтесь."
        return templates.TemplateResponse("search.html", {
            "request": request,
            "current_user": current_user,
            "errors": errors
        })

    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)

    if query:
        tasks = crud.search_tasks(db, user_id=current_user.id, query=query)
    else:
        tasks = []

    if not tasks and query:
        errors["search"] = "По вашему запросу ничего не найдено."

    return templates.TemplateResponse("search.html", {
        "request": request,
        "tasks": tasks,
        "query": query,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks,
        "errors": errors
    })

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return templates.TemplateResponse("tasks.html", {"request": request, "current_user": current_user})
    else:
        tasks = crud.get_tasks(db, user_id=current_user.id)

        tasks.sort(key=lambda task: {"низкий": 3, "средний": 2, "высокий": 1}[task.priority])
        near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "current_user": current_user, "near_deadline_tasks": near_deadline_tasks})

@app.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id)
    return templates.TemplateResponse("create_task.html", {
        "request": request,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks,
        "errors": {}
    })

@app.post("/tasks/create", response_class=HTMLResponse)
async def create_task(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    form = await request.form()
    errors = {}

    if not form.get("title"):
        errors["title"] = "Заголовок не может быть пустым"
    if not form.get("description"):
        errors["description"] = "Описание не может быть пустым"

    if len(form.get("title")) > 13:
        errors["title"] = "Заголовок должен быть не длиннее 13 символов"

    if len(form.get("description")) > 200:
        errors["description"] = "Описание должно быть не длиннее 200 символов"

    if errors:
        return templates.TemplateResponse("create_task.html", {
            "request": request,
            "current_user": current_user,
            "errors": errors
        })

    deadline = form.get("deadline") if form.get("deadline") else None
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
    return templates.TemplateResponse("edit_task.html", {
        "request": request,
        "task": task,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks,
        "errors": {}
    })

@app.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    form = await request.form()
    errors = {}

    if not form.get("title"):
        errors["title"] = "Заголовок не может быть пустым"
    if not form.get("description"):
        errors["description"] = "Описание не может быть пустым"
    
    if len(form.get("title")) > 13:
        errors["title"] = "Заголовок должен быть не длиннее 13 символов"

    if len(form.get("description")) > 200:
        errors["description"] = "Описание должно быть не длиннее 200 символов"

    existing_task = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        errors["permission"] = "У вас нет разрешения на редактирование этой задачи"

    if errors:
        return templates.TemplateResponse("edit_task.html", {
            "request": request,
            "task": existing_task,
            "current_user": current_user,
            "errors": errors
        })

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
async def delete_task(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    errors = {}

    existing_task = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        errors["permission"] = "У вас нет разрешения на удаление этой задачи"

    if errors:
        return templates.TemplateResponse("task.html", {"request": request, "task": existing_task, "current_user": current_user, "errors": errors})

    crud.delete_task(db, task_id)
    return RedirectResponse(url="/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_page(request: Request, task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    errors = {}

    # Проверка авторизации пользователя
    if current_user is None:
        errors["auth"] = "Вы не авторизованы. Пожалуйста, войдите или зарегистрируйтесь."
        return templates.TemplateResponse("task.html", {
            "request": request,
            "current_user": current_user,
            "errors": errors
        })

    # Получение задачи
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        errors["task"] = "Задача не найдена"
    elif task.owner_id != current_user.id:
        errors["permission"] = "У вас нет разрешения на просмотр этой задачи"

    near_deadline_tasks = crud.get_tasks_with_near_deadline(db, user_id=current_user.id) if current_user else []

    if errors:
        return templates.TemplateResponse("task.html", {
            "request": request,
            "current_user": current_user,
            "near_deadline_tasks": near_deadline_tasks,
            "errors": errors
        })

    return templates.TemplateResponse("task.html", {
        "request": request,
        "task": task,
        "current_user": current_user,
        "near_deadline_tasks": near_deadline_tasks
    })
