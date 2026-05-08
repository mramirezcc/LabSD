import socket
import threading
import pickle
import sys

from chat_message import ChatMessage


class Client:

  # constructor
  def __init__(self, server, port, username):
    self.server = server
    self.port = port
    self.username = username
    self.notif = " *** "
    self.socket = None
  # iniciar cliente
  def start(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.server, self.port))
    except Exception as e:
      self.display(f"Error connecting to server: {e}")
      return False
    msg = f"Connection accepted {self.server}:{self.port}"
    self.display(msg)
    # thread para escuchar servidor
    listen_thread = self.ListenFromServer(self)
    listen_thread.start()

    # enviar username
    try:
      self.socket.send(pickle.dumps(self.username))

    except Exception as e:
      self.display(f"Exception doing login: {e}")
      self.disconnect()
      return False
    return True

  # mostrar mensaje
  def display(self, msg):
    print(msg)
  # enviar mensaje
  def send_message(self, msg):
    try:
      self.socket.send(pickle.dumps(msg))
    except Exception as e:
      self.display(f"Exception writing to server: {e}")

  # desconectar
  def disconnect(self):
    try:
      if self.socket:
        self.socket.close()
    except:
      pass

  # thread que escucha servidor
  class ListenFromServer(threading.Thread):
    def __init__(self, client):
      threading.Thread.__init__(self)
      self.client = client
    def run(self):
      while True:
        try:
          msg = pickle.loads(self.client.socket.recv(4096))
          print(msg)
          print("> ", end="")
        except Exception as e:
          self.client.display(
              self.client.notif +
              f"Server has closed the connection: {e}" +
              self.client.notif
          )
          break


# ======================================
# MAIN
# ======================================

def main():
  port_number = 1500
  server_address = "localhost"
  user_name = "Anonymous"
  print("Enter the username: ")
  user_name = input()
  args = sys.argv[1:]
  if len(args) == 3:
    server_address = args[2]
  if len(args) >= 2:
    try:
      port_number = int(args[1])
    except:
      print("Invalid port number.")
      print("Usage: python client.py [username] [port] [serverAddress]")
      return
  if len(args) >= 1:
    user_name = args[0]
  if len(args) > 3:
    print("Usage: python client.py [username] [port] [serverAddress]")
    return
  # crear cliente
  client = Client(server_address, port_number, user_name)
  # conectar
  if not client.start():
    return
  print("\nHello.! Welcome to the chatroom.")
  print("Instructions:")
  print("1. Simply type the message to send broadcast to all active clients")
  print("2. Type '@username yourmessage' to send private message")
  print("3. Type 'WHOISIN' to see list of active clients")
  print("4. Type 'LOGOUT' to logoff from server")
  # loop principal
  while True:

    print("> ", end="")
    msg = input()
    # logout
    if msg.upper() == "LOGOUT":

      client.send_message(
          ChatMessage(ChatMessage.LOGOUT, "")
      )
      break
    # whoisin
    elif msg.upper() == "WHOISIN":
      client.send_message(
          ChatMessage(ChatMessage.WHOISIN, "")
      )
    # mensaje normal
    else:
      client.send_message(
          ChatMessage(ChatMessage.MESSAGE, msg)
      )
  client.disconnect()

if __name__ == "__main__":
  main()
