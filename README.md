# iFody
This repository contains the iFody project for COSC 310, a draft food‑delivery application.

---

# Running With Docker Compose

From the project root:

```bash
docker compose up --build
```

Backend will be available at:

```
http://localhost:8000
```

Frontend will be available at:

```
http://localhost:3000
```

To stop and remove all running containers:

```bash
docker compose down
```

---

# Running the Project Without Docker

### **Terminal 1 — Backend**

```bash
fastapi dev src/backend/main.py
```

or:

```bash
python -m uvicorn src.backend.main:app --reload --reload-dir src/backend --reload-exclude .venv
```

Backend runs at:

```
http://localhost:8000
```

---

### **Terminal 2 — Frontend**

```bash
cd src/frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:3000
```
