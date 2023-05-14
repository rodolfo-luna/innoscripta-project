from fastapi import FastAPI

from routes import company_router


app = FastAPI(title='Companies api')
app.include_router(company_router.router, tags=['company'])


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)