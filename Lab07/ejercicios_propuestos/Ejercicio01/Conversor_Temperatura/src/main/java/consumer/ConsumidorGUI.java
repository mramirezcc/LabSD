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
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.xml.namespace.QName;
import javax.xml.ws.Service;
import service.IConversorSOAP;

public class ConsumidorGUI extends JFrame {

    // Nueva paleta de colores empresarial / moderna (Slate & Teal)
    private static final Color BG_APP = new Color(248, 250, 252);         // Fondo general ultra-claro (Slate 50)
    private static final Color CARD_BG = Color.WHITE;                      // Fondo de componentes principales
    private static final Color PRIMARY = new Color(15, 23, 42);            // Azul pizarra oscuro (Slate 900)
    private static final Color ACCENT = new Color(13, 148, 136);           // Teal corporativo moderno (Teal 600)
    private static final Color ACCENT_HOVER = new Color(15, 118, 110);     // Teal oscuro para hover
    private static final Color TEXT_MAIN = new Color(51, 65, 85);          // Texto principal (Slate 700)
    private static final Color TEXT_MUTED = new Color(148, 163, 184);      // Texto secundario / deshabilitado
    private static final Color BORDER_COLOR = new Color(226, 232, 240);    // Líneas divisorias suaves (Slate 200)
    
    private static final Color COLOR_VERDE = new Color(16, 185, 129);      // Éxito (Emerald 500)
    private static final Color COLOR_ROJO = new Color(239, 68, 68);        // Error (Red 500)
    private JPanel panelResultado;
    private JTextField txtTemperatura;
    private JRadioButton rbCtoF;
    private JRadioButton rbFtoC;
    private JButton btnConvertir;
    private JButton btnReconectar;
    private JLabel lblResultado;
    private JLabel lblStatus;
    private IConversorSOAP proxy;
    private boolean conectado = false;

    public ConsumidorGUI() {
        initGUI();
        ejecutarConexionInicial();
    }

    private void ejecutarConexionInicial() {
        new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() {
                conectarServicio();
                return null;
            }
            @Override
            protected void done() {
                actualizarEstadoUI();
            }
        }.execute();
    }

    private void conectarServicio() {
        try {
            URL wsdlUrl = new URL("http://localhost:8080/ConversorSOAP?wsdl");
            QName qname = new QName("http://service/", "ConversorTemperaturaService");
            Service service = Service.create(wsdlUrl, qname);
            QName portName = new QName("http://service/", "ConversorSOAPPort");
            proxy = service.getPort(portName, IConversorSOAP.class);
            proxy.cToF(0); // Test de comunicación
            conectado = true;
        } catch (Exception e) {
            proxy = null;
            conectado = false;
        }
    }

    private void actualizarEstadoUI() {
        lblStatus.setText(getStatusTexto());
        lblStatus.setForeground(conectado ? COLOR_VERDE : COLOR_ROJO);
        btnConvertir.setEnabled(conectado);
        btnConvertir.repaint();
    }

    private void initGUI() {
        setTitle("Enterprise Temperature Converter");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(460, 520);
        setLocationRelativeTo(null);
        setResizable(false);
        getContentPane().setBackground(BG_APP);

        JPanel mainPanel = new JPanel(new BorderLayout(0, 0));
        mainPanel.setBackground(BG_APP);

        mainPanel.add(crearHeader(), BorderLayout.NORTH);
        mainPanel.add(crearPanelCentral(), BorderLayout.CENTER);
        mainPanel.add(crearFooter(), BorderLayout.SOUTH);

        add(mainPanel);
    }

    private JPanel crearHeader() {
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(CARD_BG);
        header.setPreferredSize(new Dimension(460, 85));
        header.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, BORDER_COLOR));

        JLabel lblTitulo = new JLabel("Conversor de Temperatura", SwingConstants.CENTER);
        lblTitulo.setFont(new Font("Segoe UI", Font.BOLD, 20));
        lblTitulo.setForeground(PRIMARY);

        JLabel lblSubtitulo = new JLabel("MÓDULO DE CLIENTE SOAP  •  JAX-WS ENTERPRISE", SwingConstants.CENTER);
        lblSubtitulo.setFont(new Font("Segoe UI", Font.BOLD, 10));
        lblSubtitulo.setForeground(TEXT_MUTED);

        JPanel textoPanel = new JPanel(new GridLayout(2, 1, 0, 0));
        textoPanel.setOpaque(false);
        textoPanel.setBorder(new EmptyBorder(22, 0, 22, 0));
        textoPanel.add(lblTitulo);
        textoPanel.add(lblSubtitulo);

        header.add(textoPanel, BorderLayout.CENTER);
        return header;
    }

    private JPanel crearPanelCentral() {
        JPanel panel = new JPanel(new GridBagLayout());
        panel.setBackground(BG_APP);
        panel.setBorder(new EmptyBorder(25, 35, 25, 35));
        
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.gridwidth = 2;
        gbc.weightx = 1.0;

        // 1. Etiqueta de Instrucción
        JLabel lblInstruccion = new JLabel("VALOR DE ENTRADA");
        lblInstruccion.setFont(new Font("Segoe UI", Font.BOLD, 11));
        lblInstruccion.setForeground(TEXT_MAIN);
        gbc.gridy = 0;
        gbc.insets = new Insets(0, 0, 6, 0);
        panel.add(lblInstruccion, gbc);

        // 2. Input de Temperatura Estilizado
        txtTemperatura = new JTextField() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(CARD_BG);
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 12, 12);
                g2d.setColor(hasFocus() ? ACCENT : BORDER_COLOR);
                g2d.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 12, 12);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
        txtTemperatura.setFont(new Font("Segoe UI", Font.PLAIN, 24));
        txtTemperatura.setHorizontalAlignment(SwingConstants.CENTER);
        txtTemperatura.setOpaque(false);
        txtTemperatura.setBorder(new EmptyBorder(10, 15, 10, 15));
        txtTemperatura.setForeground(PRIMARY);
        txtTemperatura.setCaretColor(ACCENT);
        gbc.gridy = 1;
        gbc.insets = new Insets(0, 0, 20, 0);
        panel.add(txtTemperatura, gbc);

        // 3. Etiqueta Tipo de Conversión
        JLabel lblTipo = new JLabel("DIRECCIÓN DE LA CONVERSIÓN");
        lblTipo.setFont(new Font("Segoe UI", Font.BOLD, 11));
        lblTipo.setForeground(TEXT_MAIN);
        gbc.gridy = 2;
        gbc.insets = new Insets(0, 0, 8, 0);
        panel.add(lblTipo, gbc);

        // 4. Panel de Radio Buttons Modernos
        JPanel radioPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 25, 0));
        radioPanel.setOpaque(false);

        rbCtoF = new JRadioButton("Celsius a Fahrenheit");
        rbCtoF.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        rbCtoF.setForeground(TEXT_MAIN);
        rbCtoF.setOpaque(false);
        rbCtoF.setFocusPainted(false);
        rbCtoF.setSelected(true);

        rbFtoC = new JRadioButton("Fahrenheit a Celsius");
        rbFtoC.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        rbFtoC.setForeground(TEXT_MAIN);
        rbFtoC.setOpaque(false);
        rbFtoC.setFocusPainted(false);

        ButtonGroup grupo = new ButtonGroup();
        grupo.add(rbCtoF);
        grupo.add(rbFtoC);

        radioPanel.add(rbCtoF);
        radioPanel.add(rbFtoC);

        gbc.gridy = 3;
        gbc.insets = new Insets(0, 0, 25, 0);
        panel.add(radioPanel, gbc);

        // 5. Botón de Acción Estilo Flat / Premium
        btnConvertir = new JButton("Procesar Conversión") {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                if (!isEnabled()) {
                    g2d.setColor(BORDER_COLOR);
                } else if (getModel().isPressed()) {
                    g2d.setColor(ACCENT_HOVER);
                } else if (getModel().isRollover()) {
                    g2d.setColor(ACCENT_HOVER);
                } else {
                    g2d.setColor(ACCENT);
                }
                
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 12, 12);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
        btnConvertir.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btnConvertir.setForeground(Color.WHITE);
        btnConvertir.setFocusPainted(false);
        btnConvertir.setContentAreaFilled(false);
        btnConvertir.setBorder(new EmptyBorder(14, 0, 14, 0));
        btnConvertir.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btnConvertir.addActionListener(e -> realizarConversion());

        txtTemperatura.addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                    realizarConversion();
                }
            }
        });

        gbc.gridy = 4;
        gbc.insets = new Insets(0, 0, 25, 0);
        panel.add(btnConvertir, gbc);

        // 6. Card de Resultados Limpia
        panelResultado = new JPanel(new BorderLayout()) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(CARD_BG);
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 16, 16);
                g2d.setColor(BORDER_COLOR);
                g2d.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 16, 16);
                g2d.dispose();
                super.paintComponent(g);
            }
        };
        panelResultado.setPreferredSize(new Dimension(390, 75));
        panelResultado.setOpaque(false);

        lblResultado = new JLabel("Sistemas Listos", SwingConstants.CENTER);
        lblResultado.setFont(new Font("Segoe UI", Font.BOLD, 20));
        lblResultado.setForeground(TEXT_MUTED);
        panelResultado.add(lblResultado, BorderLayout.CENTER);

        gbc.gridy = 5;
        gbc.insets = new Insets(0, 0, 5, 0);
        panel.add(panelResultado, gbc);

        return panel;
    }

    private JPanel crearFooter() {
        JPanel footer = new JPanel(new BorderLayout());
        footer.setBackground(CARD_BG);
        footer.setPreferredSize(new Dimension(460, 40));
        footer.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER_COLOR));

        lblStatus = new JLabel(getStatusTexto());
        lblStatus.setFont(new Font("Segoe UI", Font.BOLD, 11));
        lblStatus.setForeground(TEXT_MUTED);
        lblStatus.setBorder(new EmptyBorder(0, 20, 0, 0));

        btnReconectar = new JButton("Sincronizar");
        btnReconectar.setFont(new Font("Segoe UI", Font.BOLD, 11));
        btnReconectar.setForeground(ACCENT);
        btnReconectar.setContentAreaFilled(false);
        btnReconectar.setBorderPainted(false);
        btnReconectar.setFocusPainted(false);
        btnReconectar.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btnReconectar.setBorder(new EmptyBorder(0, 0, 0, 20));
        btnReconectar.addActionListener(e -> reconectar());

        footer.add(lblStatus, BorderLayout.WEST);
        footer.add(btnReconectar, BorderLayout.EAST);
        return footer;
    }

    private void realizarConversion() {
        if (!conectado || proxy == null) {
            mostrarError("Error: Sin enlace activo con el servidor.");
            return;
        }

        String texto = txtTemperatura.getText().trim();
        if (texto.isEmpty()) {
            mostrarError("Aviso: El campo está vacío.");
            return;
        }

        double valorParseado;
        try {
            valorParseado = Double.parseDouble(texto);
        } catch (NumberFormatException e) {
            mostrarError("Error: Formato numérico inválido.");
            return;
        }

        final double valorFinal = valorParseado;
        btnConvertir.setEnabled(false);
        btnConvertir.setText("Procesando petición...");
        lblResultado.setText("Consultando nodo SOAP...");
        lblResultado.setForeground(TEXT_MUTED);

        new SwingWorker<String, Void>() {
            @Override
            protected String doInBackground() throws Exception {
                boolean esCtoF = rbCtoF.isSelected();
                double resultado = esCtoF ? proxy.cToF(valorFinal) : proxy.fToC(valorFinal);

                String simboloOrigen = esCtoF ? "°C" : "°F";
                String simboloDestino = esCtoF ? "°F" : "°C";
                return String.format("%.2f %s  =  %.2f %s", valorFinal, simboloOrigen, resultado, simboloDestino);
            }

            @Override
            protected void done() {
                try {
                    lblResultado.setText(get());
                    lblResultado.setForeground(PRIMARY);
                } catch (Exception e) {
                    lblResultado.setText("Fallo de infraestructura SOAP");
                    lblResultado.setForeground(COLOR_ROJO);
                    conectado = false;
                    proxy = null;
                    actualizarEstadoUI();
                }
                btnConvertir.setEnabled(true);
                btnConvertir.setText("Procesar Conversión");
                txtTemperatura.selectAll();
                txtTemperatura.requestFocus();
            }
        }.execute();
    }

    private void reconectar() {
        btnReconectar.setEnabled(false);
        lblStatus.setText("Estableciendo Handshake...");
        lblStatus.setForeground(TEXT_MUTED);

        new SwingWorker<Boolean, Void>() {
            @Override
            protected Boolean doInBackground() {
                conectarServicio();
                return conectado;
            }

            @Override
            protected void done() {
                try {
                    conectado = get();
                } catch (Exception e) {
                    conectado = false;
                }
                actualizarEstadoUI();
                btnReconectar.setEnabled(true);
                if (conectado) {
                    lblResultado.setText("Sistemas Listos");
                    lblResultado.setForeground(TEXT_MUTED);
                    txtTemperatura.requestFocus();
                }
            }
        }.execute();
    }

    private void mostrarError(String mensaje) {
        lblResultado.setText(mensaje);
        lblResultado.setForeground(COLOR_ROJO);
        txtTemperatura.selectAll();
        txtTemperatura.requestFocus();
    }

    private String getStatusTexto() {
        return conectado 
            ? "● ENLACE ACTIVO (SOAP Server: 8080)" 
            : "○ NODO DESCONECTADO";
    }

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        SwingUtilities.invokeLater(() -> new ConsumidorGUI().setVisible(true));
    }
}