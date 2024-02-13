from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from odmantic import ObjectId
from typing import Annotated
from database.client import engine
from models.user import UserIn, UserPatchScheme, UserOut
from dependencies.authorization import get_password_hash

user_routes = APIRouter()


def hidden_password(user: UserIn) -> UserOut:
	user_dict: dict = user.model_dump()
	user_dict.pop("password")
	return UserOut(**user_dict)


@user_routes.put('/users', response_model=UserOut, tags=["users"])
async def create_user(user: UserIn):
	user.password = get_password_hash(user.password)
	await engine.save(user)
	return hidden_password(user)


@user_routes.get('/users', response_model=list[UserOut], tags=["users"])
async def get_all_users():
	users = await engine.find(UserIn)
	return list(map(hidden_password, users))


@user_routes.get('/users/{user_id}', response_model=UserOut, tags=["users"])
async def get_user_by_id(user_id: ObjectId):
	user = await engine.find_one(UserIn, UserIn.id == user_id)
	if user is None:
		raise HTTPException(404)
	return hidden_password(user)


@user_routes.delete('/users/{user_id}', response_model=UserOut, tags=["users"])
async def delete_user_by_id(user_id: ObjectId):
	user = await engine.find_one(UserIn, UserIn.id == user_id)
	if user is None:
		raise HTTPException(404)
	await engine.delete(user)
	return hidden_password(user)


@user_routes.patch('/users/{user_id}', response_model=UserOut, tags=["users"])
async def update_user_by_id(user_id: ObjectId, patch: UserPatchScheme):
	user = await engine.find_one(UserIn, UserIn.id == user_id)
	if user is None:
		raise HTTPException(404)
	user.model_update(patch)
	await engine.save(user)
	return hidden_password(user)
