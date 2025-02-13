from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_headers=["*"], allow_origins=["*"])

@app.post("/run")
def post_run(task:str):
    return {"task": task}

@app.get("/read")
def get_read(path:str):
    return {"path": path}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("hello:app", host="127.0.0.1", port=8000)
