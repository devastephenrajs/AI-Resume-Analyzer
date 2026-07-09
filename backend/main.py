# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import resume, export, history, compare

app = FastAPI(title="AI Resume Analyzer API")

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(compare.router, prefix="/api", tags=["compare"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Resume Analyzer API"}


@app.get("/health")
async def check_health():
    return {"status": "ok"}
