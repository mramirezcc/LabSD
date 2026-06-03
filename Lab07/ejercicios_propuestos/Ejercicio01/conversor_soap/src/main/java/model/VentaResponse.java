package model;

import javax.xml.bind.annotation.XmlType;

@XmlType(name = "VentaResponse", namespace = "http://service/")
public class VentaResponse {
    private boolean exito;
    private String mensaje;
    private String codigoTransaccion;
    private double totalPagado;

    public VentaResponse() {}

    public VentaResponse(boolean exito, String mensaje, String codigoTransaccion, double totalPagado) {
        this.exito = exito;
        this.mensaje = mensaje;
        this.codigoTransaccion = codigoTransaccion;
        this.totalPagado = totalPagado;
    }

    // Getters y Setters
    public boolean isExito() { return exito; }
    public void setExito(boolean exito) { this.exito = exito; }
    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }
    public String getCodigoTransaccion() { return codigoTransaccion; }
    public void setCodigoTransaccion(String codigoTransaccion) { this.codigoTransaccion = codigoTransaccion; }
    public double getTotalPagado() { return totalPagado; }
    public void setTotalPagado(double totalPagado) { this.totalPagado = totalPagado; }
}