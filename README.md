# SparkProcess

An autonomous AI innovation platform that orchestrates 21 specialist agents through the **Double Diamond** methodology — from raw problem discovery to a validated, launch-ready solution.

---

## How it works

SparkProcess runs your innovation challenge through four phases, each powered by a dedicated set of Claude agents:

```
┌─────────────────────────────────────────────────────────────────┐
│  EXPLORE           DEFINE           CREATE           LAUNCH      │
│  (parallel)     ── (sequential) ──  (parallel)   ── (sequential)│
│                                                                   │
│  Market           Synthesise        Ideation        Orchestrate  │
│  Ethnographic     Define Problem    Prototype       Governance   │
│  Competitive  ══► Personas      ══► UI/UX       ══► Monitoring  │
│  Data Mining      Set Goals         Code Dev        Support      │
│  Trends           Frame Problem     A/B Testing     Updates      │
│  Tech Spikes                                                      │
│               🔒 Security 1                   🔒 Security 2      │
└─────────────────────────────────────────────────────────────────┘
```

Two autonomous **Security Checkpoints** gate progress — evaluating bias, privacy, ethics, regulatory risk, and scope before the pipeline continues.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS, Framer Motion, Zustand |
| Backend | FastAPI, LangGraph, Python 3.12 |
| LLM | Claude 3.5 Sonnet / Haiku via AWS Bedrock (cross-region inference) |
| Memory | AWS DynamoDB (session persistence) |
| Observability | Datadog LLM Observability |
| Infra | Docker, Docker Compose, DynamoDB Local (dev) |

Real-time pipeline progress is streamed to the UI over **Server-Sent Events (SSE)**.

---

## Getting started

### Prerequisites

- Docker & Docker Compose
- AWS account with Bedrock access (Claude 3.5 Sonnet enabled in `us-east-1`)
- AWS credentials (access key pair, or an IAM role if running on EC2/ECS)

### 1. Clone and configure

```bash
git clone https://github.com/willfoxy/SparkProcess.git
cd SparkProcess

cp .env.example .env
# Open .env and fill in your AWS credentials and any optional settings
```

The only required values to get started:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your key>
AWS_SECRET_ACCESS_KEY=<your secret>
```

Everything else has sensible defaults for local development.

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| DynamoDB Local | http://localhost:8001 |

### 3. Run your first session

Open http://localhost:3000, describe your innovation challenge, and watch the agents work in real time.

---

## Local development (without Docker)

**Backend**

```bash
cd backend
pip install -r requirements.txt
export PYTHONPATH=$(pwd)/..
uvicorn backend.api.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

The frontend proxies `/api/*` to `localhost:8000` automatically in dev mode (no env var needed).

---

## Deploying to Vercel (frontend)

1. Import the repo in [vercel.com/new](https://vercel.com/new)
2. In **Settings → General → Root Directory** set it to `frontend`
3. Add one environment variable:

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_API_URL` | URL of your deployed backend (e.g. `https://api.yourapp.com`) |

4. Deploy. The frontend will call your backend directly (SSE streams bypass Vercel's proxy layer).

> **Backend CORS:** add your Vercel deployment URL to `CORS_ORIGINS` in your backend environment.

---

## Environment variables

See [`.env.example`](.env.example) for the full list with descriptions. Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | Bedrock region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS credentials | — |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | — |
| `BEDROCK_MODEL_ID` | Primary Claude model | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `DYNAMODB_TABLE_NAME` | Session memory table | `spark-process-memory` |
| `DYNAMODB_ENDPOINT_URL` | Set to `http://localhost:8001` for local dev | _(AWS)_ |
| `DD_API_KEY` | Datadog API key (optional) | — |
| `DD_LLM_OBS_ENABLED` | Enable LLM tracing | `true` |
| `SECURITY_STRICT_MODE` | Reject sessions with risk score > 60 | `false` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend (Vercel / production) | _(uses proxy in dev)_ |

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sessions` | Start a new innovation session |
| `GET` | `/api/sessions` | List active sessions |
| `GET` | `/api/sessions/{id}` | Get full session state and outputs |
| `GET` | `/api/sessions/{id}/stream` | SSE stream of live pipeline events |
| `DELETE` | `/api/sessions/{id}` | Clear session memory |
| `GET` | `/health` | Health check |

---

## Project structure

```
SparkProcess/
├── backend/
│   ├── agents/            # 21 specialist agent classes
│   ├── api/main.py        # FastAPI app + SSE streaming
│   ├── graph/
│   │   ├── pipeline.py    # LangGraph DAG (parallel + sequential phases)
│   │   └── state.py       # Shared state schema + merge reducers
│   ├── memory/            # DynamoDB session persistence
│   ├── observability/     # Datadog LLM tracing
│   └── config.py          # Pydantic settings
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom hooks (SSE, session state)
│   └── lib/               # API client
├── docker-compose.yml
├── Dockerfile.api
└── .env.example
```
