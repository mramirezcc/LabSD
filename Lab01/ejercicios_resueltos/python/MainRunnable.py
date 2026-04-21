import threading
import time

from Cajera import Cajera
from Cliente import Cliente


class MainRunnable:
  def __init__(self, cliente, cajera, initialTime):
    self.cliente = cliente
    self.cajera = cajera
    self.initialTime = initialTime

  def run(self):
    self.cajera.procesarCompra(self.cliente, self.initialTime)


if __name__ == "__main__":
  cliente1 = Cliente("Cliente 1", [2, 2, 1, 5, 2, 3])
  cliente2 = Cliente("Cliente 2", [1, 3, 5, 1, 1])
  cajera1 = Cajera("Cajera 1")
  cajera2 = Cajera("Cajera 2")

  initialTime = time.time() * 1000

  proceso1 = MainRunnable(cliente1, cajera1, initialTime)
  proceso2 = MainRunnable(cliente2, cajera2, initialTime)

  t1 = threading.Thread(target=proceso1.run)
  t2 = threading.Thread(target=proceso2.run)

  t1.start()
  t2.start()
