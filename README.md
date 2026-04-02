# iFody---COSC-310-Project
This is the repository for the iFody project in COSC 310, a food delivery draft application.

---

# 📘 Running the Project

The iFody project supports **two different run modes** depending on your workflow:

- **One‑command mode** (FastAPI serves both frontend + backend on port 8000)
- **Two‑terminal mode** (Frontend dev server + FastAPI backend)

---

## 🚀 One‑Command Mode (Production‑Style)

In this mode, FastAPI serves **both** the backend API and the built React frontend.  
You only need **one terminal** and **one command**.

### **1. Build the frontend**  
(Only required when UI changes)

```bash
cd src/frontend
npm install
npm run build
```

This generates the production build in:

```
src/frontend/dist/
```

### **2. Run FastAPI from the project root**

```bash
fastapi dev src/backend/main.py
```

### **3. Open the app**

```
http://localhost:8000
```

### **What this mode does**

- FastAPI serves the backend  
- FastAPI serves the built frontend  
- Everything runs on **port 8000**  
- No Vite dev server  
- No second terminal  

Best for:
- Demos  
- Deployment  
- Simplicity  

---

## 🛠️ Two‑Terminal Mode (Development)

In this mode, the frontend runs on its own dev server with hot reload, while FastAPI runs separately.

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