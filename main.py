from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Healthy"}

@app.get("/print/{x}")
def test(x: int):
    return {"message": x}
