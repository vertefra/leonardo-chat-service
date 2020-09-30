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
    socketio_path='/socket.io',
)

users = ConnectedUsers()

carol_bus = "http://127.0.0.1:3005"

# event dispatcher function


async def send_event(endpoint: str, data: dict, event_type: str):
    event = {"type": event_type, "payload": data}
    res = await requests.post(f"{carol_bus}/{endpoint}", json=event)
    return res.json()

# event listener from bus =====================================

# event data model


@fast_app.post('/events/')
async def event_listener(event: dict):
    print("Carol dispatched a new event: ")
    if (event['type'] == 'userJoin'):
        user = User(event['payload'])
        if(users.connect_user(user)):
            print(f"{user} ready for connection")
    return ({'status': 'event received'})

# ==============================================================


@sio.event
async def connect(sid, environ):
    await sio.emit("connected", {
        'connect': "true", "sid": sid}, room=sid)


@sio.event
async def disconnect(sid):
    print("disconnecting => ", sid)
    users.disconnect_user(sid)
    await sio.emit("disconnect", {
        'connected_users': users.connected_users
    })


@sio.on("join")
async def join(sid, data):
    user = User(data['user']['username'], sid=sid)

    print("connection user=> ", data)

    # sending event to Carol
    print('connected users ==> ', users.connected_users)
    users.connect_user(user)
    await sio.emit('joined', {
        'connected_users': users.connected_users})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
