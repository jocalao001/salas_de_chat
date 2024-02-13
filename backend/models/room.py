from odmantic import Model, ObjectId
from datetime import datetime


class Room(Model):
	name: str
	created_at: datetime | None = datetime.now()
	create_by: ObjectId | None = None
	users: list[ObjectId] | None = None
