# syntax=docker/dockerfile:1.7

# ── Stage 1: deps ─────────────────────────────────────────────────────────────
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ── Stage 2: build ────────────────────────────────────────────────────────────
FROM node:22-alpine AS build
WORKDIR /app

# NEXT_PUBLIC_* env vars are inlined at build time — pass via --build-arg.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ── Stage 3: runtime ──────────────────────────────────────────────────────────
FROM node:22-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000

# Copy the built app + only prod-runtime deps. With a standard `next build`
# (no `output: "standalone"`) we ship node_modules.
COPY --from=build /app/package.json /app/package-lock.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/next.config.ts ./

RUN addgroup -g 1001 -S nodejs \
 && adduser -S nextjs -u 1001 \
 && chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=3s --retries=10 \
    CMD wget -qO- http://127.0.0.1:3000/ > /dev/null || exit 1

CMD ["npm", "run", "start", "--", "--port", "3000", "--hostname", "0.0.0.0"]
