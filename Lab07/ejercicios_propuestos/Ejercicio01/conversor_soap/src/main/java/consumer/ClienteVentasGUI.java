package consumer;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.RenderingHints;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.net.URL;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.xml.namespace.QName;
import javax.xml.ws.Service;
import model.Producto;
import model.VentaResponse;
import service.IVentaSOAP;

public class ClienteVentasGUI extends JFrame {

    // Paleta de colores Premium / Corporativa (Slate & Teal)
    private static final Color BG_APP = new Color(248, 250, 252);
    private static final Color CARD_BG = Color.WHITE;
    private static final Color PRIMARY = new Color(15, 23, 42);
    private static final Color ACCENT = new Color(13, 148, 136);
    private static final Color ACCENT_HOVER = new Color(15, 118, 110);
    private static final Color TEXT_MAIN = new Color(51, 65, 85);
    private static final Color TEXT_MUTED = new Color(148, 163, 184);
    private static final Color BORDER_COLOR = new Color(226, 232, 240);
    private static final Color COLOR_VERDE = new Color(16, 185, 129);
    private static final Color COLOR_ROJO = new Color(239, 68, 68);

    // Componentes del Formulario
    private JTextField txtIdProducto;
    private JTextField txtCantidad;
    private JTextField txtCliente;
    
    private JButton btnBuscar;
    private JButton btnComprar;
    private JButton btnSincronizar;
    
    private JLabel lblStatus;
    private JLabel lblDetalleProducto;
    private JLabel lblResultadoVenta;
    private JPanel panelBoleta;

    private IVentaSOAP proxy;
    private boolean conectado = false;

    public ClienteVentasGUI() {
        initGUI();
    }

    private void conectarServicio() {
        try {
            URL wsdlUrl = new URL("http://localhost:8085/VentaOnlineSOAP?wsdl");
            QName qname = new QName("http://service/", "VentaOnlineService");
            Service service = Service.create(wsdlUrl, qname);
            QName portName = new QName("http://service/", "VentaSOAPPort");
            proxy = service.getPort(portName, IVentaSOAP.class);
            proxy.buscarProducto("PROD01"); // Handshake de prueba
            conectado = true;
        } catch (Exception e) {
            System.out.println("❌ ERROR REAL DE CONEXIÓN SOAP:");
            e.printStackTrace();
            proxy = null;
            conectado = false;
        }
    }

    private void actualizarEstadoUI() {
        lblStatus.setText(conectado ? "● SISTEMA DE VENTAS ONLINE ACTIVO" : "○ ERROR: SERVIDOR DE VENTAS CAÍDO");
        lblStatus.setForeground(conectado ? COLOR_VERDE : COLOR_ROJO);
        btnBuscar.setEnabled(conectado);
        btnComprar.setEnabled(conectado);
    }

    private void initGUI() {
        setTitle("E-Commerce Enterprise Client (SOAP)");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(500, 640);
        setLocationRelativeTo(null);
        setResizable(false);
        getContentPane().setBackground(BG_APP);

        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(BG_APP);

        // 1. HEADER
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(CARD_BG);
        header.setPreferredSize(new Dimension(500, 85));
        header.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, BORDER_COLOR));

        JLabel lblTitulo = new JLabel("Portal de Ventas SOAP", SwingConstants.CENTER);
        lblTitulo.setFont(new Font("Segoe UI", Font.BOLD, 22));
        lblTitulo.setForeground(PRIMARY);
        JLabel lblSubtitulo = new JLabel("SISTEMA DISTRIBUIDO DE FACTURACIÓN E INVENTARIOS", SwingConstants.CENTER);
        lblSubtitulo.setFont(new Font("Segoe UI", Font.BOLD, 9));
        lblSubtitulo.setForeground(TEXT_MUTED);

        JPanel textoPanel = new JPanel(new GridLayout(2, 1, 0, 2));
        textoPanel.setOpaque(false);
        textoPanel.setBorder(new EmptyBorder(20, 0, 20, 0));
        textoPanel.add(lblTitulo);
        textoPanel.add(lblSubtitulo);
        header.add(textoPanel, BorderLayout.CENTER);
        mainPanel.add(header, BorderLayout.NORTH);

        // 2. PANEL CENTRAL (GRIDBAG LAYOUT FORMAL)
        JPanel centro = new JPanel(new GridBagLayout());
        centro.setBackground(BG_APP);
        centro.setBorder(new EmptyBorder(20, 35, 20, 35));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(5, 0, 5, 0);

        // Fila 0: Buscar Producto
        JLabel lblId = new JLabel("CÓDIGO DEL PRODUCTO (Ej: PROD01, PROD02, PROD03)");
        lblId.setFont(new Font("Segoe UI", Font.BOLD, 10));
        lblId.setForeground(TEXT_MAIN);
        gbc.gridx = 0; gbc.gridy = 0; gbc.gridwidth = 2; gbc.weightx = 1.0;
        centro.add(lblId, gbc);

        txtIdProducto = crearTextField();
        gbc.gridy = 1; gbc.gridwidth = 1; gbc.weightx = 0.7;
        centro.add(txtIdProducto, gbc);

        btnBuscar = crearBoton("Buscar");
        gbc.gridx = 1; gbc.gridy = 1; gbc.gridwidth = 1; gbc.weightx = 0.3;
        gbc.insets = new Insets(5, 10, 5, 0);
        centro.add(btnBuscar, gbc);

        // Fila 2: Display de información del Producto
        gbc.insets = new Insets(5, 0, 15, 0);
        lblDetalleProducto = new JLabel("Ingrese un código para consultar stock...", SwingConstants.CENTER);
        lblDetalleProducto.setFont(new Font("Segoe UI", Font.ITALIC, 12));
        lblDetalleProducto.setForeground(TEXT_MAIN);
        gbc.gridx = 0; gbc.gridy = 2; gbc.gridwidth = 2;
        centro.add(lblDetalleProducto, gbc);

        // Fila 3: Datos de la Venta
        JLabel lblCliente = new JLabel("NOMBRE DEL CLIENTE O RAZÓN SOCIAL");
        lblCliente.setFont(new Font("Segoe UI", Font.BOLD, 10));
        lblCliente.setForeground(TEXT_MAIN);
        gbc.gridy = 3; gbc.gridwidth = 2;
        centro.add(lblCliente, gbc);

        txtCliente = crearTextField();
        gbc.gridy = 4;
        centro.add(txtCliente, gbc);

        JLabel lblCantidad = new JLabel("CANTIDAD A ADQUIRIR");
        lblCantidad.setFont(new Font("Segoe UI", Font.BOLD, 10));
        lblCantidad.setForeground(TEXT_MAIN);
        gbc.gridy = 5;
        centro.add(lblCantidad, gbc);

        txtCantidad = crearTextField();
        gbc.gridy = 6;
        centro.add(txtCantidad, gbc);

        // Botón Comprar
        btnComprar = crearBoton("Procesar Transacción Comercial");
        gbc.gridy = 7;
        gbc.insets = new Insets(15, 0, 15, 0);
        centro.add(btnComprar, gbc);

        // Card de Resultados (Boleta)
        panelBoleta = new JPanel(new BorderLayout()) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(CARD_BG);
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 12, 12);
                g2d.setColor(BORDER_COLOR);
                g2d.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 12, 12);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
        panelBoleta.setPreferredSize(new Dimension(400, 100));
        panelBoleta.setOpaque(false);
        
        lblResultadoVenta = new JLabel("<html><center>Esperando operaciones...</center></html>", SwingConstants.CENTER);
        lblResultadoVenta.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        lblResultadoVenta.setForeground(TEXT_MUTED);
        panelBoleta.add(lblResultadoVenta, BorderLayout.CENTER);

        gbc.gridy = 8;
        gbc.insets = new Insets(0, 0, 0, 0);
        centro.add(panelBoleta, gbc);

        mainPanel.add(centro, BorderLayout.CENTER);

        // 3. FOOTER
        JPanel footer = new JPanel(new BorderLayout());
        footer.setBackground(CARD_BG);
        footer.setPreferredSize(new Dimension(500, 40));
        footer.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER_COLOR));

        lblStatus = new JLabel("Conectando con el nodo central...");
        lblStatus.setFont(new Font("Segoe UI", Font.BOLD, 10));
        lblStatus.setBorder(new EmptyBorder(0, 20, 0, 0));
        
        btnSincronizar = new JButton("Sincronizar");
        btnSincronizar.setFont(new Font("Segoe UI", Font.BOLD, 11));
        btnSincronizar.setForeground(ACCENT);
        btnSincronizar.setContentAreaFilled(false);
        btnSincronizar.setBorderPainted(false);
        btnSincronizar.setFocusPainted(false);
        btnSincronizar.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btnSincronizar.setBorder(new EmptyBorder(0, 0, 0, 20));

        footer.add(lblStatus, BorderLayout.WEST);
        footer.add(btnSincronizar, BorderLayout.EAST);
        mainPanel.add(footer, BorderLayout.SOUTH);

        add(mainPanel);

        // Eventos
        btnBuscar.addActionListener(e -> buscarProductoSOAP());
        btnComprar.addActionListener(e -> procesarVentaSOAP());
        btnSincronizar.addActionListener(e -> reconectarServicio());
    }

    // Auxiliares de Diseño Moderno
    private JTextField crearTextField() {
        return new JTextField() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(CARD_BG);
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 8, 8);
                g2d.setColor(hasFocus() ? ACCENT : BORDER_COLOR);
                g2d.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 8, 8);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
    }

    private JButton crearBoton(String texto) {
        JButton btn = new JButton(texto) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                if (!isEnabled()) g2d.setColor(BORDER_COLOR);
                else if (getModel().isPressed() || getModel().isRollover()) g2d.setColor(ACCENT_HOVER);
                else g2d.setColor(ACCENT);
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 8, 8);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
        btn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setContentAreaFilled(false);
        btn.setBorder(new EmptyBorder(10, 15, 10, 15));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        return btn;
    }

    // LÓGICA DE PROXIES ASÍNCRONOS (SwingWorkers)
    private void buscarProductoSOAP() {
        final String id = txtIdProducto.getText().trim().toUpperCase();
        if (id.isEmpty()) return;

        btnBuscar.setEnabled(false);
        lblDetalleProducto.setText("Consultando inventario central...");

        new SwingWorker<Producto, Void>() {
            @Override
            protected Producto doInBackground() {
                return proxy.buscarProducto(id);
            }
            @Override
            protected void done() {
                try {
                    Producto prod = get();
                    if (prod != null) {
                        lblDetalleProducto.setText(String.format("✔ %s  |  Precio: $%.2f  |  Stock: %d uds.", 
                            prod.getNombre(), prod.getPrecio(), prod.getStock()));
                        lblDetalleProducto.setForeground(PRIMARY);
                    } else {
                        lblDetalleProducto.setText("Código no registrado en el sistema.");
                        lblDetalleProducto.setForeground(COLOR_ROJO);
                    }
                } catch (Exception e) {
                    lblDetalleProducto.setText("Fallo de red SOAP.");
                }
                btnBuscar.setEnabled(true);
            }
        }.execute();
    }

    private void procesarVentaSOAP() {
        final String id = txtIdProducto.getText().trim().toUpperCase();
        final String cliente = txtCliente.getText().trim();
        final String cantTexto = txtCantidad.getText().trim();

        if (id.isEmpty() || cliente.isEmpty() || cantTexto.isEmpty()) {
            lblResultadoVenta.setText("⚠️ Complete todos los campos del formulario.");
            lblResultadoVenta.setForeground(COLOR_ROJO);
            return;
        }

        int cant;
        try {
            cant = Integer.parseInt(cantTexto);
        } catch (NumberFormatException e) {
            lblResultadoVenta.setText("⚠️ Cantidad numérica inválida.");
            lblResultadoVenta.setForeground(COLOR_ROJO);
            return;
        }

        final int cantidadFinal = cant;
        btnComprar.setEnabled(false);
        lblResultadoVenta.setText("Generando payload y firmando orden XML...");

        new SwingWorker<VentaResponse, Void>() {
            @Override
            protected VentaResponse doInBackground() {
                return proxy.procesarVenta(id, cantidadFinal, cliente);
            }
            @Override
            protected void done() {
                try {
                    VentaResponse res = get();
                    if (res.isExito()) {
                        lblResultadoVenta.setText(String.format(
                            "<html><center><font color='#10B981'><b>¡VENTA EN LÍNEA COMPLETADA!</b></font><br>" +
                            "<b>Ticket:</b> %s | <b>Total Neto:</b> $%.2f<br>%s</center></html>",
                            res.getCodigoTransaccion(), res.getTotalPagado(), res.getMensaje()
                        ));
                        // Refrescar stock de inmediato
                        buscarProductoSOAP();
                    } else {
                        lblResultadoVenta.setText(String.format(
                            "<html><center><font color='#EF4444'><b>TRANSACCIÓN RECHAZADA</b></font><br><b>Código:</b> %s<br>%s</center></html>",
                            res.getCodigoTransaccion(), res.getMensaje()
                        ));
                    }
                } catch (Exception e) {
                    lblResultadoVenta.setText("Fallo crítico de infraestructura SOAP.");
                }
                btnComprar.setEnabled(true);
            }
        }.execute();
    }

    private void reconectarServicio() {
        btnSincronizar.setEnabled(false);
        lblStatus.setText("Estableciendo comunicación SOAP...");
        lblStatus.setForeground(TEXT_MUTED);

        new SwingWorker<Boolean, Void>() {
            @Override
            protected Boolean doInBackground() {
                conectarServicio();
                return conectado;
            }
            @Override
            protected void done() {
                actualizarEstadoUI();
                btnSincronizar.setEnabled(true);
            }
        }.execute();
    }

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}
        SwingUtilities.invokeLater(() -> {
            ClienteVentasGUI cliente = new ClienteVentasGUI();
            cliente.setVisible(true);
            cliente.reconectarServicio();
        });
    }
}