import time


class Cajera:
  def __init__(self, nombre=None):
    self.nombre = nombre

  def getNombre(self):
    return self.nombre

  def setNombre(self, nombre):
    self.nombre = nombre

  def procesarCompra(self, cliente, timeStamp):
    print(f"La cajera {self.nombre} COMIENZA A PROCESAR LA COMPRA DEL CLIENTE {cliente.getNombre()} EN EL TIEMPO: {self._elapsed_seconds(timeStamp)}seg")

    for i, segundos in enumerate(cliente.getCarroCompra()):
      self._esperar_x_segundos(segundos)
      print(
          f"Procesado el producto {i + 1} -> Tiempo: {self._elapsed_seconds(timeStamp)}seg")

    print(f"La cajera {self.nombre} HA TERMINADO DE PROCESAR {cliente.getNombre()} EN EL TIEMPO: {self._elapsed_seconds(timeStamp)}seg")

  def _esperar_x_segundos(self, segundos):
    time.sleep(segundos)

  def _elapsed_seconds(self, time_stamp):
    return int((time.time() * 1000 - time_stamp) / 1000)
