import threading
import time
import random

class Productor(threading.Thread):
    def __init__(self, cubbyhole, numero):
        super().__init__()
        self.cubbyhole = cubbyhole
        self.numero = numero

    def run(self):
        for i in range(10):
            self.cubbyhole.put(i)
            print(f"Productor #{self.numero} pone: {i}")
            # Tiempo de espera aleatorio (0 a 0.1 segundos)
            time.sleep(random.random() * 0.1)