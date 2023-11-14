from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Union, Annotated
from dependencies import get_current_user

router = APIRouter(
	prefix="/users",
   	tags=["users"],
)

@router.get('/{uid}')
async def getUser(uid: int):
	return {'uid': uid}


@router.get('')
async def getUsers(user: any = Depends(get_current_user), offset: int = 1, limit: Union[str, None] = None):
	print(user)
	return {'offset': offset, 'limit': limit}

class User(BaseModel):
	name: str = Field(title='用户姓名')
	age: int

@router.post('')
async def createUser(user: User):
	user.name = user.name.title()
	dict = {'aa':111, **user.model_dump()}
	dict.update({'aa':222})
	return dict