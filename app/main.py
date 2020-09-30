from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from classes.user_class import User, ConnectedUsers
from httpx import AsyncClient
import socketio
import uvicorn
import json


fast_app = FastAPI(debug=True)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=fast_app,
    socketio_path='/socket.io/'
)
users = ConnectedUsers()

carol_bus = "http://127.0.0.1:3005"

# event dispatcher function


# event listener from bus =====================================


@fast_app.post('/events')
async def event_listener(event: dict):
    print("Carol dispatched a new event: ", event)
    # test end
    if (event['type'] == 'userJoin'):
        payload = event['payload']
        user = User(payload['username'], sid=payload['sid'])
        print("connecting user => ", user)
        if(users.connect_user(user)):
            print(f"{user} ready for connection")
            await sio.emit('joined', {
                'connected_users': users.connected_users})

    print("test request ")

    return ({'status': 'event received'})

# ==============================================================


@ sio.event
async def connect(sid, environ):
    await sio.emit("connected", {
        'connect': "true", "sid": sid}, room=sid)


@ sio.event
async def disconnect(sid):
    print("disconnecting => ", sid)
    users.disconnect_user(sid)
    await sio.emit("disconnect", {
        'connected_users': users.connected_users
    })


@ sio.event
async def join(sid, data):
    print("JOINING")
    user = User(data['user']['username'], sid=sid)

    print("connected user user ==> ", data)
    print('connected users     ==> ', users.connected_users)
    users.connect_user(user)
    await sio.emit('joined', {
        'connected_users': users.connected_users})


@ sio.on("message_to")
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
            async with AsyncClient() as client:
                res = await client.post(f"{carol_bus}/events",
                                        json={"type": "messageSent", "payload": data})
            print(res)
        except Exception as err:
            print(err)

        print("test test test")

        await sio.emit('dispatched_message', {
            'message': data['message'],
            'recipient_sid': recipient_sid,
            'sender_sid': sender_sid,
            'recipient_username': recipient_username,
            'sender_username': sender_username,
            'timestamp': timestamp
        }, room=recipient_sid)

        await sio.emit("ok_status", {'ok_status': True})

    else:
        await sio.emit('error', {'error': 'user not identified'})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
