# 🏥 Healthcare Claims Processing API

Hey there! 👋
Welcome to the **Healthcare Claims Processing API** — a powerful backend system built using **FastAPI** that streamlines the creation, management, and reporting of **health insurance claims**.

---
## 📘 Project Overview

This app demonstrates:

* ✅ Secure JWT Auth
* 📄 CRUD for insurance claims
* 📥 CSV bulk claim upload
* ⏳ Async report generation (Celery + Redis)
* 🔔 Webhook notification on report completion
* 📉 Rate-limited endpoints
---

## 🧠 My Approach

### 📘 Complete Project Design, Flow & Architecture

🔍 Explore how everything fits together — from models, authentication, background tasks, to webhook logic and error handling.

➡️ **🗂️ [CLICK HERE TO OPEN THE PROJECT EXPLANATION PDF](https://github.com/user-attachments/files/20847827/HEALTHCARE.CLAIM.API.pdf)** ⬅️

> This PDF breaks down the **entire backend system** in a clear, structured format.
> Ideal for **reviewers, tech leads**, and curious developers! 🧑‍💻

---
## 🎬 Demo Videos

* 🔐 **Postman Demo**
  [▶ Watch](https://github.com/user-attachments/assets/29505550-7242-499c-ab24-ba806d5ceb1d)

* ⚡ **Thunder Client Demo**
  [▶ Watch](https://github.com/user-attachments/assets/002c42c7-e607-4e30-888f-5df0cf454a02)

---

## 🚀 Quickstart Guide (Under 5 Minutes)

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/yourname/healthcare-claims-api.git
cd healthcare-claims-api
```

### 2️⃣ Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install All Requirements

```bash
pip install -r requirements.txt
```

### 4️⃣ Start Redis (If Not Running)

```bash
redis-server
```

### 5️⃣ Launch Celery Worker

```bash
celery -A app.celery_worker.celery_app worker --loglevel=info
```

### 6️⃣ Run FastAPI App

```bash
uvicorn app.main:app --reload
```

Visit 👉 [http://localhost:8000](http://localhost:8000)
to see your interactive Swagger API docs.

---

## 📁 Project Structure

```
app/
├── main.py                 # FastAPI entrypoint
├── celery_worker.py        # Celery configuration
├── Auth/
│   └── auth.py             # Login & signup logic
├── Tasks/
│   └── tasks.py            # Background job for reports
├── Utils/
│   ├── config.py           # App settings
│   ├── database.py         # SQLAlchemy DB setup
│   ├── logger.py           # Custom logging
│   ├── models.py           # ORM Models
│   └── schemas.py          # Pydantic Schemas
├── reports/                # CSV output folder
└── tests/                  # Pytest unit tests
```
---

## 🧪 How to Test the API

You can test the API using:

### 🔸 1. Thunder Client (VS Code Extension)

> 🧩 Lightweight and beginner-friendly (recommended for quick local testing)

* Open VS Code → Install **Thunder Client**
* Send requests by setting:

  * `Content-Type: application/json`
  * `Authorization: Bearer <your_token_here>` (after login)
* Upload CSV files directly in the request body for `/claims/bulk` *(premium feature)*

### 🔸 2. Postman

> 🌐 Ideal for team collaboration and full-featured API testing

* Import endpoints manually or use Swagger UI to copy requests

* Add an environment with a variable for the token

* Make sure to set headers:

  ```
  Authorization: Bearer <your_token_here>
  Content-Type: application/json
  ```

* To test `/claims/bulk`, go to `Body > form-data`, and upload the CSV file with key = `file`


### 🔸 3. Swagger UI (Auto-Generated)

> Built-in testing via browser

* Visit: [http://localhost:8000/docs](http://localhost:8000/docs)
* Authorize using the **JWT token** via the top-right 🔒 button
* Interact with every endpoint live

---

### 📁 Sample Request (Postman/Thunder Client)

#### ➕ Create Claim

```
POST /claims
```

**Headers:**

```
Authorization: Bearer <your_token>
Content-Type: application/json
```

**Body:**

```json
{
  "patient_name": "Jane Doe",
  "diagnosis_code": "D123",
  "procedure_code": "P456",
  "claim_amount": 1500.00
}
```

---

## 🔐 Authentication Endpoints

### 📝 Register

**POST** `/auth/signup`

```json
{
  "username": "testuser",
  "password": "strongpassword"
}
```

---

### 🔑 Login

**POST** `/auth/login`

```json
{
  "username": "testuser",
  "password": "strongpassword"
}
```

**Returns:**

```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

🔒 Use it in requests:

```
Authorization: Bearer your_jwt_token
```

---

## 📄 Claims Endpoints

### ➕ Create

**POST** `/claims`

```json
{
  "patient_name": "John Smith",
  "diagnosis_code": "D123",
  "procedure_code": "P456",
  "claim_amount": 1200.50
}
```

---

### 📋 Fetch All

**GET** `/claims`
Supports filters like: `status`, `diagnosis_code`, etc.

---

### 🔍 Fetch One

**GET** `/claims/{claim_id}`

---

### 🖊️ Update

**PUT** `/claims/{claim_id}`

```json
{
  "status": "APPROVED"
}
```

---

### ❌ Delete

**DELETE** `/claims/{claim_id}`

---

## 📦 Bulk Upload (CSV)

**POST** `/claims/bulk`
Upload claims from a `.csv` file

📌 Sample CSV:

```csv
patient_name,diagnosis_code,procedure_code,claim_amount
Alice,D12,P34,500
Bob,D56,P78,900
```
---

## 📊 Report Generation (Async via Celery)

### 1️⃣ Trigger Report

**POST** `/claims/report`

**Response:**

```json
{
  "task_id": "abc-123",
  "status": "PENDING",
  "message": "Report started"
}
```

---

### 2️⃣ Check Status

**GET** `/claims/report/{task_id}`

```json
{
  "status": "COMPLETED",
  "file_path": "reports/claims_report_abc.csv"
}
```

---

### 3️⃣ Download Report

**GET** `/claims/report/{task_id}/download`
Returns the generated CSV 📥

---

## 🔔 Webhook Notifications

**POST** `/webhook`

```json
{
  "task_id": "abc-123",
  "url": "https://webhook.site/your-custom-url"
}
```
---

## 🧪 Running Tests

Run unit tests using:

```bash
pytest tests/
```

### ✅ Test Coverage Includes:

* 🔐 Authentication
* 📄 Claims CRUD Operations
* 📥 CSV Bulk Upload
* ⏳ Background Task (Celery) Status

---

## 🙌 Contribute or Show Support

Like the project? Star it ⭐ on GitHub.
Got ideas or bugs? Open an issue — contributions are welcome!
---

## 👋 Let's Connect
Built with ❤️ by Mohammed
