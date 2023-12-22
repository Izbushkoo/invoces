from fastapi import FastAPI, Request


app = FastAPI()


@app.post("/wh/get")
async def webhook_reciver(request: Request):
    print(request.json())



if __name__ == "__main__":
    uvicorn.run()
