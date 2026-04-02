# iFody
This is the repository for the iFody project in COSC 310, a food delivery draft application.

---

# Running the Project

The iFody project supports **two different run modes** depending on your workflow:

- **One‑command mode** (FastAPI serves both frontend + backend on port 8000)
- **Two‑terminal mode** (Frontend dev server + FastAPI backend)

---

### **Terminal 1 — Backend**

```bash
fastapi dev src/backend/main.py
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