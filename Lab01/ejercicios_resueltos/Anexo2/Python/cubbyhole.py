import threading

class CubbyHole:
    def __init__(self):
        self.contents = 0
        self.available = False
        self.condition = threading.Condition()

    def get(self):
        with self.condition:
            while not self.available:
                self.condition.wait()  # Espera a que el productor ponga algo
            
            self.available = False
            self.condition.notify_all()  # Avisa al productor
            return self.contents

    def put(self, value):
        with self.condition:
            while self.available:
                self.condition.wait()  # Espera a que el consumidor saque el dato
            
            self.contents = value
            self.available = True
            self.condition.notify_all()  # Avisa al consumidor