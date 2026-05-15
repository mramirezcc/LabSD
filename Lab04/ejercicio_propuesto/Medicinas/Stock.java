
package Medicinas;

import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.HashMap;

public class Stock extends UnicastRemoteObject implements StockInterface {

    private HashMap<String, MedicineInterface> medicines = new HashMap<>();

    public Stock() throws RemoteException {
        super();
        
    }

    public void addMedicine(String name, float price, int stock) throws Exception {

        medicines.put(name, new Medicine(name, price, stock));
    }

    @Override
    public MedicineInterface buyMedicine(String name, int amount) throws Exception {

        MedicineInterface aux = medicines.get(name);

        if (aux == null) {
            throw new Exception("Impossible to find " + name);
        }

        MedicineInterface element = (MedicineInterface) aux.getMedicine(amount);

        return element;
    }

    @Override
    public HashMap<String, MedicineInterface> getStockProducts() throws Exception {

        return this.medicines;
    }
}