from fastapi import FastAPI

from taskhub.api.v1 import router

app = FastAPI()
app.include_router(router)


@app.get("/health")
async def root():
    return {"message": "Good"}
