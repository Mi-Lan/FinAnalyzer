# 1. Installer Stage
FROM node:20-slim AS deps
WORKDIR /app

# Install pnpm using corepack
RUN corepack enable && corepack prepare pnpm@10.2.0 --activate

# Copy dependency definition files
COPY package.json pnpm-lock.yaml ./
# Copy workspace config
COPY pnpm-workspace.yaml ./

# Copy package.json from workspaces
COPY apps/web/package.json ./apps/web/
COPY packages/database/package.json ./packages/database/

# Install all dependencies
RUN pnpm install --frozen-lockfile --prod=false

# 2. Builder Stage
FROM node:20-slim AS builder
WORKDIR /app

# Install pnpm using corepack
RUN corepack enable && corepack prepare pnpm@10.2.0 --activate

# Copy installed dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=deps /app/packages/database/node_modules ./packages/database/node_modules

# Copy source code
COPY . .

# Build the web application
RUN pnpm --filter web build

# 3. Runner Stage
FROM node:20-slim AS runner
WORKDIR /app

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy standalone output
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME 0.0.0.0

CMD ["node", "apps/web/server.js"] 