package Lab03.ejercicio_propuesto.java;


import java.io.*;

/*
 * This class defines the different type of messages that will be exchanged between the
 * Clients and the Server.
 */
public class ChatMessage implements Serializable {

    // Tipos de mensajes
    static final int WHOISIN = 0;
    static final int MESSAGE = 1;
    static final int LOGOUT = 2;

    private int type;
    private String message;

    // Constructor
    ChatMessage(int type, String message) {
        this.type = type;
        this.message = message;
    }

    int getType() {
        return type;
    }

    String getMessage() {
        return message;
    }
}