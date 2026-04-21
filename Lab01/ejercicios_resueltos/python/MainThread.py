import time

from CajeraThread import CajeraThread
from Cliente import Cliente


if __name__ == "__main__":
  cliente1 = Cliente("Cliente 1", [2, 2, 1, 5, 2, 3])
  cliente2 = Cliente("Cliente 2", [1, 3, 5, 1, 1])

  initialTime = time.time() * 1000

  cajera1 = CajeraThread("Cajera 1", cliente1, initialTime)
  cajera2 = CajeraThread("Cajera 2", cliente2, initialTime)

  cajera1.start()
  cajera2.start()
