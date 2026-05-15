package gui_final;

import ejercicio_2.CreditCardInterface;
import ejercicio_3.CurrencyConverterInterface;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.List;
import javax.swing.text.AbstractDocument;
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.DocumentFilter;

public class FinancialGUI extends JFrame {

    // Colores Modernos - Paleta más elegante
    private final Color PRIMARY_NAV = new Color(15, 23, 42); // Slate 900
    private final Color NAV_HOVER = new Color(30, 41, 59); // Slate 800
    private final Color ACCENT_BLUE = new Color(37, 99, 235); // Blue 600
    private final Color ACCENT_HOVER = new Color(29, 78, 216); // Blue 700
    private final Color BG_LIGHT = new Color(248, 250, 252); // Slate 50
    private final Color CARD_BG = Color.WHITE;
    private final Color TEXT_DARK = new Color(15, 23, 42);
    private final Color TEXT_MUTED = new Color(100, 116, 139);

    private CardLayout cardLayout;
    private JPanel mainContent;

    // Referencias RMI
    private CreditCardInterface atmService;
    private CurrencyConverterInterface converterService;
    private String currentCard = "";

    public FinancialGUI() {
        conectarRMI();
        initWindow();
        initComponents();
    }

    private void conectarRMI() {
        try {
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            // Intentamos conectar a ambos servicios
            try {
                atmService = (CreditCardInterface) registry.lookup("ServicioTarjetas");
            } catch (Exception e) {
            }
            try {
                converterService = (CurrencyConverterInterface) registry.lookup("ServicioConversor");
            } catch (Exception e) {
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this,
                    "Error conectando a los servidores RMI. Asegúrate de que estén encendidos.", "Error de Conexión",
                    JOptionPane.ERROR_MESSAGE);
        }
    }

    private void initWindow() {
        setTitle("Financial Suite Premium - Banco 4500");
        setSize(1050, 700);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());
        getContentPane().setBackground(BG_LIGHT);
    }

    private void initComponents() {
        // Panel Lateral (Navegación)
        JPanel sidebar = new JPanel();
        sidebar.setBackground(PRIMARY_NAV);
        sidebar.setPreferredSize(new Dimension(280, 700));
        sidebar.setLayout(new FlowLayout(FlowLayout.CENTER, 0, 20));
        sidebar.setBorder(new EmptyBorder(40, 20, 20, 20));

        JLabel title = new JLabel(
                "<html><center>FINANCIAL<br><span style='color:#3b82f6'>SUITE</span></center></html>");
        title.setForeground(Color.WHITE);
        title.setFont(new Font("Segoe UI", Font.BOLD, 28));
        title.setPreferredSize(new Dimension(240, 80));
        sidebar.add(title);

        JPanel navGroup = new JPanel(new GridLayout(4, 1, 0, 15));
        navGroup.setOpaque(false);
        navGroup.setPreferredSize(new Dimension(240, 300));

        JButton btnATM = createNavButton("Cajero Automático");
        JButton btnConv = createNavButton("Conversor de Divisas");

        navGroup.add(btnATM);
        navGroup.add(btnConv);
        sidebar.add(navGroup);

        // Panel Principal (Contenido Variable)
        cardLayout = new CardLayout();
        mainContent = new JPanel(cardLayout);
        mainContent.setBackground(BG_LIGHT);

        mainContent.add(createATMPanel(), "ATM");
        mainContent.add(createConverterPanel(), "CONV");

        add(sidebar, BorderLayout.WEST);
        add(mainContent, BorderLayout.CENTER);

        // Eventos
        btnATM.addActionListener(e -> cardLayout.show(mainContent, "ATM"));
        btnConv.addActionListener(e -> cardLayout.show(mainContent, "CONV"));
    }

    private JPanel createHeader(String titleText, String subtitleText) {
        JPanel headerPanel = new JPanel();
        headerPanel.setLayout(new BoxLayout(headerPanel, BoxLayout.Y_AXIS));
        headerPanel.setOpaque(false);
        headerPanel.setBounds(50, 40, 600, 80);

        JLabel title = new JLabel(titleText);
        title.setFont(new Font("Segoe UI", Font.BOLD, 32));
        title.setForeground(TEXT_DARK);

        JLabel subtitle = new JLabel(subtitleText);
        subtitle.setFont(new Font("Segoe UI", Font.PLAIN, 16));
        subtitle.setForeground(TEXT_MUTED);

        headerPanel.add(title);
        headerPanel.add(Box.createVerticalStrut(5));
        headerPanel.add(subtitle);
        return headerPanel;
    }

    // DISEÑO DEL PANEL DE CAJERO
    private JPanel createATMPanel() {
        CardLayout atmLayout = new CardLayout();
        JPanel atmRoot = new JPanel(atmLayout);
        atmRoot.setBackground(BG_LIGHT);

        // PANEL DE LOGIN
        JPanel loginPanel = new JPanel(null);
        loginPanel.setBackground(BG_LIGHT);
        loginPanel.add(createHeader("Cajero Automático", "Gestione sus cuentas de forma segura y rápida."));

        // Tarjeta Panel
        JPanel cardPanel = new JPanel(null);
        cardPanel.setBackground(CARD_BG);
        cardPanel.setBounds(50, 140, 650, 120);
        cardPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(226, 232, 240), 1, true),
                BorderFactory.createEmptyBorder(20, 20, 20, 20)));

        JLabel lblCard = new JLabel("Número de Tarjeta:");
        lblCard.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblCard.setForeground(TEXT_DARK);
        lblCard.setBounds(25, 20, 200, 30);
        cardPanel.add(lblCard);

        JTextField txtCard = new JTextField() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                if (getText().isEmpty()) {
                    Graphics2D g2 = (Graphics2D) g.create();
                    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
                    g2.setColor(new Color(156, 163, 175));
                    g2.setFont(getFont().deriveFont(Font.ITALIC));
                    int y = (getHeight() - g.getFontMetrics().getHeight()) / 2 + g.getFontMetrics().getAscent();
                    g2.drawString("4500-XXXX-XXXX-XXXX", getInsets().left, y);
                    g2.dispose();
                }
            }
        };
        ((AbstractDocument) txtCard.getDocument()).setDocumentFilter(new DocumentFilter() {
            @Override
            public void replace(FilterBypass fb, int offset, int length, String text, AttributeSet attrs)
                    throws BadLocationException {
                formatAndReplace(fb, offset, length, text, attrs);
            }

            @Override
            public void remove(FilterBypass fb, int offset, int length) throws BadLocationException {
                formatAndReplace(fb, offset, length, "", null);
            }

            @Override
            public void insertString(FilterBypass fb, int offset, String string, AttributeSet attr)
                    throws BadLocationException {
                formatAndReplace(fb, offset, 0, string, attr);
            }

            private void formatAndReplace(FilterBypass fb, int offset, int length, String text, AttributeSet attrs)
                    throws BadLocationException {
                String currentText = fb.getDocument().getText(0, fb.getDocument().getLength());
                String newText = currentText.substring(0, offset) + text + currentText.substring(offset + length);
                String digitsOnly = newText.replaceAll("[^\\d]", "");
                if (digitsOnly.length() > 16)
                    digitsOnly = digitsOnly.substring(0, 16);

                StringBuilder formatted = new StringBuilder();
                for (int i = 0; i < digitsOnly.length(); i++) {
                    if (i > 0 && i % 4 == 0)
                        formatted.append("-");
                    formatted.append(digitsOnly.charAt(i));
                }
                fb.replace(0, fb.getDocument().getLength(), formatted.toString(), attrs);
            }
        });
        txtCard.setFont(new Font("Monospaced", Font.PLAIN, 16));
        txtCard.setBounds(25, 55, 300, 45);
        txtCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(203, 213, 225), 1, true),
                BorderFactory.createEmptyBorder(5, 15, 5, 15)));
        cardPanel.add(txtCard);

        JButton btnLogin = createCustomButton("INGRESAR", new Color(30, 64, 175), new Color(30, 58, 138));
        btnLogin.setBounds(350, 55, 150, 45);
        cardPanel.add(btnLogin);
        loginPanel.add(cardPanel);

        // PANEL DE DASHBOARD
        JPanel dashboardPanel = new JPanel(null);
        dashboardPanel.setBackground(BG_LIGHT);
        dashboardPanel.add(createHeader("Operaciones", "Seleccione la operación a realizar."));

        JButton btnLogout = createCustomButton("SALIR", new Color(225, 29, 72), new Color(190, 18, 60));
        btnLogout.setBounds(550, 40, 100, 40);
        dashboardPanel.add(btnLogout);

        JPanel ops = new JPanel(new GridLayout(2, 2, 25, 25));
        ops.setBounds(50, 140, 650, 300);
        ops.setOpaque(false);

        JButton b1 = createOpButton("CONSULTAR SALDO", "💰");
        JButton b2 = createOpButton("PAGO EN LÍNEA", "🌐");
        JButton b3 = createOpButton("ABONAR", "📥");
        JButton b4 = createOpButton("HISTORIAL", "📜");

        ops.add(b1);
        ops.add(b2);
        ops.add(b3);
        ops.add(b4);
        dashboardPanel.add(ops);

        atmRoot.add(loginPanel, "LOGIN");
        atmRoot.add(dashboardPanel, "DASHBOARD");

        // Lógica Login
        btnLogin.addActionListener(e -> {
            if (txtCard.getText().isEmpty()) {
                JOptionPane.showMessageDialog(loginPanel, "Por favor ingrese un número de tarjeta.", "Aviso",
                        JOptionPane.WARNING_MESSAGE);
                return;
            }
            try {
                String res = atmService.validarORegistrarTarjeta(txtCard.getText());
                if (res.equals("OK")) {
                    currentCard = txtCard.getText();
                    atmLayout.show(atmRoot, "DASHBOARD");
                    JOptionPane.showMessageDialog(dashboardPanel,
                            "Autenticación exitosa. Límite de crédito: $" + atmService.consultarLimite(currentCard),
                            "Bienvenido", JOptionPane.INFORMATION_MESSAGE);
                } else {
                    JOptionPane.showMessageDialog(loginPanel, "Error: " + res, "Acceso Denegado",
                            JOptionPane.ERROR_MESSAGE);
                }
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(loginPanel,
                        "No se pudo conectar al servicio RMI. ¿Está encendido el servidor?",
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        });

        btnLogout.addActionListener(e -> {
            currentCard = "";
            txtCard.setText("");
            atmLayout.show(atmRoot, "LOGIN");
        });

        b1.addActionListener(e -> {
            try {
                double saldo = atmService.consultarSaldo(currentCard);
                JOptionPane.showMessageDialog(dashboardPanel, "Saldo Disponible: $" + String.format("%.2f", saldo),
                        "Consulta de Saldo", JOptionPane.INFORMATION_MESSAGE);
            } catch (Exception ex) {
            }
        });

        b2.addActionListener(e -> {
            JTextField txtDesc = new JTextField();
            JTextField txtMonto = new JTextField();
            Object[] message = {
                    "Descripción del pago:", txtDesc,
                    "Monto a pagar:", txtMonto
            };
            int option = JOptionPane.showConfirmDialog(dashboardPanel, message, "Pago en Línea",
                    JOptionPane.OK_CANCEL_OPTION);
            if (option == JOptionPane.OK_OPTION) {
                try {
                    double monto = Double.parseDouble(txtMonto.getText());
                    String desc = txtDesc.getText().isEmpty() ? "Compra por internet" : txtDesc.getText();
                    boolean exito = atmService.realizarOperacion(currentCard, monto, "Pago: " + desc);
                    if (exito) {
                        JOptionPane.showMessageDialog(dashboardPanel,
                                "Pago realizado con éxito.\nNuevo saldo: $"
                                        + String.format("%.2f", atmService.consultarSaldo(currentCard)),
                                "Éxito", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(dashboardPanel,
                                "No se pudo realizar el pago. Verifique su saldo disponible.", "Error",
                                JOptionPane.ERROR_MESSAGE);
                    }
                } catch (NumberFormatException ex) {
                    JOptionPane.showMessageDialog(dashboardPanel, "Monto inválido.", "Error",
                            JOptionPane.ERROR_MESSAGE);
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(dashboardPanel, "Error de conexión.", "Error",
                            JOptionPane.ERROR_MESSAGE);
                }
            }
        });

        b3.addActionListener(e -> {
            String strMonto = JOptionPane.showInputDialog(dashboardPanel, "Ingrese el monto a abonar a la tarjeta:",
                    "Abonar", JOptionPane.QUESTION_MESSAGE);
            if (strMonto != null && !strMonto.isEmpty()) {
                try {
                    double monto = Double.parseDouble(strMonto);
                    boolean exito = atmService.realizarOperacion(currentCard, monto, "Abono a cuenta");
                    if (exito) {
                        JOptionPane.showMessageDialog(dashboardPanel,
                                "Abono realizado con éxito.\nNuevo saldo: $"
                                        + String.format("%.2f", atmService.consultarSaldo(currentCard)),
                                "Éxito", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(dashboardPanel,
                                "No se pudo realizar el abono. El monto excede el límite de la tarjeta.", "Error",
                                JOptionPane.ERROR_MESSAGE);
                    }
                } catch (NumberFormatException ex) {
                    JOptionPane.showMessageDialog(dashboardPanel, "Monto inválido.", "Error",
                            JOptionPane.ERROR_MESSAGE);
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(dashboardPanel, "Error de conexión.", "Error",
                            JOptionPane.ERROR_MESSAGE);
                }
            }
        });

        b4.addActionListener(e -> {
            try {
                List<String> h = atmService.obtenerHistorial(currentCard);
                JTextArea area = new JTextArea(15, 80);
                area.setFont(new Font("Monospaced", Font.PLAIN, 14));
                area.setEditable(false);
                if (h.isEmpty()) {
                    area.append("No hay transacciones registradas.");
                } else {
                    for (String s : h)
                        area.append(s + "\n");
                }
                JOptionPane.showMessageDialog(dashboardPanel, new JScrollPane(area), "Historial de Transacciones",
                        JOptionPane.PLAIN_MESSAGE);
            } catch (Exception ex) {
            }
        });

        return atmRoot;
    }

    // DISEÑO DEL PANEL DE CONVERSOR
    private JPanel createConverterPanel() {
        JPanel p = new JPanel(null);
        p.setBackground(BG_LIGHT);

        p.add(createHeader("Casa de Cambio", "Cotice y convierta sus divisas al instante."));

        // Contenedor principal del conversor
        JPanel convPanel = new JPanel(null);
        convPanel.setBackground(CARD_BG);
        convPanel.setBounds(50, 140, 650, 380);
        convPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(226, 232, 240), 1, true),
                BorderFactory.createEmptyBorder(20, 20, 20, 20)));

        JLabel lblDivisa = new JLabel("Seleccione la divisa:");
        lblDivisa.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblDivisa.setForeground(TEXT_DARK);
        lblDivisa.setBounds(30, 30, 200, 30);
        convPanel.add(lblDivisa);

        String[] monedas = { "Dólar N.A.", "Dólar Canadiense", "Peso Chileno", "Libra Esterlina", "Yen Japonés",
                "Peso Mexicano", "Euro" };
        JComboBox<String> cbMonedas = new JComboBox<>(monedas);
        cbMonedas.setFont(new Font("Segoe UI", Font.PLAIN, 16));
        cbMonedas.setBounds(30, 65, 250, 45);
        cbMonedas.setBackground(Color.WHITE);
        convPanel.add(cbMonedas);

        JLabel lblOp = new JLabel("Tipo de Operación:");
        lblOp.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblOp.setForeground(TEXT_DARK);
        lblOp.setBounds(350, 30, 200, 30);
        convPanel.add(lblOp);

        JRadioButton rbBuy = new JRadioButton("Comprar Divisa (Vender Soles)", true);
        JRadioButton rbSell = new JRadioButton("Vender Divisa (Comprar Soles)");
        rbBuy.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        rbSell.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        rbBuy.setOpaque(false);
        rbSell.setOpaque(false);
        ButtonGroup bg = new ButtonGroup();
        bg.add(rbBuy);
        bg.add(rbSell);
        rbBuy.setBounds(350, 65, 250, 25);
        rbSell.setBounds(350, 95, 250, 25);
        convPanel.add(rbBuy);
        convPanel.add(rbSell);

        JLabel lblMonto = new JLabel("Monto a convertir:");
        lblMonto.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblMonto.setForeground(TEXT_DARK);
        lblMonto.setBounds(30, 135, 200, 30);
        convPanel.add(lblMonto);

        JTextField txtMonto = new JTextField() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                if (getText().isEmpty()) {
                    Graphics2D g2 = (Graphics2D) g.create();
                    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
                    g2.setColor(new Color(156, 163, 175));
                    g2.setFont(getFont().deriveFont(Font.ITALIC));
                    int y = (getHeight() - g.getFontMetrics().getHeight()) / 2 + g.getFontMetrics().getAscent();
                    g2.drawString("Ej: 1500.50", getInsets().left, y);
                    g2.dispose();
                }
            }
        };
        txtMonto.setFont(new Font("Segoe UI", Font.PLAIN, 18));
        txtMonto.setBounds(30, 170, 250, 45);
        txtMonto.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(203, 213, 225), 1, true),
                BorderFactory.createEmptyBorder(5, 15, 5, 15)));
        convPanel.add(txtMonto);

        JButton btnCalc = createCustomButton("CALCULAR CAMBIO", new Color(16, 185, 129), new Color(5, 150, 105));
        btnCalc.setBounds(350, 170, 250, 45);
        convPanel.add(btnCalc);

        // Panel de Resultado
        JPanel resPanel = new JPanel(new BorderLayout());
        resPanel.setBackground(new Color(241, 245, 249)); // Slate 100
        resPanel.setBounds(30, 260, 570, 80);
        resPanel.setBorder(BorderFactory.createLineBorder(new Color(203, 213, 225), 1, true));

        JLabel lblRes = new JLabel(" Resultado:", SwingConstants.CENTER);
        lblRes.setFont(new Font("Segoe UI", Font.BOLD, 24));
        lblRes.setForeground(new Color(15, 23, 42));
        resPanel.add(lblRes, BorderLayout.CENTER);

        convPanel.add(resPanel);
        p.add(convPanel);

        btnCalc.addActionListener(e -> {
            try {
                double m = Double.parseDouble(txtMonto.getText());
                int idx = cbMonedas.getSelectedIndex();
                double res = 0;
                if (rbBuy.isSelected()) { // Soles -> Extranjera
                    switch (idx) {
                        case 0:
                            res = converterService.convertirADolarNA(m);
                            break;
                        case 1:
                            res = converterService.convertirADolarCanadiense(m);
                            break;
                        case 2:
                            res = converterService.convertirAPesoChileno(m);
                            break;
                        case 3:
                            res = converterService.convertirALibraEsterlina(m);
                            break;
                        case 4:
                            res = converterService.convertirAYenJapones(m);
                            break;
                        case 5:
                            res = converterService.convertirAPesoMexicano(m);
                            break;
                        case 6:
                            res = converterService.convertirAEuro(m);
                            break;
                    }
                    lblRes.setText(String.format("Recibes: %.2f %s", res, cbMonedas.getSelectedItem()));
                } else { // Extranjera -> Soles
                    switch (idx) {
                        case 0:
                            res = converterService.convertirDesdeDolarNA(m);
                            break;
                        case 1:
                            res = converterService.convertirDesdeDolarCanadiense(m);
                            break;
                        case 2:
                            res = converterService.convertirDesdePesoChileno(m);
                            break;
                        case 3:
                            res = converterService.convertirDesdeLibraEsterlina(m);
                            break;
                        case 4:
                            res = converterService.convertirDesdeYenJapones(m);
                            break;
                        case 5:
                            res = converterService.convertirDesdePesoMexicano(m);
                            break;
                        case 6:
                            res = converterService.convertirDesdeEuro(m);
                            break;
                    }
                    lblRes.setText(String.format("Recibes: S/ %.2f", res));
                }
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(p, "Monto inválido. Ingrese un número válido.", "Error",
                        JOptionPane.WARNING_MESSAGE);
                lblRes.setText(" Resultado: Error");
            }
        });

        return p;
    }

    // Helpers de UI
    private JButton createNavButton(String text) {
        JButton b = new JButton(text);
        b.setFont(new Font("Segoe UI", Font.BOLD, 15));
        b.setForeground(new Color(241, 245, 249));
        b.setBackground(PRIMARY_NAV);
        b.setFocusPainted(false);
        b.setBorderPainted(false);
        b.setContentAreaFilled(true);
        b.setCursor(new Cursor(Cursor.HAND_CURSOR));
        b.setHorizontalAlignment(SwingConstants.LEFT);
        b.setBorder(new EmptyBorder(10, 20, 10, 20));

        b.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                b.setBackground(NAV_HOVER);
            }

            public void mouseExited(MouseEvent e) {
                b.setBackground(PRIMARY_NAV);
            }
        });

        return b;
    }

    private JButton createCustomButton(String text, Color bg, Color hover) {
        JButton b = new JButton(text);
        b.setFont(new Font("Segoe UI", Font.BOLD, 14));
        b.setUI(new javax.swing.plaf.basic.BasicButtonUI());
        b.setBackground(bg);
        b.setForeground(Color.WHITE);
        b.setFocusPainted(false);
        b.setBorderPainted(false);
        b.setContentAreaFilled(true);
        b.setBorder(BorderFactory.createEmptyBorder(10, 15, 10, 15));
        b.setCursor(new Cursor(Cursor.HAND_CURSOR));

        b.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                b.setBackground(hover);
            }

            public void mouseExited(MouseEvent e) {
                b.setBackground(bg);
            }
        });
        return b;
    }

    private JButton createOpButton(String text, String icon) {
        JButton b = new JButton("<html><center><span style='font-size:50px;'>" + icon
                + "</span><br><br><span style='color:#1e293b; font-size:10px;'>" + text + "</span></center></html>");
        b.setFont(new Font("Segoe UI", Font.BOLD, 11));
        b.setBackground(Color.WHITE);
        b.setForeground(TEXT_DARK);
        b.setFocusPainted(false);
        b.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(226, 232, 240), 1, true),
                BorderFactory.createEmptyBorder(15, 5, 15, 5)));
        b.setCursor(new Cursor(Cursor.HAND_CURSOR));

        b.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                b.setBackground(new Color(248, 250, 252));
                b.setBorder(BorderFactory.createCompoundBorder(
                        BorderFactory.createLineBorder(ACCENT_BLUE, 1, true),
                        BorderFactory.createEmptyBorder(15, 5, 15, 5)));
            }

            public void mouseExited(MouseEvent e) {
                b.setBackground(Color.WHITE);
                b.setBorder(BorderFactory.createCompoundBorder(
                        BorderFactory.createLineBorder(new Color(226, 232, 240), 1, true),
                        BorderFactory.createEmptyBorder(15, 5, 15, 5)));
            }
        });

        return b;
    }

    public static void main(String[] args) {
        // Mejorar renderizado de texto en Windows
        System.setProperty("awt.useSystemAAFontSettings", "on");
        System.setProperty("swing.aatext", "true");

        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
        }

        SwingUtilities.invokeLater(() -> new FinancialGUI().setVisible(true));
    }
}