import threading

class Consumidor(threading.Thread):
    def __init__(self, cubbyhole, numero):
        super().__init__()
        self.cubbyhole = cubbyhole
        self.numero = numero

    def run(self):
        for i in range(10):
            value = self.cubbyhole.get()
            print(f"Consumidor #{self.numero} obtiene: {value}")