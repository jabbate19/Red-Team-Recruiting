class Connection:
    def __init__(self, name, socket, chat):
        self.name = name
        self.socket = socket
        self.chat = chat
        self.cmd = None
        self.file = None

    def __str__(self):
        return self.name

class FakeFile:
    def __init__(self, b):
        self.b = b

    def read(self):
        return self.b