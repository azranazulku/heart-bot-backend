from fastapi import FastAPI
from routers.xray_scan_evaluation_router import xray_scan_evaluation_router
from routers.openai_router import openai_router
from routers.user_router import user_router  # doğru isimle import

app = FastAPI()

app.include_router(xray_scan_evaluation_router)
app.include_router(openai_router)
app.include_router(user_router)  # user_router doğru şekilde eklenmeli

@app.get("/")
async def root():
    return {"message": "API is running"}
