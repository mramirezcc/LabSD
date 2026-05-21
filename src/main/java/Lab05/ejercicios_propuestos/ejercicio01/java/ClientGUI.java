package Lab05.ejercicios_propuestos.ejercicio01.java;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.MatteBorder;
import java.awt.*;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.ArrayList;

public class ClientGUI extends JFrame {

    // ── Paleta de colores formal ──────────────────────────────────────────────
    private static final Color BG_BASE        = new Color(245, 245, 247);
    private static final Color BG_CARD        = Color.WHITE;
    private static final Color BG_DISPLAY     = new Color(250, 250, 252);
    private static final Color BG_HEADER      = new Color(238, 238, 242);
    private static final Color BG_KEY_NUM     = Color.WHITE;
    private static final Color BG_KEY_OP      = new Color(232, 236, 242);
    private static final Color BG_KEY_EQUAL   = new Color(37,  99, 235);   // azul universitario
    private static final Color BG_KEY_CLEAR   = new Color(254, 242, 242);

    private static final Color FG_PRIMARY     = new Color(17,  24,  39);
    private static final Color FG_SECONDARY   = new Color(107, 114, 128);
    private static final Color FG_OPERATOR    = new Color(37,  99, 235);
    private static final Color FG_CLEAR       = new Color(185,  28,  28);
    private static final Color FG_EQUAL       = Color.WHITE;
    private static final Color FG_HISTORY     = new Color(156, 163, 175);
    private static final Color FG_DISPLAY     = new Color(17,  24,  39);
    private static final Color FG_DISABLED    = new Color(180, 180, 185);

    private static final Color BORDER_CARD    = new Color(209, 213, 219);
    private static final Color BORDER_INPUT   = new Color(209, 213, 219);
    private static final Color STATUS_OK      = new Color(22, 163,  74);
    private static final Color STATUS_ERR     = new Color(185,  28,  28);
    private static final Color STATUS_WAIT    = new Color(161, 119,  11);

    private static final Font FONT_UI    = new Font("Segoe UI", Font.PLAIN,  13);
    private static final Font FONT_BOLD  = new Font("Segoe UI", Font.BOLD,   13);
    private static final Font FONT_MONO  = new Font("Consolas",  Font.PLAIN,  13);
    private static final Font FONT_DISPLAY = new Font("Segoe UI", Font.PLAIN, 34);
    private static final Font FONT_HISTORY  = new Font("Consolas", Font.PLAIN, 13);
    private static final Font FONT_KEY_NUM  = new Font("Segoe UI", Font.PLAIN, 16);
    private static final Font FONT_KEY_OP   = new Font("Segoe UI", Font.PLAIN, 17);

    // ── Estado ────────────────────────────────────────────────────────────────
    private JTextField  txtIP;
    private JLabel      lblHistory;
    private JLabel      lblDisplay;
    private JLabel      lblStatus;
    private JLabel      lblStatusDot;
    private JButton     btnConnect;
    private Calculator  calculator;

    private final ArrayList<JButton> calcButtons = new ArrayList<>();

    private double  firstNumber       = 0;
    private String  selectedOperation = "";
    private String  operationSymbol   = "";
    private boolean startNewNumber    = true;

    // ─────────────────────────────────────────────────────────────────────────
    public ClientGUI() {
        buildUI();
        setCalcEnabled(false);
    }

    // ── Conexión RMI ──────────────────────────────────────────────────────────
    private void connectRMI(String ip) {
        setStatus("Conectando a " + ip + "…", STATUS_WAIT, false);
        SwingUtilities.invokeLater(() -> {
            try {
                Registry registry = LocateRegistry.getRegistry(ip, 1099);
                calculator = (Calculator) registry.lookup("CalculatorService");
                setStatus("Conectado a " + ip, STATUS_OK, true);
                setCalcEnabled(true);
            } catch (Exception e) {
                calculator = null;
                setCalcEnabled(false);
                setStatus("Sin conexión — error de enlace", STATUS_ERR, false);
                JOptionPane.showMessageDialog(
                    this,
                    "No se pudo conectar al servidor RMI en " + ip + ".\n" + e.getMessage(),
                    "Error de conexión",
                    JOptionPane.ERROR_MESSAGE
                );
            }
        });
    }

    private void setStatus(String msg, Color color, boolean connected) {
        lblStatus.setText(msg);
        lblStatus.setForeground(color);
        lblStatusDot.setForeground(connected ? STATUS_OK : STATUS_ERR);
        lblStatusDot.setText(connected ? "●" : "●");
    }

    // ── Habilitar/deshabilitar teclado ────────────────────────────────────────
    private void setCalcEnabled(boolean on) {
        if (!on) {
            lblDisplay.setText("—");
            lblDisplay.setForeground(FG_DISABLED);
            lblHistory.setText(" ");
        } else {
            lblDisplay.setText("0");
            lblDisplay.setForeground(FG_DISPLAY);
        }
        for (JButton b : calcButtons) b.setEnabled(on);
    }

    // ── Construcción de la interfaz ───────────────────────────────────────────
    private void buildUI() {
        setTitle("Calculadora RMI — Lab 05");
        setSize(400, 640);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setResizable(false);

        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(BG_BASE);
        root.setBorder(new EmptyBorder(20, 20, 20, 20));

        // ── Tarjeta principal ─────────────────────────────────────────────────
        JPanel card = new JPanel(new BorderLayout());
        card.setBackground(BG_CARD);
        card.setBorder(BorderFactory.createLineBorder(BORDER_CARD, 1));

        card.add(buildHeader(),  BorderLayout.NORTH);
        card.add(buildBody(),    BorderLayout.CENTER);
        card.add(buildFooter(),  BorderLayout.SOUTH);

        root.add(card, BorderLayout.CENTER);
        setContentPane(root);
    }

    // ── Encabezado: nombre y conexión ─────────────────────────────────────────
    private JPanel buildHeader() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(BG_HEADER);
        panel.setBorder(new EmptyBorder(14, 16, 14, 16));

        // Título
        JLabel title = new JLabel("Calculadora RMI");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        title.setForeground(FG_PRIMARY);

        JLabel subtitle = new JLabel("Laboratorio 05  ·  Ejercicio 01  ·  Sistemas Distribuidos");
        subtitle.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        subtitle.setForeground(FG_SECONDARY);

        JSeparator sep = new JSeparator();
        sep.setForeground(BORDER_CARD);
        sep.setMaximumSize(new Dimension(Integer.MAX_VALUE, 1));

        // Fila de conexión
        JPanel row = new JPanel(new BorderLayout(8, 0));
        row.setBackground(BG_HEADER);
        row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));

        txtIP = new JTextField("localhost");
        txtIP.setFont(FONT_MONO);
        txtIP.setForeground(FG_PRIMARY);
        txtIP.setBackground(BG_CARD);
        txtIP.setCaretColor(FG_PRIMARY);
        txtIP.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER_INPUT, 1),
            new EmptyBorder(4, 8, 4, 8)
        ));

        btnConnect = new JButton("Enlazar");
        btnConnect.setFont(FONT_BOLD);
        btnConnect.setBackground(new Color(37, 99, 235));
        btnConnect.setForeground(Color.WHITE);
        btnConnect.setFocusPainted(false);
        btnConnect.setBorderPainted(false);
        btnConnect.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        btnConnect.setBorder(new EmptyBorder(6, 14, 6, 14));
        btnConnect.addActionListener(e -> connectRMI(txtIP.getText().trim()));

        row.add(txtIP,      BorderLayout.CENTER);
        row.add(btnConnect, BorderLayout.EAST);

        // Fila de estado
        JPanel statusRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 0));
        statusRow.setBackground(BG_HEADER);
        statusRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 20));

        lblStatusDot = new JLabel("●");
        lblStatusDot.setFont(new Font("Segoe UI", Font.PLAIN, 9));
        lblStatusDot.setForeground(STATUS_ERR);

        lblStatus = new JLabel("Sin conexión — ingrese la IP del servidor");
        lblStatus.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        lblStatus.setForeground(FG_SECONDARY);

        statusRow.add(lblStatusDot);
        statusRow.add(lblStatus);

        panel.add(title);
        panel.add(Box.createRigidArea(new Dimension(0, 2)));
        panel.add(subtitle);
        panel.add(Box.createRigidArea(new Dimension(0, 10)));
        panel.add(row);
        panel.add(Box.createRigidArea(new Dimension(0, 6)));
        panel.add(statusRow);

        return panel;
    }

    // ── Cuerpo: display + teclado ─────────────────────────────────────────────
    private JPanel buildBody() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(BG_CARD);

        // Display
        JPanel display = new JPanel();
        display.setLayout(new BoxLayout(display, BoxLayout.Y_AXIS));
        display.setBackground(BG_DISPLAY);
        display.setBorder(new EmptyBorder(12, 16, 12, 16));

        lblHistory = new JLabel(" ");
        lblHistory.setFont(FONT_HISTORY);
        lblHistory.setForeground(FG_HISTORY);
        lblHistory.setAlignmentX(Component.RIGHT_ALIGNMENT);

        lblDisplay = new JLabel("—");
        lblDisplay.setFont(FONT_DISPLAY);
        lblDisplay.setForeground(FG_DISABLED);
        lblDisplay.setAlignmentX(Component.RIGHT_ALIGNMENT);

        display.add(lblHistory);
        display.add(Box.createRigidArea(new Dimension(0, 4)));
        display.add(lblDisplay);

        JPanel displayWrapper = new JPanel(new BorderLayout());
        displayWrapper.setBackground(BG_CARD);
        displayWrapper.setBorder(new MatteBorder(0, 0, 1, 0, BORDER_CARD));
        displayWrapper.add(display);

        panel.add(displayWrapper, BorderLayout.NORTH);
        panel.add(buildKeypad(),  BorderLayout.CENTER);

        return panel;
    }

    // ── Teclado ───────────────────────────────────────────────────────────────
    private JPanel buildKeypad() {
        JPanel pad = new JPanel(new GridLayout(5, 4, 0, 0));
        pad.setBackground(BORDER_CARD);
        pad.setBorder(BorderFactory.createLineBorder(BORDER_CARD, 0));

        // Fila 1
        JButton btnC   = makeKey("C",   KeyType.CLEAR);
        JButton btnPow = makeKey("^",   KeyType.OP);
        JButton btnDiv = makeKey("÷",   KeyType.OP);
        JButton btnMul = makeKey("×",   KeyType.OP);
        // Fila 2
        JButton btn7   = makeKey("7",   KeyType.NUM);
        JButton btn8   = makeKey("8",   KeyType.NUM);
        JButton btn9   = makeKey("9",   KeyType.NUM);
        JButton btnSub = makeKey("−",   KeyType.OP);
        // Fila 3
        JButton btn4   = makeKey("4",   KeyType.NUM);
        JButton btn5   = makeKey("5",   KeyType.NUM);
        JButton btn6   = makeKey("6",   KeyType.NUM);
        JButton btnAdd = makeKey("+",   KeyType.OP);
        // Fila 4
        JButton btn1   = makeKey("1",   KeyType.NUM);
        JButton btn2   = makeKey("2",   KeyType.NUM);
        JButton btn3   = makeKey("3",   KeyType.NUM);
        JButton btnBck = makeKey("←",   KeyType.OP);
        // Fila 5
        JButton btn0   = makeKey("0",   KeyType.NUM);
        JButton btnDot = makeKey(".",   KeyType.NUM);
        JButton btnSgn = makeKey("±",   KeyType.OP);
        JButton btnEq  = makeKey("=",   KeyType.EQUAL);

        // Registrar todos para bloqueo/desbloqueo
        JButton[] all = { btnC, btnPow, btnDiv, btnMul,
                          btn7, btn8, btn9, btnSub,
                          btn4, btn5, btn6, btnAdd,
                          btn1, btn2, btn3, btnBck,
                          btn0, btnDot, btnSgn, btnEq };
        for (JButton b : all) calcButtons.add(b);

        // Acciones numéricas
        for (JButton b : new JButton[]{ btn0,btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9 })
            b.addActionListener(e -> appendDigit(b.getText()));
        btnDot.addActionListener(e -> appendDot());

        // Acciones de control
        btnC.addActionListener(e -> clearAll());
        btnBck.addActionListener(e -> backspace());
        btnSgn.addActionListener(e -> toggleSign());

        // Operadores remotos
        btnAdd.addActionListener(e -> prepareOperation("add",      "+"));
        btnSub.addActionListener(e -> prepareOperation("subtract", "−"));
        btnMul.addActionListener(e -> prepareOperation("multiply", "×"));
        btnDiv.addActionListener(e -> prepareOperation("divide",   "÷"));
        btnPow.addActionListener(e -> prepareOperation("power",    "^"));
        btnEq.addActionListener(e  -> executeCalculation());

        // Agregar en orden
        pad.add(btnC);   pad.add(btnPow); pad.add(btnDiv); pad.add(btnMul);
        pad.add(btn7);   pad.add(btn8);   pad.add(btn9);   pad.add(btnSub);
        pad.add(btn4);   pad.add(btn5);   pad.add(btn6);   pad.add(btnAdd);
        pad.add(btn1);   pad.add(btn2);   pad.add(btn3);   pad.add(btnBck);
        pad.add(btn0);   pad.add(btnDot); pad.add(btnSgn); pad.add(btnEq);

        return pad;
    }

    private enum KeyType { NUM, OP, EQUAL, CLEAR }

    private JButton makeKey(String label, KeyType type) {
        JButton btn = new JButton(label) {
            @Override protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                if (getModel().isPressed()) g2.setColor(getBackground().darker());
                else if (getModel().isRollover() && isEnabled()) g2.setColor(getBackground().brighter());
                else g2.setColor(getBackground());
                g2.fillRect(0, 0, getWidth(), getHeight());
                g2.dispose();
                super.paintComponent(g);
            }
        };
        btn.setOpaque(false);
        btn.setContentAreaFilled(false);
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 1, BORDER_CARD));
        btn.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        btn.setPreferredSize(new Dimension(90, 64));

        switch (type) {
            case NUM:
                btn.setFont(FONT_KEY_NUM);
                btn.setForeground(FG_PRIMARY);
                btn.setBackground(BG_KEY_NUM);
                break;
            case OP:
                btn.setFont(FONT_KEY_OP);
                btn.setForeground(FG_OPERATOR);
                btn.setBackground(BG_KEY_OP);
                break;
            case EQUAL:
                btn.setFont(new Font("Segoe UI", Font.BOLD, 18));
                btn.setForeground(FG_EQUAL);
                btn.setBackground(BG_KEY_EQUAL);
                break;
            case CLEAR:
                btn.setFont(FONT_KEY_OP);
                btn.setForeground(FG_CLEAR);
                btn.setBackground(BG_KEY_CLEAR);
                break;
        }

        // Override de colores cuando está deshabilitado
        btn.addPropertyChangeListener("enabled", evt -> {
            if (!(Boolean) evt.getNewValue()) btn.setForeground(FG_DISABLED);
            else {
                switch (type) {
                    case NUM:   btn.setForeground(FG_PRIMARY);  break;
                    case OP:    btn.setForeground(FG_OPERATOR); break;
                    case EQUAL: btn.setForeground(FG_EQUAL);    break;
                    case CLEAR: btn.setForeground(FG_CLEAR);    break;
                }
            }
        });

        return btn;
    }

    // ── Pie de página ─────────────────────────────────────────────────────────
    private JPanel buildFooter() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(BG_HEADER);
        panel.setBorder(new MatteBorder(1, 0, 0, 0, BORDER_CARD));

        JLabel left = new JLabel("UNSA — Ingeniería de Sistemas");
        left.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        left.setForeground(FG_SECONDARY);
        left.setBorder(new EmptyBorder(8, 14, 8, 0));

        JLabel right = new JLabel("Puerto 1099");
        right.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        right.setForeground(FG_SECONDARY);
        right.setBorder(new EmptyBorder(8, 0, 8, 14));

        panel.add(left,  BorderLayout.WEST);
        panel.add(right, BorderLayout.EAST);
        return panel;
    }

    // ── Lógica de la calculadora ──────────────────────────────────────────────
    private String getDisplay() { return lblDisplay.getText(); }
    private void   setDisplay(String v) { lblDisplay.setText(v); }

    private void appendDigit(String d) {
        if (startNewNumber || getDisplay().equals("0") || getDisplay().equals("—")) {
            setDisplay(d);
            lblDisplay.setForeground(FG_DISPLAY);
            startNewNumber = false;
        } else {
            setDisplay(getDisplay() + d);
        }
    }

    private void appendDot() {
        if (startNewNumber) { setDisplay("0."); startNewNumber = false; return; }
        if (!getDisplay().contains(".")) setDisplay(getDisplay() + ".");
    }

    private void clearAll() {
        setDisplay("0");
        lblDisplay.setForeground(FG_DISPLAY);
        lblHistory.setText(" ");
        firstNumber = 0;
        selectedOperation = "";
        operationSymbol   = "";
        startNewNumber    = true;
    }

    private void backspace() {
        String cur = getDisplay();
        if (cur.length() > 1) setDisplay(cur.substring(0, cur.length() - 1));
        else { setDisplay("0"); startNewNumber = true; }
    }

    private void toggleSign() {
        try {
            double v = Double.parseDouble(getDisplay());
            if (v != 0) {
                v = -v;
                setDisplay(v % 1 == 0 ? String.valueOf((long) v) : String.valueOf(v));
            }
        } catch (NumberFormatException ignored) {}
    }

    private void prepareOperation(String op, String sym) {
        try {
            firstNumber       = Double.parseDouble(getDisplay());
            selectedOperation = op;
            operationSymbol   = sym;
            String fmt = firstNumber % 1 == 0
                ? String.valueOf((long) firstNumber)
                : String.valueOf(firstNumber);
            lblHistory.setText(fmt + "  " + operationSymbol);
            startNewNumber = true;
        } catch (NumberFormatException e) {
            setDisplay("Error");
        }
    }

    private void executeCalculation() {
        if (calculator == null || selectedOperation.isEmpty()) return;
        try {
            double b = Double.parseDouble(getDisplay());
            double r;
            // 1. Iniciar el temporizador justo antes de la llamada de red
            long tiempoInicio = System.nanoTime();
            switch (selectedOperation) {
                case "add":      r = calculator.add(firstNumber, b);      break;
                case "subtract": r = calculator.subtract(firstNumber, b); break;
                case "multiply": r = calculator.multiply(firstNumber, b); break;
                case "divide":   r = calculator.divide(firstNumber, b);   break;
                case "power":    r = calculator.power(firstNumber, b);    break;
                default: return;
            }
            // 2. Detener el temporizador inmediatamente después de recibir la respuesta
            long tiempoFin = System.nanoTime();
            
            // 3. Convertir la diferencia de nanosegundos a milisegundos
            double tiempoTotalMs = (tiempoFin - tiempoInicio) / 1_000_000.0;
            
            // 4. Imprimir la telemetría en la consola de VS Code
            System.out.println("\n[TELEMETRÍA RMI — EJERCICIO 01]");
            System.out.printf("Operación ejecutada: %s (%f, %f)\n", selectedOperation, firstNumber, b);
            System.out.printf(">>>> Tiempo de respuesta del servidor: %.3f ms\n", tiempoTotalMs);
            // Código para estimar la memoria en uso por la JVM
            Runtime runtime = Runtime.getRuntime();
            long memoriaUsada = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);
            System.out.printf(">>>> Memoria estimada en uso: %d MB\n", memoriaUsada);
            System.out.println("────────────────────────────────────────────────────────");
            
            lblHistory.setText(" ");
            setDisplay(r % 1 == 0 ? String.valueOf((long) r) : String.valueOf(r));
            selectedOperation = "";
            operationSymbol   = "";
            startNewNumber    = true;
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, ex.getMessage(),
                "Error en el servidor", JOptionPane.ERROR_MESSAGE);
            setDisplay("Error");
            lblHistory.setText(" ");
            startNewNumber = true;
        }
    }

    // ── Main ──────────────────────────────────────────────────────────────────
    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}
        SwingUtilities.invokeLater(() -> new ClientGUI().setVisible(true));
    }
}