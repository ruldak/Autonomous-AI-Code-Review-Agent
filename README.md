# 🤖 Autonomous AI Code Review Agent

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-F5A623?style=for-the-badge&logo=openai&logoColor=white)](https://groq.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=chainlink)](https://www.langchain.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

An enterprise-grade, multi-tenant AI-powered code review assistant. It hooks directly into your GitHub workflow as a GitHub App, intercepts Pull Requests via secure webhooks, builds an **Abstract Syntax Tree (AST)** representation of code modifications, runs regex-based security compliance scanners, and processes structural code with a high-performance **Groq LLM (via LangChain)**. Within seconds, it posts actionable, contextual inline review comments directly back to your GitHub PR discussion.

---

## 📖 Table of Contents

- [💡 Layperson's Guide (What & Why)](#-laypersons-guide-what--why)
- [🎬 See it in Action (Zero-Installation Walkthrough)](#-see-it-in-action-zero-installation-walkthrough)
- [🏗️ Technical Architecture & Flow](#%EF%B8%8F-technical-architecture--flow)
- [🛡️ Code Scanning Strategies](#%EF%B8%8F-code-scanning-strategies)
- [💾 Database & Storage Schema](#-database--storage-schema)
- [🚀 Local Setup & Installation](#-local-setup--installation)
- [🐳 Production Deployment with Docker Compose](#-production-deployment-with-docker-compose)
- [⚙️ Environment Configuration](#%EF%B8%8F-environment-configuration)

---

## 💡 Layperson's Guide (What & Why)

### What does this tool do?
Imagine hiring a senior, world-class developer whose *only* job is to review changes in your code, 24 hours a day, 7 days a week, and who gets the job done in less than 3 seconds. 

That is what this **Autonomous AI Code Review Agent** does. 

Whenever a programmer creates a **Pull Request (PR)**—which is simply a request to merge new code changes into the main company codebase—this agent automatically wakes up, reads the new changes line-by-line, analyzes them for errors, and posts comments telling the programmer what needs to be fixed.

### Why is this valuable?
1. **Never Let Secrets Leak:** It instantly catches developers accidentally uploading passwords or AWS credentials before they reach the main repository.
2. **Prevent Security Vulnerabilities:** It flags weaknesses that hackers could exploit, such as insecure database queries (SQL injection).
3. **Double-Check Logic:** It spots complex bugs, loops that slow down performance, and missing error protection that might cause the application to crash.
4. **Time & Cost Savings:** Senior engineers spend hours reviewing code. This tool automates the repetitive parts, letting them focus on building features.

### How does a non-technical person experience it?
You don't need to open terminal windows or touch code! You just use GitHub as usual:
```
1. Developer uploads code modifications to GitHub.
      ↓
2. The AI Agent automatically runs in the background.
      ↓
3. Inline notes appear directly on the developer's screen:
   "⚠️ Line 12: Warning! This SQL query could allow SQL injection. Here is why..."
```

---

## 🎬 See it in Action (Zero-Installation Walkthrough)

To understand exactly how the agent behaves, let’s walk through a realistic scenario. You don't need to install or run the application; the steps below illustrate exactly how it works in real-time.

### Step 1: A Developer Submits Insecure Code
A developer opens a Pull Request on a GitHub repository. They have added a new file named `payment_processor.js` containing several hidden issues:

```javascript
// Line 1: Payment logic
const eval = require('eval');

function processPayment(userInput) {
    // ⚠️ Secret Leak: Access Key left in code
    const awsKey = "AKIA1234567890ABCDEF";
    
    // ⚠️ SQL Injection: Directly injecting variables into queries
    const query = "SELECT * FROM transactions WHERE card = '" + userInput.cardNumber + "'";
    
    // ⚠️ Performance Trap: Inefficient nested looping
    for (let i = 0; i < 1000; i++) {
        for (let j = 0; j < 1000; j++) {
            console.log("Checking transactions: ", i, j);
        }
    }
    
    // ⚠️ Security Risk: Remote Code Execution hazard
    return eval(userInput.scriptCode);
}
```

### Step 2: The Agent Receives the Event and Triggers Scanning
Instantly, the FastAPI server receives a webhook notification from GitHub, validates the request, and queues a review task to Celery via Redis. The Celery worker processes the review asynchronously. If you inspect the logs, here is what you would see:

**FastAPI Server Log:**
```log
INFO:  [2026-06-23 21:38:12] Received GitHub webhook [event=pull_request, action=opened, repo=myorg/payment-system]
INFO:  [2026-06-23 21:38:13] Registered new SaaS tenant [installation_id=45991823]
INFO:  [2026-06-23 21:38:13] Triggering review for PR [pr_number=42, repo=myorg/payment-system]
INFO:  [2026-06-23 21:38:13] Enqueued review task to Celery [task=process_pr_review_task]
```

**Celery Worker Log:**
```log
INFO:  [2026-06-23 21:38:13] Starting Celery task [pr_number=42, repo=myorg/payment-system]
INFO:  [2026-06-23 21:38:13] Fetching PR changed files [url=https://api.github.com/repos/myorg/payment-system/pulls/42/files]
INFO:  [2026-06-23 21:38:14] Fetched changed files [count=1, pr_number=42]
INFO:  [2026-06-23 21:38:14] Tree-sitter: AST Parsed Successfully [filename=payment_processor.js, language=javascript]
INFO:  [2026-06-23 21:38:14] Cached AST in Redis [key=ast:myorg/payment-system:payment_processor.js]
INFO:  [2026-06-23 21:38:14] Security pattern matched [pattern=AWS Access Key, filename=payment_processor.js, line=5]
INFO:  [2026-06-23 21:38:14] Security pattern matched [pattern=SQL Injection (Concat), filename=payment_processor.js, line=8]
INFO:  [2026-06-23 21:38:14] Security pattern matched [pattern=Dangerous Eval, filename=payment_processor.js, line=18]
INFO:  [2026-06-23 21:38:14] Starting AI analysis [filename=payment_processor.js, model=openai/gpt-oss-120b]
INFO:  [2026-06-23 21:38:16] AI analysis completed [filename=payment_processor.js, findings_count=1]
INFO:  [2026-06-23 21:38:16] Attempting to post inline review to GitHub [url=https://api.github.com/repos/myorg/payment-system/pulls/42/reviews]
INFO:  [2026-06-23 21:38:17] Successfully posted inline GitHub review [pr_number=42]
```

### Step 3: The Code Review Appears on GitHub
On GitHub, the pull request interface updates immediately. The developer is notified with inline code reviews matching the exact lines in their code:

![Inline Comment Screenshot](inline_comment_ss.png)

---

#### **Review Box on Line 5**
> 🛑 **[BLOCKER] Configuration**
> 
> **Message:** Hardcoded secret detected: AWS Access Key
> 
> **Explanation:** Menyimpan kredensial atau secret key secara hardcoded di dalam source code adalah risiko keamanan fatal. Secret dapat terekspos jika repository bocor atau terbaca di history commit.

---

#### **Review Box on Line 8**
> 🛑 **[CRITICAL] Security**
> 
> **Message:** Potential SQL Injection via string concatenation
> 
> **Explanation:** Menggabungkan string SQL dengan variabel eksternal secara langsung (concatenation) sangat rentan terhadap injeksi. Gunakan parameterized queries.

---

#### **Review Box on Line 10**
> ⚠️ **[WARNING] Performance**
> 
> **Message:** Inefficient nested loops detected
> 
> **Explanation:** An $O(N^2)$ nested loop executing $1,000,000$ iterations total is executing inside a basic client function. This block will block execution frames and impact API response times.

---

#### **Review Box on Line 18**
> 🛑 **[CRITICAL] Security**
> 
> **Message:** Dangerous use of eval()
> 
> **Explanation:** Fungsi eval() mengeksekusi string sebagai kode. Jika input berasal dari user, ini adalah celah Remote Code Execution (RCE).

---

## 🏗️ Technical Architecture & Flow

The application leverages a decoupled background task model powered by **Celery** with **Redis** as a message broker. This design allows the FastAPI web app to respond to GitHub's webhook request immediately, preventing webhook timeout issues, while distributed Celery workers execute deep static syntax tree parsing and large language model evaluations asynchronously.

## 🛡️ Code Scanning Strategies

The code analysis process is divided into two distinct components: a static, high-speed Regex compliance engine and an Abstract Syntax Tree (AST) augmented Language Model.

### 1. Static Security Scan (Patterns)
For absolute safety, secret-key leak checking and high-profile security issues are detected locally before any code gets sent to external LLMs. The scanning engine checks for:
*   **Credentials:** AWS Access Keys (`AKIA...`), generic API keys, databases passwords, and bearer tokens.
*   **Injection Vulnerabilities:** Insecure SQL string concatenations.
*   **Dangerous Code Execution:** Native execution commands (e.g. `eval()`).

### 2. AST (Abstract Syntax Tree) Parser
Using the high-speed tree-sitter libraries (`tree-sitter-python` and `tree-sitter-javascript`), the application compiles the incoming code files into an AST. 
*   **Supported File Types:** `.py` (Python), `.js` (JavaScript), `.jsx` (React/Javascript).
*   **Metric Extraction:** It maps code structures down to function declarations, classes, and code hierarchy metrics.
*   **AI Context Augmentation:** These structural metrics are supplied to the LLM. Providing the list of defined classes/functions lets the AI accurately locate references, scope, and variables, ensuring context-rich reviews.

---

## 💾 Database & Storage Schema

The SQL database (configured via **SQLAlchemy Async Session**) maps SaaS integrations and review logs.

### Schema Relationships
```mermaid
erDiagram
    tenants {
        int id PK
        int github_installation_id UK
        datetime created_at
    }
    review_logs {
        int id PK
        int tenant_id FK
        string repo_full_name
        int pr_number
        string status
        int findings_count
        json ai_metadata
        datetime created_at
    }
    tenants ||--o{ review_logs : reviews
```

*   **`tenants`:** Tracks registered organizations integrating with the application (isolated by their unique GitHub Installation ID).
*   **`review_logs`:** Audits completed reviews, recording the status (`PENDING`, `SUCCESS`, `FAILED`), total findings reported, and AI parameters (tokens used, response payload metadata).

---

## 📊 Analytics & Dashboard API
The application exposes RESTful endpoints to retrieve historical review data and SaaS metrics. These endpoints are designed to be consumed by a frontend dashboard (e.g., React, Next.js, Streamlit).

### `GET /reviews/logs`
Retrieves paginated review history.
**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max 100)
- `repo_full_name` (string, optional): Filter by repository name
- `status` (string, optional): Filter by status (`SUCCESS`, `FAILED`)

### `GET /reviews/stats`
Retrieves aggregated SaaS metrics and success rates.
**Query Parameters:**
- `repo_full_name` (string, optional): Filter stats by repository

**Response Example:**
```json
{
  "total_reviews": 150,
  "successful_reviews": 145,
  "failed_reviews": 5,
  "success_rate_percent": 96.67,
  "total_bugs_detected": 342
}
```

---

## 🚀 Local Setup & Installation

### Prerequisites
*   Python 3.11+ installed.
*   PostgreSQL running (locally or on cloud).
*   Redis instance running.
*   Groq API Key (for LLM analysis).
*   GitHub Developer Account (to configure a GitHub App or issue a GitHub Personal Access Token).

### Steps
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/ruldak/Autonomous-AI-Code-Review-Agent.git
    cd Autonomous-AI-Code-Review-Agent
    ```

2.  **Create a Virtual Environment & Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Setup Environment Configuration:**
    Copy the sample configuration file and populate your keys:
    ```bash
    cp .env.example .env
    ```
    *(See [Environment Configuration](#%EF%B8%8F-environment-configuration) below for details).*

4.  **Run Database Migrations:**
    Initialize tables using Alembic:
    ```bash
    alembic upgrade head
    ```

5.  **Start the Server:**
    Run the Uvicorn local development server:
    ```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    ```
    Your health endpoint is now accessible at `http://127.0.0.1:8000/health`.

6.  **Start the Celery Worker:**
    In a new terminal window (with virtual environment active), start the Celery worker to consume the queued review tasks:
    ```bash
    celery -A app.core.celery_app.celery_app worker --loglevel=info
    ```
    *Note for Windows users:* If you are running locally on Windows without WSL, you should run with the `--pool=solo` parameter:
    ```bash
    celery -A app.core.celery_app.celery_app worker --loglevel=info --pool=solo
    ```

---

## 🐳 Production Deployment with Docker Compose

For production, the service containerizes components into isolated services (FastAPI, Redis, PostgreSQL).

Run the full stack with a single command:
```bash
docker-compose up --build -d
```

This starts:
*   `code_review_web` at port `8000`.
*   `code_review_redis` at port `6379`.
*   `code_review_postgres` at database port `5432`.
*   *(Includes active healthcheck directives, ensuring services are ready before starting dependent containers).*

---

## 🔗 Multi-Tenant SaaS Installation Flow
To allow other users or organizations to use your SaaS without manual token configuration, the application leverages the official GitHub App Installation Flow:

1. **Register a GitHub App** in your GitHub Developer Settings.
2. **Set the Webhook URL** to your public server endpoint (e.g., `https://your-domain.com/webhook`).
3. **Set the Setup URL** to your callback endpoint (e.g., `https://your-domain.com/github/setup`).
4. **Share the public installation link** with your users: 
   `https://github.com/apps/YOUR-APP-NAME/installations/new`
5. When a user installs the app, GitHub redirects them to your Setup URL with an `installation_id`. Your server automatically registers this ID as a new Tenant in PostgreSQL, and the bot instantly starts reviewing their Pull Requests using isolated JWT credentials.

___

## ⚙️ Environment Configuration

Create a file named `.env` in the root directory. Below is the list of expected values:

```ini
# Server Context
APP_ENV=development                     # 'development' or 'production'
LOG_LEVEL=INFO                          # Log filtering level (DEBUG, INFO, WARNING, ERROR)

# GitHub Integration
GITHUB_APP_ID=1028372                   # The ID of your registered GitHub App
GITHUB_PRIVATE_KEY_PATH=./private-key.pem  # Path to the private key downloaded from GitHub App settings
GITHUB_WEBHOOK_SECRET=your_hmac_secret  # Secret token configured in the GitHub Webhook settings
GITHUB_PAT=ghp_exampleToken1234567890   # Personal Access Token used for development fallback testing

# AI Processing Model
GROQ_API_KEY=gsk_Ue3N...                # Your API key from the Groq console

# Infrastructure Connections
REDIS_URL=redis://localhost:6379/0      # Redis instance connection string
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/code_review_db # PostgreSQL Async connection URI
```

---

*This application is built for maximum speed, security, and integration convenience. For questions regarding customized AST plugins, please open an issue in the repository.*