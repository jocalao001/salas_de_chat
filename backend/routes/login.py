import os
from datetime import timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.dependencies.authorization import authenticate_user, create_access_token, get_current_active_user
from backend.models.authorization import Token
from backend.models.user import UserIn

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

login_routes = APIRouter()


@login_routes.post('/token', tags=["login"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
	user = await authenticate_user(form_data.username, form_data.password)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={
				"WWW-Authenticate": "Bearer"
			},
		)
	access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
	access_token = create_access_token(
		data={
			"sub": user.username # TODO: falta arreglar
		}, expires_delta=access_token_expires
	)
	return Token(access_token=access_token, token_type="bearer")


@login_routes.get("/users/me/")
async def read_users_me(
		current_user: Annotated[UserIn, Depends(get_current_active_user)]
):
	return current_user
