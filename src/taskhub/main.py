from fastapi import FastAPI

from taskhub.api.v1 import router
from taskhub.handlers import register_exception_handlers

app = FastAPI()
app.include_router(router)
register_exception_handlers(app)


@app.get("/health")
async def root():
    return {"message": "Good"}
