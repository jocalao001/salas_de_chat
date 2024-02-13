from fastapi import APIRouter
from backend.database.client import engine
from backend.models.message import Message
from odmantic import ObjectId
message_routes = APIRouter()


@message_routes.get('/messages/{room_id}', tags=["messages"])
async def get_messages_by_room(room_id: ObjectId):
	messages = await engine.find(Message, Message.room_id == room_id)
	return messages
