# iFody
This is the repository for the iFody project in COSC 310, a food delivery draft application.

---

# Running With Docker Compose

From the project root:

```bash
docker compose up --build
```

Backend runs at:

```
http://localhost:8000
```

Frontend runs at:

```
http://localhost:3000
```

---

# Running the Project

### **Terminal 1 — Backend**

```bash
fastapi dev src/backend/main.py
```
or
```bash
python -m uvicorn src.backend.main:app --reload --reload-dir src/backend --reload-exclude .venv
```

Backend runs at:

```
http://localhost:8000
```

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
