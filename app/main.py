from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from classes.user_class import User, ConnectedUsers

import socketio
import uvicorn
import httpx
import json


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


# event listener from bus =====================================

# event data model


@fast_app.post('/events/')
async def event_listener(event: dict):
    print("Carol dispatched a new event: ", event)
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


@sio.event
async def join(sid, data):
    print("JOINING")
    user = User(data['user']['username'], sid=sid)

    print("connection user=> ", data, sid)

    # sending event to Carol
    print('connected users ==> ', users.connected_users)
    users.connect_user(user)
    await sio.emit('joined', {
        'connected_users': users.connected_users}, room=sid)


@sio.on("message_to")
async def message_to(sid, data):
    print()
    print("===== data after sent a message =======")
    print(data)
    print()
    print("=======================================")
    recipient_username = data['recipient_username']
    sender_sid = data['sender_sid']
    if(users.connected_users[recipient_username]):
        print()
        print("found recipient => ", recipient_username)
        print()
        recipient_sid = users.connected_users[recipient_username]['sid']
        sender_username = data['sender_username']
        timestamp = data['timestamp']
        data['recipient_sid'] = recipient_sid

        try:
            event = {"type": "messageSent", "payload": data}
            response = httpx.post(f"{carol_bus}/events", json=event)
            res = response.text()
            print("Response", res)
        except:
            print('Something went wrong')

        print("I should be after")

        await sio.emit('dispatched_message', {
            'message': data['message'],
            'recipient_sid': recipient_sid,
            'sender_sid': sender_sid,
            'recipient_username': recipient_username,
            'sender_username': sender_username,
            'timestamp': timestamp
        }, room=recipient_sid)

        # await emit("ok_status", {'ok_status': True})

    else:
        sio.emit('error', {'error': 'user not identified'})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
