# DRF Academy

## Локальный запуск

### Через Docker Compose

1. Скопируйте шаблон окружения:

```bash
cp .env.example .env
```

Для PowerShell:

```powershell
Copy-Item .env.example .env
```

2. Запустите проект:

```bash
docker compose up --build
```

3. Приложение будет доступно на `http://localhost:8001`.

4. Остановка проекта:

```bash
docker compose down
```

## Переменные окружения

Шаблон лежит в `.env.example`.

Основные переменные:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_URL`
- `STRIPE_API_KEY`
- `EMAIL_HOST`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `DEFAULT_FROM_EMAIL`

Файл `.env` не должен попадать в репозиторий. Для сервера создайте отдельный production-вариант с реальными значениями.

## Настройка удаленного сервера

Ниже пример для Ubuntu.

### 1. Установка пакетов

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx git
```

Если Gunicorn еще не ставится через проект, его можно установить в серверное окружение после деплоя или добавить в зависимости проекта.

### 2. Создание пользователя и каталога приложения

```bash
sudo mkdir -p /home/user/app
sudo chown -R user:user /home/user/app
```

### 3. Настройка `.env` на сервере

Создайте файл `/home/user/app/.env` и заполните его production-значениями.

Минимальный пример:

```env
DEBUG=False
SECRET_KEY=change-me
ALLOWED_HOSTS=84.252.136.209,localhost,127.0.0.1
DB_ENGINE=sqlite
REDIS_URL=redis://localhost:6379/0
STRIPE_API_KEY=
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=webmaster@localhost
```

Если используется PostgreSQL, задайте:

```env
DB_ENGINE=postgres
DB_NAME=academy
DB_USER=academy
DB_PASSWORD=secret
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 4. Systemd для Gunicorn

Пример unit-файла `/etc/systemd/system/drf-academy.service`:

```ini
[Unit]
Description=DRF Academy Gunicorn
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/app
EnvironmentFile=/home/user/app/.env
ExecStart=/home/user/app/venv/bin/python -m gunicorn config.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Применение:

```bash
sudo systemctl daemon-reload
sudo systemctl enable drf-academy.service
sudo systemctl start drf-academy.service
sudo systemctl status drf-academy.service
```

### 5. Nginx

Пример конфига `/etc/nginx/sites-available/drf-academy`:

```nginx
server {
    listen 80;
    server_name 84.252.136.209;

    location /static/ {
        alias /home/user/app/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/drf-academy /etc/nginx/sites-enabled/drf-academy
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Безопасность

- используйте вход только по SSH-ключам;
- отключите парольный вход при необходимости;
- откройте только нужные порты, обычно `22`, `80`, `443`;
- приложение не должно слушать внешний интерфейс напрямую, Gunicorn лучше держать на `127.0.0.1`.

Пример с `ufw`:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## GitHub Actions

Workflow лежит в `.github/workflows/ci.yml`.

Что делает workflow:

1. запускается на каждый `push` и `pull_request`;
2. поднимает Python `3.13`;
3. ставит зависимости через Poetry;
4. применяет миграции;
5. запускает тесты;
6. если тесты успешны и был `push` в `main` или `master`, запускает деплой на сервер.

Ошибки тестов останавливают деплой, потому что job `deploy` зависит от job `test` через `needs: test`.

## Secrets GitHub

Для деплоя в GitHub repository secrets должны быть заданы:

- `SSH_KEY` - приватный SSH-ключ
- `SSH_USER` - пользователь сервера
- `SERVER_IP` - IP сервера
- `DEPLOY_DIR` - каталог проекта на сервере, например `/home/user/app`
- `APP_SERVICE` - имя systemd-сервиса, например `drf-academy.service`

## Как работает деплой

При успешном `push` в основную ветку workflow:

1. подключается к серверу по SSH;
2. копирует код через `rsync`;
3. создает `venv`, если его еще нет;
4. ставит зависимости через Poetry;
5. применяет миграции;
6. выполняет `collectstatic`;
7. перезапускает systemd-сервис приложения.

## Что проверить перед сдачей

1. Убедиться, что приложение открывается по IP сервера или домену.
2. Убедиться, что `sudo systemctl status drf-academy.service` показывает активный сервис.
3. Проверить прохождение workflow в GitHub Actions.
4. Проверить, что в git не попали `.env`, `.idea`, `.venv`, `__pycache__`.
5. Создать ветку домашней работы и открыть pull request в `develop`.

## Сдача задания

Для сдачи нужен pull request из вашей рабочей ветки в `develop`.

Перед отправкой полезно проверить:

```bash
git status
git diff
```

И убедиться, что в PR входят:

- `.github/workflows/ci.yml`
- обновленный `README.md`
- `.env.example`
- связанные изменения для деплоя
