class Cliente:
  def __init__(self, nombre=None, carro_compra=None):
    self.nombre = nombre
    self.carro_compra = carro_compra or []

  def getNombre(self):
    return self.nombre

  def setNombre(self, nombre):
    self.nombre = nombre

  def getCarroCompra(self):
    return self.carro_compra

  def setCarroCompra(self, carro_compra):
    self.carro_compra = carro_compra
