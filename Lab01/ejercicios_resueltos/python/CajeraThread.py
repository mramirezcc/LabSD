import threading
import time

class CajeraThread(threading.Thread):
  def __init__(self, nombre=None, cliente=None, initialTime=None):
    super().__init__()
    self.nombre = nombre
    self.cliente = cliente
    self.initialTime = initialTime

  def getNombre(self):
    return self.nombre

  def setNombre(self, nombre):
    self.nombre = nombre

  def getInitialTime(self):
    return self.initialTime

  def setInitialTime(self, initialTime):
    self.initialTime = initialTime

  def getCliente(self):
    return self.cliente

  def setCliente(self, cliente):
    self.cliente = cliente

  def run(self):
    assert self.cliente is not None, "Cliente no asignado"
    print(f"La cajera {self.nombre} COMIENZA A PROCESAR LA COMPRA DEL CLIENTE {self.cliente.getNombre()} EN EL TIEMPO: {self._elapsed_seconds()}seg")

    for i, segundos in enumerate(self.cliente.getCarroCompra()):
      self._esperar_x_segundos(segundos)
      print(
          f"Procesado el producto {i + 1} del cliente {self.cliente.getNombre()} -> Tiempo: {self._elapsed_seconds()}seg")

    print(f"La cajera {self.nombre} HA TERMINADO DE PROCESAR {self.cliente.getNombre()} EN EL TIEMPO: {self._elapsed_seconds()}seg")

  def _esperar_x_segundos(self, segundos):
    time.sleep(segundos)

  def _elapsed_seconds(self):
      if self.initialTime is None:
          return 0
      return int((time.time() * 1000 - self.initialTime) / 1000)
