import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8899")),
        reload=os.getenv("APP_RELOAD", "false").lower() == "true",
    )
