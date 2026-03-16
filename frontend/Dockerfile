# syntax=docker/dockerfile:1
# Multi-stage Dockerfile для VeritasAd Frontend — оптимизированная сборка

# ==================== BASE ====================
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# NEXT_PUBLIC_* переменные встраиваются в бандл при сборке — передавать через build args
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_DISABLE_AUTH=false
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_DISABLE_AUTH=$NEXT_PUBLIC_DISABLE_AUTH

# Копируем только файлы зависимостей для кэширования (слой кэшируется при изменении кода)
COPY package.json package-lock.json ./

# Устанавливаем зависимости с кэшированием
RUN npm ci --frozen-lockfile && \
    npm cache clean --force

# ==================== BUILDER ====================
FROM base AS builder
WORKDIR /app

# Копируем node_modules из deps (кэшированный слой)
COPY --from=deps /app/node_modules ./node_modules

# Копируем исходный код (исключая .dockerignore)
COPY . .

# Создаём public directory (если отсутствует)
RUN mkdir -p public

# Переменные для сборки (объявляем повторно для этой стадии)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_DISABLE_AUTH=false
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_DISABLE_AUTH=$NEXT_PUBLIC_DISABLE_AUTH

# Отключаем телеметрию Next.js
ENV NEXT_TELEMETRY_DISABLED=1

# Собираем проект
RUN npm run build

# ==================== RUNNER ====================
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Создаём non-root пользователя
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Копируем public из builder
COPY --from=builder /app/public ./public

# Копируем standalone output из .next/standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Копируем статические файлы
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Переключаемся на non-root пользователя
USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
