from cubbyhole import CubbyHole
from productor import Productor
from consumidor import Consumidor

if __name__ == "__main__":
    cub = CubbyHole()
    
    prod = Productor(cub, 1)
    cons = Consumidor(cub, 1)
    
    prod.start()
    cons.start()
    
    prod.join()
    cons.join()
    print("Simulación terminada.")