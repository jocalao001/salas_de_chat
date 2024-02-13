from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from database.client import engine
from dependencies.authorization import get_current_active_user
from models.room import Room
from models.user import UserIn
from odmantic import ObjectId
room_routes = APIRouter()


@room_routes.put('/rooms', response_model=Room, tags=["rooms"])
async def create_room(room: Room, current_user: Annotated[UserIn, Depends(get_current_active_user)]):
	room.create_by = current_user.id
	room.users = [current_user.id]
	user = await engine.find_one(UserIn, UserIn.id == current_user.id)
	user.rooms.append(room.id)
	await engine.save(room)
	await engine.save(user)
	return room


@room_routes.get('/rooms/{user_id}', tags=["rooms"])
async def get_rooms_by_user(user_id: str):
	rooms = await engine.find(Room, Room.users == user_id)
	return rooms


@room_routes.patch('/rooms/{room_id}', tags=['rooms'], response_model=Room)
async def add_user_to_room(room_id: ObjectId, current_user: Annotated[UserIn, Depends(get_current_active_user)]):
	room = await engine.find_one(Room, Room.id == room_id)
	user = await engine.find_one(UserIn, UserIn.id == current_user.id)
	room.users.append(current_user.id)
	await engine.save(room)
	await engine.save(user)
	return room

