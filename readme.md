# TeamFinder

Платформа для поиска команды и совместной работы над pet-проектами. Разработчики, дизайнеры и другие специалисты могут публиковать свои идеи, находить единомышленников и присоединяться к уже существующим проектам.

## Функциональность

- Регистрация и аутентификация пользователей
- Создание, редактирование и завершение проектов
- Участие в проектах других пользователей
- Фильтрация проектов по навыкам
- Управление навыками на странице проекта
- Редактирование профиля (аватар, контактные данные, описание)
- Смена пароля

## Стек технологий

- **Python** 3.10
- **Django** 5.2
- **PostgreSQL** 16
- **Docker** и **Docker Compose**
- **Pillow** 10.1+ (генерация аватарок)
- **python-decouple** (переменные окружения)

## Установка и запуск

### Требования

- Docker и Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd team-finder-ad
```

### 2. Переменные окружения

Скопируйте пример и при необходимости отредактируйте значения:

```bash
cp .env_example .env
```

Минимальный набор переменных в `.env`:

```env
DJANGO_SECRET_KEY=change_for_safety
DJANGO_DEBUG=True

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=db
POSTGRES_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=False
```

### 3. Что дальше?

После клонирования, перехода в каталог проекта и создания `.env` выполните:

```bash
docker compose up --build
```

В другом терминале (пока контейнеры запущены) примените миграции:

```bash
docker compose exec web python manage.py migrate
```

При необходимости создайте суперпользователя для входа в админ панель:

```bash
docker compose exec web python manage.py createsuperuser
```

Откройте в браузере:

- приложение: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- админ панель: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Остановить контейнеры:

```bash
docker compose down
```

## Автор

Максим Тикшаев
GitHub: https://github.com/vrqnv
Email: tikshaev.ycheba@gmail.com
