from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

EMAIL = "24f2008956@ds.study.iitm.ac.in"  # <-- replace with your exact logged-in email
ALLOWED_ORIGIN = "https://dash-e7eeib.example.com"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    nums = [int(x.strip()) for x in values.split(",") if x.strip()]

    count = len(nums)
    total = sum(nums)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / count,
    }

@app.get("/")
async def home():
    return {"message": "API is running"}