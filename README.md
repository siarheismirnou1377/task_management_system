# Task Management System

Этот проект представляет собой систему управления задачами (Task Management System), разработанную с использованием FastAPI. Он позволяет пользователям регистрироваться, создавать задачи, управлять ими (редактировать, удалять) и отслеживать сроки выполнения. Проект также включает интеграцию с базой данных PostgreSQL, аутентификацию пользователей и возможность поиска задач.

## Структура проекта

Проект организован следующим образом:
```
task_management_system/
│
├── app/
│   ├── configs/
│   │   ├── config.env
│   │   └── configs.py
│   ├── static/
│   │   ├── scripts.js
│   │   └── styles.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── create_task.html
│   │   ├── edit_task.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── search.html
│   │   ├── task.html
│   │   └── tasks.html
│   ├── __init__.py
│   ├── api.py
│   ├── auth.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```
## Установка и запуск

### Предварительные требования

1. Убедитесь, что у вас установлены Docker и Docker Compose.
2. Убедитесь, что у вас установлен Python 3.12.3 или выше.

### Шаги для запуска

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/siarheismirnou1377/task_management_system.git
   cd task_management_system
   ```

2. **Настройте переменные окружения:**

   В `config.env` и настройте переменные окружения:

   Пример содержимого `config.env`:

   ```env
   APP_HOST=0.0.0.0
   APP_PORT=8080
   DB_LOGIN=login
   DB_PASSWORD=password
   DB_NAME=task_management_system
   DB_HOST=db
   DB_HOST_PORT=5433
   ```

3. **Соберите и запустите контейнеры с помощью Docker Compose:**

   ```bash
   sudo docker-compose --env-file app/configs/config.env up --build
   ```
   -чтобы перезапустить контейнер если вы его завершли, можете спользовать команду:
   ```bash
   sudo docker-compose --env-file app/configs/config.env up -d
   ```
4. **Доступ к приложению:**

   После успешного запуска, приложение будет доступно по адресу:

   ```url
   http://localhost:8080
   ```

## Основные функции

### Аутентификация

- **Регистрация пользователя:** Пользователи могут зарегистрироваться, указав имя пользователя и пароль.
- **Вход в систему:** Пользователи могут войти в систему с помощью имени пользователя и пароля.
- **Выход из системы:** Пользователи могут выйти из системы, чтобы завершить сессию.

### Управление задачами

- **Создание задачи:** Пользователи могут создавать новые задачи, указывая заголовок, описание, статус, приоритет и срок выполнения.
- **Редактирование задачи:** Пользователи могут редактировать существующие задачи.
- **Удаление задачи:** Пользователи могут удалять задачи.
- **Просмотр задач:** Пользователи могут просматривать список своих задач.

### Поиск задач

- **Поиск по заголовку:** Пользователи могут искать задачи по заголовку с использованием алгоритма Левенштейна.

### Уведомления

- **Уведомления о приближающихся сроках:** Пользователи получают уведомления о задачах, у которых срок выполнения истекает в течение суток.

## API

Проект также предоставляет API для управления задачами. Основные маршруты API:

- **GET `/api/tasks`**: Получить список задач текущего пользователя.
- **POST `/api/tasks`**: Создать новую задачу.
- **PUT `/api/tasks/{task_id}`**: Обновить задачу по её идентификатору.
- **DELETE `/api/tasks/{task_id}`**: Удалить задачу по её идентификатору.

## Технологии

- **FastAPI**: Веб-фреймворк для создания API.
- **PostgreSQL**: Реляционная база данных для хранения данных.
- **SQLAlchemy**: ORM для работы с базой данных.
- **Jinja2**: Шаблонизатор для генерации HTML.
- **Docker**: Контейнеризация приложения.
- **bcrypt**: Хэширование паролей.

## Лицензия

Этот проект лицензирован под MIT License. Подробности смотрите в файле [LICENSE](LICENSE).
