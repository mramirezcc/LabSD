package Java;

public class Demo {
    public static void main(String[] args) {
        CubbyHole cub = new CubbyHole();
        
        // Creamos los hilos pasándoles el mismo objeto 'cub'
        Consumidor cons = new Consumidor(cub, 1);
        Productor prod = new Productor(cub, 1);

        // Iniciamos los hilos
        prod.start();
        cons.start();
    }
}
