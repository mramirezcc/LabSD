import socket
import threading
import pickle
from datetime import datetime

from chat_message import ChatMessage


class Server:
  unique_id = 0
  # constructor
  def __init__(self, port):
    self.port = port
    self.al = []
    self.keep_going = True
    self.notif = " *** "
  # iniciar servidor
  def start(self):
    try:
      server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_socket.bind(("0.0.0.0", self.port))
      server_socket.listen()
      print(f"Server waiting for Clients on port {self.port}.")
      while self.keep_going:
        client_socket, address = server_socket.accept()
        print(f"Connection accepted {address}")
        t = self.ClientThread(self, client_socket)
        self.al.append(t)
        t.start()
    except Exception as e:
      print(f"Exception on ServerSocket: {e}")
  # mostrar mensajes
  def display(self, msg):
    time = datetime.now().strftime("%H:%M:%S")
    print(f"{time} {msg}")
  # broadcast
  def broadcast(self, message):
    time = datetime.now().strftime("%H:%M:%S")
    words = message.split(" ", 2)
    is_private = False
    if len(words) > 1 and words[1].startswith("@"):
      is_private = True
    # mensaje privado
    if is_private:
      to_check = words[1][1:]
      message = words[0] + " " + words[2]
      message_lf = f"{time} {message}\n"
      found = False
      for ct in self.al:
        if ct.username == to_check:
          if not ct.write_msg(message_lf):
            self.al.remove(ct)
          found = True
          break
      return found

    # broadcast general
    else:
      message_lf = f"{time} {message}\n"
      print(message_lf)
      for ct in self.al:
        if not ct.write_msg(message_lf):
          self.al.remove(ct)
          self.display(
              f"Disconnected Client {ct.username} removed from list."
          )
      return True

  # remover cliente
  def remove(self, client_id):
    disconnected_client = ""
    for ct in self.al:
      if ct.id == client_id:
        disconnected_client = ct.username
        self.al.remove(ct)
        break
    self.broadcast(
        self.notif +
        disconnected_client +
        " has left the chat room." +
        self.notif
    )

  # ======================================
  # CLIENT THREAD
  # ======================================

  class ClientThread(threading.Thread):
    def __init__(self, server, socket_client):
      threading.Thread.__init__(self)
      Server.unique_id += 1
      self.id = Server.unique_id
      self.server = server
      self.socket = socket_client
      self.username = ""
      self.date = str(datetime.now())
      print("Thread trying to create Input/Output Streams")
      try:
        self.username = pickle.loads(
            self.socket.recv(4096)
        )
        self.server.broadcast(
            self.server.notif +
            self.username +
            " has joined the chat room." +
            self.server.notif
        )
      except Exception as e:
        self.server.display(
            f"Exception creating streams: {e}"
        )

    # run
    def run(self):
      keep_going = True
      while keep_going:
        try:
          cm = pickle.loads(
              self.socket.recv(4096)
          )
        except Exception as e:
          self.server.display(
              f"{self.username} Exception reading streams: {e}"
          )
          break
        message = cm.get_message()
        # MESSAGE
        if cm.get_type() == ChatMessage.MESSAGE:
          confirmation = self.server.broadcast(
              self.username + ": " + message
          )
          if confirmation is False:
            msg = (
                self.server.notif +
                "Sorry. No such user exists." +
                self.server.notif
            )
            self.write_msg(msg)

        # LOGOUT
        elif cm.get_type() == ChatMessage.LOGOUT:
          self.server.display(
              f"{self.username} disconnected with a LOGOUT message."
          )

          keep_going = False

        # WHOISIN
        elif cm.get_type() == ChatMessage.WHOISIN:
          self.write_msg(
              "List of the users connected at "
              + datetime.now().strftime("%H:%M:%S")
              + "\n"
          )
          i = 1
          for ct in self.server.al:
            self.write_msg(
                f"{i}) {ct.username} since {ct.date}"
            )
            i += 1

      self.server.remove(self.id)
      self.close()

    # cerrar
    def close(self):
      try:
        self.socket.close()
      except:
        pass
    # enviar mensaje
    def write_msg(self, msg):
      try:
        self.socket.send(
            pickle.dumps(msg)
        )
        return True
      except Exception as e:
        self.server.display(
            self.server.notif +
            f"Error sending message to {self.username}" +
            self.server.notif
        )
        self.server.display(str(e))
        return False


# ======================================
# MAIN
# ======================================

def main():

  port_number = 1500
  server = Server(port_number)
  server.start()


if __name__ == "__main__":
  main()
