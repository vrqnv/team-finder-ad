# TeamFinder

## Запуск проекта

1. Клонируйте репозиторий и перейдите в папку проекта.

2. Создайте файл .env со следующим содержимым:
   DJANGO_SECRET_KEY=change_for_safety
   DJANGO_DEBUG=True
   TASK_VERSION=3

3. Запустите контейнеры командой: docker-compose up --build

4. В отдельном терминале выполните миграции: docker exec -it team-finder-ad-web-1 python manage.py migrate

5. Создайте суперпользователя: docker exec -it team-finder-ad-web-1 python manage.py createsuperuser

6. Откройте в браузере: http://localhost:8000/projects/list/

7. Для остановки проекта выполните: docker-compose down