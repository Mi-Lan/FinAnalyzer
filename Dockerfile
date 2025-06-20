# Base image for installing dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm fetch

# Base image for building the application
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm install -g pnpm && pnpm install -w --prod && pnpm run build

# Final image for running the application
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/apps/next-app/.next ./apps/next-app/.next
COPY --from=builder /app/node_modules ./node_modules

# This is a placeholder command. Each service will override this.
CMD ["node"] 