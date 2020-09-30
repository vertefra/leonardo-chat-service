from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from classes.user_class import User, ConnectedUsers

import socketio
import uvicorn

fast_app = FastAPI()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=fast_app,
    socketio_path='/socket.io'
)

users = ConnectedUsers()

carol_bus = "http://127.0.0.1:3005"


@sio.event
async def connect(sid, environ):
    await sio.emit("connected", {
        'connect': "true", "sid": sid})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
