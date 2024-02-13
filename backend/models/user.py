from odmantic import Model, ObjectId
from pydantic import EmailStr, BaseModel


class UserIn(Model):
	username: str
	email: EmailStr
	password: str
	disabled: bool = False
	rooms: list[ObjectId] = []


class UserOut(Model):
	username: str
	email: EmailStr
	disabled: bool | None = False
	rooms: list[ObjectId] = []


class UserPatchScheme(BaseModel):
	username: str = None
	email: float = None
	password: float = None
	disabled: bool = None
