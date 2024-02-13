import os
from datetime import timedelta, datetime, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from database.client import engine
from models.user import UserIn
from models.authorization import TokenData

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
	return pwd_context.hash(password)


async def get_user(username: str) -> UserIn:
	user = await engine.find_one(UserIn, UserIn.username == username)
	return user


async def authenticate_user(username: str, password: str):
	user = await get_user(username)
	if not user:
		return False
	if not verify_password(password, user.password):
		return False
	return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=15)
	to_encode.update({
		"exp": expire
	})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail={"Could not validate credentials"},
		headers={
			"WWW-Authenticate": "Bearer"
		}
	)
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
		token_data = TokenData(username=username)
	except JWTError:
		raise credentials_exception
	user = await get_user(username=token_data.username)
	if user is None:
		raise credentials_exception
	return user


async def get_current_active_user(current_user: Annotated[UserIn, Depends(get_current_user)]):
	if current_user.disabled:
		raise HTTPException(status_code=400, detail={"Inactive User"})
	return current_user
