from fastapi import FastAPI, Depends
from routes import company_router
from dependency import has_access


app = FastAPI(title='Companies api')

PROTECTED = [Depends(has_access)]
app.include_router(company_router.router, tags=['company'])


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)