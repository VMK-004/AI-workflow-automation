# Frontend Quick Start

## Get Running in 2 Minutes

### 1. Setup (30 seconds)

```bash
cd frontend
npm install
```

### 2. Configure Environment (10 seconds)

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
```

### 3. Start Dev Server (10 seconds)

```bash
npm run dev
```

Open http://localhost:5173

### 4. Test the App (1 minute)

1. **Register**: Go to http://localhost:5173/register
   - Create account with username, email, password

2. **Login**: Use your credentials

3. **Dashboard**: You'll see the main dashboard

4. **Create Workflow**:
   - Click "Workflows" in sidebar
   - Click "New Workflow"
   - Enter name and description
   - Click "Create"

5. **View Collections**:
   - Click "Vector Collections" in sidebar
   - See your FAISS collections

## That's it! ✅

You now have:
- ✅ Running frontend
- ✅ Connected to backend
- ✅ Auth working
- ✅ Dashboard loaded
- ✅ Workflows manageable

## Troubleshooting

### "Network Error"
- Make sure backend is running on port 8000
- Check `.env` file has correct API URL

### "Cannot connect to backend"
```bash
# In backend directory
cd ../backend
uvicorn app.main:app --reload
```

### Port 5173 already in use
```bash
# Kill the process or use different port
npm run dev -- --port 3000
```

## Next Steps

1. **Build Visual Editor**: Add React Flow for node canvas
2. **Add Vector UI**: Collection creation and search
3. **Execution Monitoring**: Real-time workflow status

---

**Status**: 🟢 Ready to develop!





