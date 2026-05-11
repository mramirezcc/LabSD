package Lab03.ejercicio_propuesto.java;
import java.io.*;
import java.net.*;
import java.text.SimpleDateFormat;
import java.util.*;

// Servidor del chat
public class Server {

    private static int uniqueId;

    private ArrayList<ClientThread> al;

    private SimpleDateFormat sdf;

    private int port;

    private boolean keepGoing;

    private String notif = " *** ";

    // Constructor
    public Server(int port) {

        this.port = port;

        sdf = new SimpleDateFormat("HH:mm:ss");

        al = new ArrayList<ClientThread>();
    }

    // Iniciar servidor
    public void start() {

        keepGoing = true;

        try {

            ServerSocket serverSocket = new ServerSocket(port);

            while (keepGoing) {

                display("Server waiting for Clients on port " + port + ".");

                Socket socket = serverSocket.accept();

                if (!keepGoing)
                    break;

                ClientThread t = new ClientThread(socket);

                al.add(t);

                t.start();
            }

            try {

                serverSocket.close();

                for (int i = 0; i < al.size(); ++i) {

                    ClientThread tc = al.get(i);

                    try {
                        tc.sInput.close();
                        tc.sOutput.close();
                        tc.socket.close();
                    } catch (IOException ioE) {
                    }
                }

            } catch (Exception e) {
                display("Exception closing server: " + e);
            }

        } catch (IOException e) {

            String msg =
                    sdf.format(new Date()) +
                            " Exception on new ServerSocket: " + e;

            display(msg);
        }
    }

    // Mostrar mensaje
    private void display(String msg) {

        String time = sdf.format(new Date()) + " " + msg;

        System.out.println(time);
    }

    // Broadcast
    private synchronized boolean broadcast(String message) {

        String time = sdf.format(new Date());

        String messageLf = time + " " + message + "\n";

        System.out.print(messageLf);

        for (int i = al.size(); --i >= 0;) {

            ClientThread ct = al.get(i);

            if (!ct.writeMsg(messageLf)) {

                al.remove(i);

                display("Disconnected Client "
                        + ct.username +
                        " removed from list.");
            }
        }

        return true;
    }

    // Eliminar cliente
    synchronized void remove(int id) {

        for (int i = 0; i < al.size(); ++i) {

            ClientThread ct = al.get(i);

            if (ct.id == id) {

                al.remove(i);

                break;
            }
        }
    }

    // Main
    public static void main(String[] args) {

        int portNumber = 1500;

        Server server = new Server(portNumber);

        server.start();
    }

    // Hilo por cliente
    class ClientThread extends Thread {

        Socket socket;

        ObjectInputStream sInput;
        ObjectOutputStream sOutput;

        int id;

        String username;

        ChatMessage cm;

        String date;

        // Constructor
        ClientThread(Socket socket) {

            id = ++uniqueId;

            this.socket = socket;

            System.out.println(
                    "Thread trying to create Object Input/Output Streams");

            try {

                sOutput =
                        new ObjectOutputStream(socket.getOutputStream());

                sInput =
                        new ObjectInputStream(socket.getInputStream());

                username = (String) sInput.readObject();

                broadcast(notif +
                        username +
                        " has joined the chat room." +
                        notif);

            } catch (IOException e) {

                display("Exception creating streams: " + e);

                return;

            } catch (ClassNotFoundException e) {
            }

            date = new Date().toString();
        }

        public void run() {

            boolean keepGoing = true;

            while (keepGoing) {

                try {

                    cm = (ChatMessage) sInput.readObject();

                } catch (IOException e) {

                    display(username +
                            " Exception reading Streams: " + e);

                    break;

                } catch (ClassNotFoundException e2) {

                    break;
                }

                String message = cm.getMessage();

                switch (cm.getType()) {

                    case ChatMessage.MESSAGE:

                        broadcast(username + ": " + message);

                        break;

                    case ChatMessage.LOGOUT:

                        display(username +
                                " disconnected with a LOGOUT message.");

                        keepGoing = false;

                        break;

                    case ChatMessage.WHOISIN:

                        writeMsg("List of the users connected at "
                                + sdf.format(new Date()));

                        for (int i = 0; i < al.size(); ++i) {

                            ClientThread ct = al.get(i);

                            writeMsg((i + 1) + ") "
                                    + ct.username
                                    + " since "
                                    + ct.date);
                        }

                        break;
                }
            }

            remove(id);

            close();
        }

        // Cerrar conexiones
        private void close() {

            try {
                if (sOutput != null)
                    sOutput.close();
            } catch (Exception e) {
            }

            try {
                if (sInput != null)
                    sInput.close();
            } catch (Exception e) {
            }

            try {
                if (socket != null)
                    socket.close();
            } catch (Exception e) {
            }
        }

        // Enviar mensaje
        private boolean writeMsg(String msg) {

            if (!socket.isConnected()) {

                close();

                return false;
            }

            try {

                sOutput.writeObject(msg);

            } catch (IOException e) {

                display(notif +
                        "Error sending message to "
                        + username +
                        notif);

                display(e.toString());
            }

            return true;
        }
    }
}