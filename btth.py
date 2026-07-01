from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

promo_codes_db = {
    "SUMMER25": {"code": "SUMMER25", "discount_rate": 0.15, "max_budget": 50000000, "is_active": True},
    "WELCOME50": {"code": "WELCOME50", "discount_rate": 0.50, "max_budget": 10000000, "is_active": False},
}


class PromoInternal(BaseModel):
    code: str
    discount_rate: float
    max_budget: int
    is_active: bool


class PromoPublic(BaseModel):
    code: str
    discount_rate: float


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    envelope = {
        "statusCode": exc.status_code,
        "data": None,
        "error": exc.detail,
        "message": exc.detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": str(request.url.path),
    }
    return JSONResponse(status_code=exc.status_code, content=envelope)


@app.get("/promos/{code}", response_model=PromoPublic)
def get_promo(code: str):
    promo = promo_codes_db.get(code)
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mã giảm giá không tồn tại"
        )

    if not promo["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã giảm giá đã hết hạn sử dụng",
        )

    return promo
