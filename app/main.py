from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import search, documents, indexes, settings as settings_api, tasks, causal

logging.basicConfig(
    level=logging.INFO if not settings.api_debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 搜索引擎API服务启动中...")
    logger.info(f"📋 配置: MEILI_URL={settings.meili_url}")
    yield
    logger.info("🛑 搜索引擎API服务关闭")


app = FastAPI(
    title="搜索引擎API",
    description="基于Meilisearch的高性能搜索引擎API，支持混合搜索、拼写容错、同义词、多语种、因果推理搜索等功能",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": "Internal Server Error"}
    )


app.include_router(search.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(indexes.router, prefix="/api/v1")
app.include_router(settings_api.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(causal.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "搜索引擎API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "实时搜索（输入即搜）",
            "拼写错误容错",
            "混合搜索（关键词+语义）",
            "筛选与排序",
            "同义词支持",
            "多语种支持",
            "分面搜索",
            "高亮显示",
            "因果推理搜索",
            "知识图谱管理",
            "用户意图理解",
            "反事实推理",
            "因果路径分析",
            "潜在需求发现"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
