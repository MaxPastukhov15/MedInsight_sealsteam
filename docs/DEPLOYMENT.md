# Deployment Guide

## Локальная разработка

### Использование Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend

# Остановить
docker-compose down
```

## Production Deployment

### Backend (Railway)

1. **Создать проект на Railway**
   - Перейти на [railway.app](https://railway.app)
   - Создать новый проект
   - Подключить GitHub репозиторий

2. **Добавить сервисы**
   - PostgreSQL
   - Redis
   - Backend (Python)

3. **Настроить Environment Variables**
   ```
   DATABASE_URL=<provided-by-railway>
   REDIS_URL=<provided-by-railway>
   LLM_PROVIDER=ollama
   ENVIRONMENT=production
   DEBUG=False
   ```

4. **Deploy**
   - Railway автоматически соберёт и задеплоит backend

### Frontend (Vercel)

1. **Импортировать проект**
   - Перейти на [vercel.com](https://vercel.com)
   - Import Git Repository
   - Выбрать `frontend/` как root directory

2. **Настроить Environment Variables**
   ```
   VITE_API_BASE_URL=https://your-backend.railway.app
   ```

3. **Deploy**
   - Vercel автоматически соберёт и задеплоит

## CI/CD

GitHub Actions автоматически:
- Запускает тесты на каждый push
- Проверяет качество кода
- Deploy на merge в main

См. `.github/workflows/test.yml` и `.github/workflows/deploy.yml`
