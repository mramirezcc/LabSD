package Lab03.ejercicio_propuesto.java;

import java.net.*;
import java.io.*;
import java.util.*;

// Cliente del chat
public class Client {

    private String notif = " *** ";

    // Streams
    private ObjectInputStream sInput;
    private ObjectOutputStream sOutput;

    private Socket socket;

    private String server;
    private String username;

    private int port;

    // Constructor
    Client(String server, int port, String username) {
        this.server = server;
        this.port = port;
        this.username = username;
    }

    // Iniciar cliente
    public boolean start() {

        try {
            socket = new Socket(server, port);
        } catch (Exception ec) {
            display("Error connecting to server: " + ec);
            return false;
        }

        String msg = "Connection accepted " +
                socket.getInetAddress() + ":" + socket.getPort();

        display(msg);

        try {
            sInput = new ObjectInputStream(socket.getInputStream());
            sOutput = new ObjectOutputStream(socket.getOutputStream());
        } catch (IOException eIO) {
            display("Exception creating streams: " + eIO);
            return false;
        }

        // Hilo para escuchar mensajes
        new ListenFromServer().start();

        try {
            sOutput.writeObject(username);
        } catch (IOException eIO) {
            display("Exception doing login : " + eIO);
            disconnect();
            return false;
        }

        return true;
    }

    // Mostrar mensajes
    private void display(String msg) {
        System.out.println(msg);
    }

    // Enviar mensaje
    void sendMessage(ChatMessage msg) {
        try {
            sOutput.writeObject(msg);
        } catch (IOException e) {
            display("Exception writing to server: " + e);
        }
    }

    // Desconectar
    private void disconnect() {

        try {
            if (sInput != null)
                sInput.close();
        } catch (Exception e) {
        }

        try {
            if (sOutput != null)
                sOutput.close();
        } catch (Exception e) {
        }

        try {
            if (socket != null)
                socket.close();
        } catch (Exception e) {
        }
    }

    // Main
    public static void main(String[] args) {

        int portNumber = 1500;
        String serverAddress = "localhost";
        String userName = "Anonymous";

        Scanner scan = new Scanner(System.in);

        System.out.println("Enter the username: ");
        userName = scan.nextLine();

        Client client = new Client(serverAddress, portNumber, userName);

        if (!client.start())
            return;

        System.out.println("\nHello.! Welcome to the chatroom.");
        System.out.println("Instructions:");
        System.out.println("1. Write a message to send to all users");
        System.out.println("2. Write '@username message' for private message");
        System.out.println("3. Type WHOISIN to see active users");
        System.out.println("4. Type LOGOUT to exit");

        while (true) {

            System.out.print("> ");

            String msg = scan.nextLine();

            if (msg.equalsIgnoreCase("LOGOUT")) {

                client.sendMessage(
                        new ChatMessage(ChatMessage.LOGOUT, ""));

                break;
            }

            else if (msg.equalsIgnoreCase("WHOISIN")) {

                client.sendMessage(
                        new ChatMessage(ChatMessage.WHOISIN, ""));
            }

            else {

                client.sendMessage(
                        new ChatMessage(ChatMessage.MESSAGE, msg));
            }
        }

        scan.close();

        client.disconnect();
    }

    // Hilo que escucha mensajes del servidor
    class ListenFromServer extends Thread {

        public void run() {

            while (true) {

                try {

                    String msg = (String) sInput.readObject();

                    System.out.println(msg);

                    System.out.print("> ");

                } catch (IOException e) {

                    display(notif +
                            "Server has closed the connection: "
                            + e + notif);

                    break;

                } catch (ClassNotFoundException e2) {
                }
            }
        }
    }
}