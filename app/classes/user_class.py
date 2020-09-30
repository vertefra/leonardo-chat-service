class ConnectedUsers:
    def __init__(self):
        self.connected_users = {}

    def __repr___(self):
        return self.connected_users

    def connect_user(self, user):
        key = user.username
        user_dict = {'username': user.username, 'sid': user.sid}
        print()
        print(
            f"connecting {user.sid}, {user.username} with dict=>", user_dict)
        # print("key to update => ", self.connected_users[key])
        print()
        self.connected_users[key] = user_dict
        return True

    def disconnect_user(self, sid):
        for key in self.connected_users:
            print('Checking for sid to disconnect')
            if(sid == self.connected_users[key]['sid']):
                del self.connected_users[key]
                break
        return True


class User:
    def __init__(self, username, sid=None):
        self.username = username
        self.sid = sid

    def user_obj(self):
        return {'sid': self.sid, 'username': self.username}

    def __str__(self):
        return f"user: <{self.username}> <{self.sid}>"
