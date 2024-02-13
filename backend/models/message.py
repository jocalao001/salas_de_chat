from odmantic import Model, ObjectId
from datetime import datetime


class Message(Model):
	room_id: ObjectId
	user_id: ObjectId
	username: str
	message: str
	created_at: datetime
	updated_at: datetime | None = None
	deleted_at: datetime | None = None
