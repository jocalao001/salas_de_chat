from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from fastapi.responses import HTMLResponse
from dependencies.authorization import get_current_active_user
from routes import book, user, login, room, message
from models.user import UserIn
from models.message import Message
from typing import Annotated
from fastapi import Depends
from odmantic import ObjectId
from datetime import datetime
from database.client import engine
app = FastAPI()

app.include_router(book)
app.include_router(user)
app.include_router(login)
app.include_router(room)
app.include_router(message)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var room = "65caccf261addfb610900d8c"
            var user = "65caca8a01433dd1dcebe77c"
            var ws = new WebSocket(`ws://localhost:8000/ws/${room}/${user}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
	def __init__(self):
		self.rooms: dict[str, list[WebSocket]] = {}

	async def connect(self, websocket: WebSocket, room: ObjectId):
		await websocket.accept()
		if room in self.rooms:
			self.rooms[room].append(websocket)
		else:
			self.rooms[room] = [websocket]

	def disconnect(self, websocket: WebSocket, room: ObjectId):
		self.rooms[room].remove(websocket)

	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)

	async def broadcast(self, message: str, room: ObjectId):
		for connection in self.rooms[room]:
			await connection.send_text(message)

manager = ConnectionManager()


@app.get('/')
async def get():
	return HTMLResponse(html)


@app.websocket('/ws/{room}/{user_id}')
async def websocket_endpoint(websocket: WebSocket, room: ObjectId, user_id: ObjectId):
	await manager.connect(websocket, room)
	try:
		while True:
			data = await websocket.receive_text()
			user = await engine.find_one(UserIn, UserIn.id == user_id)
			message = Message(room_id=room,
							  user_id=user_id,
			                  username=user.username,
			                  message=data,
			                  created_at=datetime.now())
			await engine.save(message)
			await manager.broadcast(f"Message text was {data}", room)
	except WebSocketDisconnect:
		manager.disconnect(websocket, room)
