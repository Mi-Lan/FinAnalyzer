# Base image for installing dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
# Copy lock file if it exists
COPY pnpm-loc[k].yaml* ./
RUN npm install -g pnpm || echo "pnpm install skipped"

# Base image for building the application
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/ ./
COPY . .
RUN npm install -g pnpm || echo "pnpm install skipped"

# Final image for running the application
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/package.json ./package.json
# Copy any built assets (placeholder for now)
COPY --from=builder /app/scripts ./scripts

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

# This is a placeholder command. Each service will override this.
CMD ["node", "--version"] 