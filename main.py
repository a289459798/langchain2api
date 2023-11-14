from fastapi import FastAPI, Query, Header
from typing import Union, Annotated
from pydantic import BaseModel, Field
from tools.error import Abort
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from routers import users
from routers import chat
from middlewares.fornt_middleware import ForntMiddleware
from dotenv import load_dotenv
import os
import uvicorn

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc:RequestValidationError):
    return JSONResponse({'message': exc.errors()[0]['msg'] + ': ' + exc.errors()[0]['loc'][1]}, status_code=400)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse({'message': exc.detail}, status_code=exc.status_code)

app.include_router(users.router)
app.include_router(chat.router)

app.add_middleware(ForntMiddleware)

@app.get('/')
async def root():
	return {'message': 'hello fastapi'}



@app.get('/header')
async def getHeader(user_agent: Annotated[Union[str, None], Header()] = None):
	Abort(401, '不存在')
	return  user_agent


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')

if __name__ == '__main__':
      uvicorn.run(app, host="0.0.0.0", port=8000)