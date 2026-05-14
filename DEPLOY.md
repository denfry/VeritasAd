# VeritasAd — Деплой фронтенда на Vercel (Demo-режим)

Быстрый старт для деплоя **только фронтенда** на Vercel без бэкенда. Все страницы доступны без авторизации (mock-режим).

---

## 1. Подготовка

Убедись, что у тебя установлен Vercel CLI (опционально):

```bash
npm i -g vercel
```

## 2. Настройка окружения

Файл `frontend/.env.production` уже содержит базовые настройки для демо:

```
NEXT_PUBLIC_DISABLE_AUTH=true
```

Это автоматически:
- Отключает проверку авторизации в middleware
- Создаёт mock-пользователя в AuthContext
- Делает все страницы (даже `/admin`) доступными без входа

## 3. Деплой через Vercel Dashboard (рекомендуется)

1. Зайди на [vercel.com](https://vercel.com) и импортируй репозиторий
2. В настройках проекта укажи:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
3. Добавь Environment Variables (если нужно):
   - `NEXT_PUBLIC_API_URL` — URL бэкенда (если появится позже)
   - `NEXT_PUBLIC_APP_URL` — URL фронтенда (например `https://your-project.vercel.app`)
   - `NEXT_PUBLIC_DISABLE_AUTH=true`
4. Нажми **Deploy**

## 4. Деплой через CLI

```bash
cd frontend
vercel --prod
```

При первом запуске CLI задаст вопросы:
- Link to existing project? — `N` (создать новый)
- Project name — `veritasad-frontend` (или свой)
- Directory — `frontend/`

## 5. Демо-режим без бэкенда

В текущей конфигурации:
- ✅ Все страницы открываются без авторизации
- ✅ UI полностью виден и интерактивен
- ❌ API-запросы (анализ видео, история, оплата) будут падать с ошибками — это нормально для демо
- ❌ WebSocket/SSE прогресса не работают без бэкенда

Чтобы подключить бэкенд позже:
1. Задеплой бэкенд отдельно (Railway, Render, VPS)
2. В настройках Vercel обнови `NEXT_PUBLIC_API_URL` на URL бэкенда
3. Пересобери проект (Vercel сделает это автоматически при пуше)

## 6. Полезные команды

```bash
# Предпросмотр (preview deploy)
cd frontend && vercel

# Локальная проверка production-сборки
cd frontend && npm run build && npm start

# Логи
vercel logs --all
```

## 7. Кастомный домен (опционально)

В настройках проекта на Vercel:
- **Domains** → Add custom domain
- Следуй инструкциям для DNS
- Обнови `NEXT_PUBLIC_APP_URL` в env vars

---

## Что уже настроено

- `vercel.json` — указан framework Next.js
- `.env.production` — отключена авторизация
- `middleware.ts` — пропускает все запросы при `DISABLE_AUTH=true`
- `auth-context.tsx` — создаёт mock-пользователя для демо
