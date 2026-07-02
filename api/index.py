from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

EMAIL = "24f2008956@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-e7eeib.example.com"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/stats")
def stats(values: str = Query(...)):
    nums = [int(x.strip()) for x in values.split(",")]
    total = sum(nums)

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }

from fastapi import HTTPException
from pydantic import BaseModel
import jwt

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-wfrhugll.apps.exam.local"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

class TokenRequest(BaseModel):
    token: str


@app.post("/verify")
def verify_token(req: TokenRequest):
    try:
        payload = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"valid": False}
        )
        
        
        
load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(v):
    return str(v).lower() in ["true", "1", "yes", "on"]


def coerce(key, value):
    if key in ["port", "workers"]:
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    # -------------------------
    # 1. YAML layer
    # -------------------------
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            yaml_config = yaml.safe_load(f) or {}
            config.update(yaml_config)

    # -------------------------
    # 2. .env layer
    # -------------------------
    # APP_LOG_LEVEL=info
    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    # APP_API_KEY=key-727amr6hbx
    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # Alias support: NUM_WORKERS -> workers
    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    # -------------------------
    # 3. OS environment layer
    # (highest priority before CLI)
    # -------------------------
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("APP_WORKERS"):
        config["workers"] = int(os.getenv("APP_WORKERS"))

    if os.getenv("APP_DEBUG"):
        config["debug"] = coerce("debug", os.getenv("APP_DEBUG"))

    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # -------------------------
    # 4. CLI overrides
    # ?set=key=value&set=...
    # -------------------------
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)

            if key in ["port", "workers"]:
                config[key] = int(value)

            elif key == "debug":
                config[key] = value.lower() in [
                    "true",
                    "1",
                    "yes",
                    "on",
                ]

            else:
                config[key] = value

    # -------------------------
    # Never expose secrets
    # -------------------------
    config["api_key"] = "****"

    return config

@app.get("/effective-config")
def effective_config():
    return {"test": "working"}