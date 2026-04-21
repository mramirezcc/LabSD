import time

from Cajera import Cajera
from Cliente import Cliente


if __name__ == "__main__":
  cliente1 = Cliente("Cliente 1", [2, 2, 1, 5, 2, 3])
  cliente2 = Cliente("Cliente 2", [1, 3, 5, 1, 1])
  cajera1 = Cajera("Cajera 1")
  cajera2 = Cajera("Cajera 2")

  initialTime = time.time() * 1000
  cajera1.procesarCompra(cliente1, initialTime)
  cajera2.procesarCompra(cliente2, initialTime)
