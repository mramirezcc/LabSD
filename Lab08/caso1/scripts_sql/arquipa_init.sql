DROP TABLE IF EXISTS inventario;

CREATE TABLE inventario(
    id SERIAL PRIMARY KEY,
    producto VARCHAR(100),
    stock INTEGER
);

INSERT INTO inventario(producto, stock) VALUES('Paracetamol', 100);