import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8001,
        reload=True,
        reload_excludes=["app/database.py","app/models/*.py"]
    )