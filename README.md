# FinAnalyzer - Financial Analysis Platform

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Task Master](https://img.shields.io/badge/Built%20with-Task%20Master-blue.svg)](https://github.com/eyaltoledano/claude-task-master)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![Turborepo](https://img.shields.io/badge/Turborepo-Enabled-blue)](https://turbo.build/repo)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com/)

An AI-powered platform for automated financial data analysis and scoring built with modern monorepo architecture and optimized for production deployment.

## Project Status

✅ Production-ready infrastructure with Turborepo and Docker optimization

## Development Progress

**Overall Progress: 5/18 tasks completed (28%)**

| ID | Task | Status | Priority | Dependencies |
|:---|:-----|:-------|:---------|:-------------|
| 1 | Setup Project Repository & CI/CD Pipeline | ✅ done | high | none |
| 2 | Design and Deploy PostgreSQL Schema | ✅ done | high | none |
| 3 | Implement Data Ingestion Adapter for FMP API | ✅ done | high | 1 |
| 4 | Scaffold Next.js Frontend with Mock Data | ✅ done | medium | 1 |
| 5 | Build FastAPI Gateway for FE/BE Communication | ✅ done | medium | 1, 2 |
| 6 | Implement Real-Time Data Pull and Storage | ⏳ pending | high | 2, 3 |
| 7 | Develop Hard-Coded Prompt Chain for Single Temp... | ⏳ pending | medium | 2, 3 |
| 8 | Build Scoring Module with Pydantic Validation | ⏳ pending | medium | 2, 7 |
| 9 | Display Scores & Insights in UI | ⏳ pending | medium | 4, 5, 8 |
| 10 | Add Caching for Repeat Requests | ⏳ pending | medium | 3, 6 |
| 11 | Develop JSON-Based Template Engine | ⏳ pending | medium | 2, 7 |
| 12 | Implement Responsive Layout & Filtering | ⏳ pending | medium | 4, 9 |
| 13 | Integrate Recharts for Data Visualization | ⏳ pending | medium | 4, 9 |
| 14 | Enable Report Export to PDF/CSV | ⏳ pending | medium | 9, 12 |
| 15 | Implement Bulk Screening Workflow | ⏳ pending | medium | 2, 6, 11 |
| 16 | Add Auth & Multi-Tenant Support | ⏳ pending | medium | 2, 5 |
| 17 | Implement Embeddings Store with pgvector | ⏳ pending | low | 2, 10 |
| 18 | Deploy Microservices with Kubernetes/ECS | ⏳ pending | medium | 1, 5 |


## Built with Task Master

This project uses [Task Master](https://github.com/eyaltoledano/claude-task-master) for structured development - an AI-powered project management system that breaks down complex projects into manageable tasks.

### Task Master Implementation

- **18 main tasks** broken into **101 detailed subtasks**
- AI-assisted task breakdown and complexity analysis
- Clear dependency management and execution order
- Real-time progress tracking with status updates
- Iterative development workflow

### Progress Automation Rules

To keep the progress table updated automatically:

1. **After completing any task or subtask:**

   ```bash
   # Update task status
   task-master set-status --id=<task-id> --status=done

   # Automatically update README progress table
   npm run update-progress
   ```

2. **Commit progress updates:**

   ```bash
   git add README.md .taskmaster/tasks/tasks.json
   git commit -m "progress: Complete task <id> - <task-title>"
   ```

3. **Automated script features:**

   - Reads live data from `.taskmaster/tasks/tasks.json`
   - Updates progress percentage and completion stats
   - Maintains proper status icons and formatting
   - Preserves all other README content

4. **Weekly progress sync:**
   - Review dependency blockers
   - Plan next iteration focus
   - Check for outdated task descriptions

---

## What This Does

A platform that automates financial analysis from data ingestion to scoring, designed to handle large-scale analysis efficiently with enterprise-grade infrastructure.

### Core Features

**1. Automated Data Ingestion & Storage**

- Python-based data adapter with FMP API integration.
- **Persistent Storage**: Asynchronously fetches and stores financial data in a PostgreSQL database, performing an "upsert" to merge new data with existing records for a complete, consolidated view.
- **High-Throughput Processing**: Includes an `AsyncProcessor` to handle concurrent data ingestion and retrieval for multiple stock tickers.
- Pydantic validation and an enhanced parser for robust data cleaning, validation, and error recovery.
- Rate limiting and transport abstraction with Redis caching.
- Configurable data sources and normalization.

**2. Modern Frontend Architecture**

- Next.js 15 with React 19 for cutting-edge performance
- Tailwind CSS with shadcn/ui component library
- TanStack Query for efficient data fetching
- TypeScript with strict type checking

**3. Prompt-Chain Scoring Engine**

- Uses LangChain and AI models for financial analysis
- Configurable prompt chains for different analysis types
- Consistent scoring across large datasets

**4. Enterprise Monorepo Structure**

- Turborepo for optimized build caching (20x speed improvements)
- Shared TypeScript configuration and path aliases
- Cross-package dependency management
- Parallel task execution with intelligent caching

**5. Production-Ready Infrastructure**

- Multi-stage Docker builds with optimized caching
- PostgreSQL database with Prisma ORM
- Comprehensive CI/CD with quality gates
- Hot reloading and development optimization

---

## Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js 15 App]
        A1[React 19 Components]
        A2[TanStack Query]
        A3[Tailwind + shadcn/ui]
    end

    subgraph "Backend Layer"
        B[FastAPI Gateway]
        B1[Data Adapter Layer]
        B2[LangChain AI Engine]
    end

    subgraph "Data Layer"
        C[PostgreSQL + Prisma]
        D[Redis Cache]
        F[Financial APIs]
    end

    subgraph "Infrastructure"
        E[Docker Containers]
        G[Turborepo Build System]
        H[GitHub Actions CI/CD]
    end

    A --> B
    B --> C
    B --> D
    B1 --> F
    B --> B2
    E -.-> A
    E -.-> B
    E -.-> C
    G -.-> A
    G -.-> B1
    H --> G
```

### Tech Stack

**Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query  
**Backend**: FastAPI, Python, Pydantic, LangChain  
**Database**: PostgreSQL, Prisma ORM, Redis  
**Data Layer**: Python data adapter, FMP API integration  
**Infrastructure**: Docker, Turborepo, pnpm workspaces, GitHub Actions  
**Development**: Node.js 20+, pnpm 10.2+, TypeScript 5.8+

---

## Monorepo Structure

```
FinAnalyzer/
├── apps/
│   └── web/                 # Next.js 15 frontend application
│       ├── src/
│       │   ├── app/         # App Router (Next.js 15)
│       │   ├── components/  # React components with shadcn/ui
│       │   ├── lib/         # Utilities and hooks
│       │   └── types/       # TypeScript definitions
│       ├── public/          # Static assets
│       └── next.config.ts   # Next.js configuration
├── packages/
│   ├── api-gateway/         # FastAPI gateway for frontend
│   │   ├── src/api_gateway/ # Python package source
│   │   │   ├── main.py      # FastAPI application
│   │   │   └── security.py  # API key authentication
│   │   └── pyproject.toml   # Python package configuration
│   ├── database/            # Prisma database package
│   │   ├── prisma/          # Database schema and migrations
│   │   ├── index.ts         # Prisma client exports
│   │   └── package.json     # Database package config
│   └── data-adapter/        # Python data ingestion layer
│       ├── src/data_adapter/# Python package source
│       │   ├── providers/   # API provider implementations
│       │   ├── async_processor.py # High-throughput data processing
│       │   ├── database.py  # Asynchronous DB manager
│       │   ├── factory.py   # Provider factory pattern
│       │   └── models.py    # SQLAlchemy data models
│       └── pyproject.toml   # Python package configuration
├── turbo.json              # Turborepo pipeline configuration
├── tsconfig.base.json      # Shared TypeScript configuration
├── docker-compose.yml      # Complete development stack
├── Dockerfile             # Optimized multi-stage build
└── pnpm-workspace.yaml    # pnpm workspace configuration
```

---

## Setup

### Prerequisites

- **Node.js 20.11.0+** (Required for React 19 and modern features)
- **Docker & Docker Compose** (For containerized development)
- **pnpm 10.2+** (For workspace management and caching)

### Quick Start

The entire development environment is containerized and optimized. Get started in seconds:

```bash
# Clone the repository
git clone https://github.com/Mi-Lan/FinAnalyzer.git
cd FinAnalyzer

# Build and start all services (web app, database, etc.)
docker-compose up --build
```

The web application will be available at `http://localhost:3000`.

### Local Development & Testing

For reliable local development and testing, follow these comprehensive steps:

#### 1. Environment Setup

```bash
# Ensure you have the correct Node.js version
node --version  # Should be 20.11.0 or higher

# Verify pnpm version
pnpm --version  # Should be 10.2.0 or higher

# If using older versions, update:
nvm install 20.11.0 && nvm use 20.11.0
npm install -g pnpm@10.2.0
```

#### 2. Repository Setup

```bash
# Clone and enter the repository
git clone https://github.com/Mi-Lan/FinAnalyzer.git
cd FinAnalyzer

# Install all dependencies (uses Turborepo for optimization)
pnpm install
```

#### 3. Database Setup

```bash
# Start PostgreSQL database only
docker-compose up -d postgres

# Verify database is running
docker-compose ps

# Generate Prisma client and run migrations
cd packages/database
pnpm db:generate
pnpm db:migrate
cd ../..
```

#### 4. Environment Configuration

```bash
# Copy environment template (if available)
cp .env.example .env

# Or create .env file with required variables:
cat > .env << EOF
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/findb"

# Optional: Financial data API keys
FMP_API_KEY="your_fmp_api_key_here"

# Development settings
NODE_ENV=development
NEXT_PUBLIC_API_URL="http://localhost:3000"
EOF
```

#### 5. Build and Validate

```bash
# Build all packages (tests Turborepo integration)
pnpm build

# Run quality checks
pnpm lint
pnpm type-check

# Verify everything compiled successfully
echo "✅ Build completed successfully"
```

#### 6. Start Development Servers

```bash
# Option A: Start all services with Docker (recommended)
docker-compose up --build

# Option B: Start services individually for development
# Terminal 1: Database (if not already running)
docker-compose up -d postgres

# Terminal 2: Web application
cd apps/web
pnpm dev

# Terminal 3: (Future) API server
# cd apps/api && pnpm dev
```

#### 7. Verify Local Setup

```bash
# Test web application
curl http://localhost:3000
# Should return HTML content

# Test database connection
cd packages/database
pnpm db:studio
# Opens Prisma Studio at http://localhost:5555

# Test Turborepo caching
pnpm lint  # First run
pnpm lint  # Second run should be much faster (cached)
```

#### 8. Testing Commands

```bash
# Run all tests across the monorepo
pnpm test

# Test specific packages
cd apps/web && pnpm test
cd packages/database && pnpm test

# Test Python data adapter
cd packages/data-adapter
pip install -e .
python -m pytest tests/ -v

# Test Docker build (without running)
docker build -t finanalyzer-test .
```

#### 9. Development Workflow Testing

```bash
# Test hot reloading
# 1. Start dev server: pnpm dev
# 2. Edit apps/web/src/app/page.tsx
# 3. Verify changes appear automatically in browser

# Test Turborepo task dependencies
pnpm turbo run build --dry-run
# Should show: database builds before web

# Test cross-package imports
# Verify @repo/database can be imported in web app
cd apps/web
pnpm type-check  # Should pass without errors
```

#### 10. Troubleshooting Common Issues

```bash
# Clear all caches and restart
pnpm clean
rm -rf node_modules */node_modules
pnpm install

# Reset database
docker-compose down -v
docker-compose up -d postgres
cd packages/database && pnpm db:migrate

# Check Docker resources
docker system df
docker system prune  # If needed

# Verify port availability
lsof -i :3000  # Web app port
lsof -i :5432  # Database port
lsof -i :5555  # Prisma Studio port
```

#### 11. Performance Verification

```bash
# Measure Turborepo cache performance
time pnpm lint  # First run (cache miss)
time pnpm lint  # Second run (cache hit, should be ~20x faster)

# Check Docker build optimization
time docker build -t test .
# Should complete in under 60 seconds with proper caching
```

#### 12. Integration Testing

```bash
# Full stack integration test
./scripts/integration-test.sh  # If available

# Manual integration verification
# 1. Start full stack: docker-compose up --build
# 2. Visit http://localhost:3000
# 3. Verify data loads correctly
# 4. Check browser network tab for API calls
# 5. Verify database contains data (Prisma Studio)
```

### Production Testing

Test the production build locally:

```bash
# Build production image
docker build -t finanalyzer-prod .

# Run production container
docker run -p 3000:3000 -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/findb" finanalyzer-prod

# Verify production build works
curl http://localhost:3000
```

### Development Workflow

This monorepo uses **[Turborepo](https://turbo.build/repo)** for optimized task execution with intelligent caching:

#### Core Commands

```bash
# Development
pnpm dev              # Start all development servers in parallel
pnpm build            # Build all packages with dependency awareness
pnpm lint             # Lint all packages (with caching)
pnpm type-check       # TypeScript validation across the monorepo
pnpm test             # Run tests across all packages

# Advanced
pnpm lint:fix         # Auto-fix linting issues
pnpm clean            # Clean all build artifacts and caches
```

#### Turborepo Performance

- **🚀 20x faster builds** with intelligent caching
- **⚡ Parallel execution** where dependencies allow
- **🎯 Only rebuild what changed** with fine-grained cache invalidation
- **📦 Cross-package dependency** awareness

Example performance improvement:

```bash
# First run:  2.047s (cache miss)
# Second run: 98ms   (cache hit) ← 2000% improvement!
```

### Package-Level Development

Work within specific packages for focused development:

```bash
# Frontend development
cd apps/web
pnpm dev                # Next.js development server
pnpm build              # Production build
pnpm type-check         # TypeScript validation

# Database management
cd packages/database
pnpm db:generate        # Generate Prisma client
pnpm db:migrate         # Run database migrations
pnpm db:studio          # Open Prisma Studio

# Data adapter (Python)
cd packages/data-adapter
pip install -e .        # Install in development mode
python -m pytest       # Run Python tests
```

### Development with Task Master

```bash
task-master next          # See next task
task-master show 1        # Get task details
task-master list          # View all tasks

# Work on tasks
task-master set-status --id=1.1 --status=in-progress
# ... implement task ...
task-master set-status --id=1.1 --status=done
```

---

## Production Deployment

### Docker Production Build

The project includes a production-optimized multi-stage Dockerfile:

```bash
# Build production image
docker build -t finanalyzer .

# Run production container
docker run -p 3000:3000 finanalyzer
```

**Docker Features:**

- **Multi-stage builds** for minimal image size
- **Turborepo integration** for optimized builds
- **Node.js 20 slim base** for security and performance
- **Non-root user** for security best practices
- **Standalone Next.js output** for optimal runtime

### CI/CD Pipeline

Automated quality gates and deployment:

- **✅ Linting** with ESLint across all packages
- **✅ Type checking** with TypeScript strict mode
- **✅ Testing** with comprehensive test suites
- **✅ Build verification** with Turborepo optimization
- **✅ Docker image building** and scanning

---

## Development Features

### TypeScript Configuration

- **Centralized configuration** with `tsconfig.base.json`
- **Path aliases** for clean imports (`@/components`, `@db/*`)
- **Strict type checking** for reliability
- **Composite projects** for incremental compilation

### Modern Next.js 15 Features

- **App Router** with advanced routing patterns
- **React 19**: Latest performance improvements
- **Server Components** and **Client Components**
- **Async route parameters** (Next.js 15 compatibility)
- **Standalone output** for Docker optimization

### Database Integration

- **Prisma ORM** with TypeScript integration
- **PostgreSQL** with full-text search capabilities
- **Database migrations** with version control
- **Connection pooling** and performance optimization

### Python Data Layer

- **Modern Python packaging** with `pyproject.toml`
- **Abstract provider pattern** for extensible data sources
- **Pydantic validation** for data integrity
- **Rate limiting** and error handling
- **FMP API integration** with comprehensive data models

---

## Development Phases

Using Task Master's structured approach:

### Phase 1: Foundation (Tasks 1-4)

- [x] Repository setup and monorepo structure
- [x] Database schema and migrations
- [x] Docker containerization
- [x] Next.js frontend with mock data

### Phase 2: Core Backend (Tasks 5-8)

- [x] FastAPI gateway and authentication
- [x] Data ingestion pipeline
- [ ] LangChain prompt chains
- [ ] Scoring module

### Phase 3: Integration (Tasks 9-12)

- [ ] Frontend-backend integration
- [ ] Authentication system
- [ ] Template management
- [ ] Bulk processing

### Phase 4: Enhancement (Tasks 13-18)

- [ ] Performance optimization
- [ ] Caching strategies
- [ ] Deployment automation
- [ ] Monitoring

---

## Performance & Optimization

### Turborepo Benefits

- **Incremental builds**: Only rebuild changed packages
- **Remote caching**: Share build cache across team
- **Parallel execution**: Run independent tasks simultaneously
- **Dependency-aware**: Respect package relationships

### Docker Optimization

- **Layer caching**: Optimize Docker build layers
- **Multi-stage builds**: Separate build and runtime
- **Minimal runtime**: Node.js slim for production
- **Security**: Non-root user and minimal attack surface

### Next.js 15 Performance

- **App Router**: Improved routing and rendering
- **React 19**: Latest performance improvements
- **Bundling optimization**: Advanced webpack configuration
- **Static generation**: Pre-built pages where possible

---

## Task Master Workflow

This project demonstrates Task Master's development methodology:

**Current Stats**: 18 main tasks, 101 subtasks, real-time tracking

**Workflow**:

1. `task-master next` - Get next available task
2. `task-master show <id>` - Review implementation details
3. `task-master expand <id>` - Break down complex tasks
4. Implement code according to task specs
5. `task-master update-subtask` - Log progress
6. `task-master set-status done` - Mark completion

**Benefits**: Clear direction, manageable complexity, visible progress, AI assistance

---

## Contributing

### For Monorepo Development

```bash
# Install dependencies
pnpm install

# Run quality checks
pnpm lint && pnpm type-check && pnpm test

# Add new packages
mkdir packages/new-package
cd packages/new-package
pnpm init

# Update Turborepo pipeline in turbo.json as needed
```

### Task Master Users

```bash
task-master list --status=pending    # See available tasks
task-master set-status --id=<id> --status=in-progress
task-master show <id>                # Get task details
```

### Traditional Contributors

1. Fork repository
2. Check [task list](.taskmaster/tasks/tasks.json) for available work
3. Create feature branch
4. Submit pull request

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Acknowledgments

- [Task Master](https://github.com/eyaltoledano/claude-task-master) by [@eyaltoledano](https://github.com/eyaltoledano)
- [Turborepo](https://turbo.build/repo) for monorepo optimization
- [Next.js](https://nextjs.org/) and [React](https://react.dev/) teams
- [Prisma](https://prisma.io/) for database tooling
- Financial Modeling Prep API
- Open source community

### API Gateway

The `packages/api-gateway` service is a FastAPI application that acts as a secure entry point for the frontend. It handles authentication and will orchestrate calls to other backend services.

## Getting Started

First, install the dependencies:

```bash
# Clone the repository
git clone https://github.com/Mi-Lan/FinAnalyzer.git
cd FinAnalyzer

# Build and start all services (web app, database, etc.)
docker-compose up --build
```
