package Lab05.ejercicios_propuestos.ejercicio02.java;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.MatteBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;

public class ClientGrpcGUI extends JFrame {

    // ── Paleta formal ─────────────────────────────────────────────────────────
    private static final Color BG_ROOT      = new Color(243, 244, 246);
    private static final Color BG_CARD      = Color.WHITE;
    private static final Color BG_HEADER    = new Color(248, 249, 250);
    private static final Color BG_ROW_A     = Color.WHITE;
    private static final Color BG_ROW_B     = new Color(249, 250, 251);
    private static final Color BG_INPUT     = new Color(252, 252, 253);
    private static final Color BG_BTN       = new Color(37,  99, 235);
    private static final Color BG_BTN_HOVER = new Color(29,  78, 216);
    private static final Color BG_CONNECT   = new Color(37,  99, 235);

    private static final Color FG_PRIMARY   = new Color(17,  24,  39);
    private static final Color FG_SECONDARY = new Color(107, 114, 128);
    private static final Color FG_TERTIARY  = new Color(156, 163, 175);
    private static final Color FG_OK        = new Color(22, 163,  74);
    private static final Color FG_ERR       = new Color(185,  28,  28);
    private static final Color FG_WAIT      = new Color(146, 103,  10);
    private static final Color FG_RESULT    = new Color(37,  99, 235);

    private static final Color BORDER       = new Color(229, 231, 235);
    private static final Color BORDER_INPUT = new Color(209, 213, 219);

    // ── Tipografía ────────────────────────────────────────────────────────────
    private static final Font F_TITLE   = new Font("Segoe UI", Font.BOLD,  15);
    private static final Font F_SUB     = new Font("Segoe UI", Font.PLAIN, 11);
    private static final Font F_LABEL   = new Font("Segoe UI", Font.PLAIN, 12);
    private static final Font F_LABEL_B = new Font("Segoe UI", Font.BOLD,  12);
    private static final Font F_INPUT   = new Font("Segoe UI", Font.PLAIN, 13);
    private static final Font F_RESULT  = new Font("Segoe UI", Font.BOLD,  15);
    private static final Font F_MONO    = new Font("Consolas",  Font.PLAIN, 13);
    private static final Font F_STATUS  = new Font("Segoe UI", Font.PLAIN, 11);
    private static final Font F_BTN     = new Font("Segoe UI", Font.BOLD,  12);

    // ── Estado ────────────────────────────────────────────────────────────────
    private JTextField txtIP;
    private JLabel     lblStatus, lblStatusDot;
    private JButton    btnConnect;

    private ManagedChannel              canalRed;
    private ConverterGrpc.ConverterBlockingStub stubBloqueante;

    private final ArrayList<JComponent> componentes = new ArrayList<>();

    // ─────────────────────────────────────────────────────────────────────────
    public ClientGrpcGUI() {
        buildUI();
        habilitarComponentes(false); // Solo bloquea inputs y botones de conversión
    }

    // ── Conexión gRPC ─────────────────────────────────────────────────────────
    private void conectar(String ip) {
        setStatus("Conectando a " + ip + "…", FG_WAIT, false);
        SwingWorker<Boolean, Void> worker = new SwingWorker<>() {
            @Override protected Boolean doInBackground() {
                try {
                    if (canalRed != null) canalRed.shutdown();
                    canalRed = ManagedChannelBuilder.forAddress(ip, 9090)
                            .usePlaintext().build();
                    stubBloqueante = ConverterGrpc.newBlockingStub(canalRed);
                    return true;
                } catch (Exception e) { return false; }
            }
            @Override protected void done() {
                try {
                    if (get()) {
                        setStatus("Conectado a " + ip + " (puerto 9090)", FG_OK, true);
                        habilitarComponentes(true);
                    } else {
                        setStatus("Sin conexión — no se pudo abrir el canal gRPC", FG_ERR, false);
                        habilitarComponentes(false);
                        JOptionPane.showMessageDialog(ClientGrpcGUI.this,
                            "No se pudo establecer el canal HTTP/2 con " + ip + ".",
                            "Error de conexión", JOptionPane.ERROR_MESSAGE);
                    }
                } catch (Exception ignored) {}
            }
        };
        worker.execute();
    }

    private void setStatus(String msg, Color color, boolean ok) {
        lblStatus.setText(msg);
        lblStatus.setForeground(color);
        lblStatusDot.setForeground(ok ? FG_OK : FG_ERR);
    }

    private void habilitarComponentes(boolean on) {
        for (JComponent c : componentes) {
            c.setEnabled(on);
            if (c instanceof JTextField) {
                ((JTextField) c).setText("");
                c.setBackground(on ? BG_INPUT : new Color(245, 245, 247));
            }
        }
    }

    // ── Llamada remota ────────────────────────────────────────────────────────
    private void convertir(String opCode, JTextField input, JLabel result, JLabel unit) {
        if (stubBloqueante == null) return;
        try {
            double val = Double.parseDouble(input.getText().trim());
            ConvertRequest req = ConvertRequest.newBuilder()
                    .setValue(val).setConversionType(opCode).build();
            
            // 1. Iniciar temporizador gRPC (Antes de la serialización binaria y envío HTTP/2)
            long tiempoInicio = System.nanoTime();
            ConvertResponse resp = stubBloqueante.convert(req);

            // 2. Detener el temporizador inmediatamente después de recibir la respuesta
            long tiempoFin = System.nanoTime();

            // 3. Convertir la diferencia de nanosegundos a milisegundos
            double tiempoTotalMs = (tiempoFin - tiempoInicio) / 1_000_000.0;
        
            // 4. Imprimir la telemetría en la consola de VS Code
            System.out.println("\n[TELEMETRÍA gRPC — EJERCICIO 02]");
            System.out.printf("Operación ejecutada: %s (%f, %f)\n", opCode, val, resp.getResult());
            System.out.printf(">>>> Tiempo de respuesta del servidor: %.3f ms\n", tiempoTotalMs);
            // Código para estimar la memoria en uso por la JVM
            Runtime runtime = Runtime.getRuntime();
            long memoriaUsada = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);
            System.out.printf(">>>> Memoria estimada en uso: %d MB\n", memoriaUsada);
            System.out.println("────────────────────────────────────────────────────────");

            if (resp.getMessage().startsWith("Error")) {
                result.setText("—");
                result.setForeground(FG_ERR);
                unit.setForeground(FG_ERR);
                JOptionPane.showMessageDialog(this, resp.getMessage(),
                        "Validación rechazada", JOptionPane.WARNING_MESSAGE);
            } else {
                result.setText(String.format(java.util.Locale.US, "%.4f", resp.getResult()));
                result.setForeground(FG_RESULT);
                unit.setForeground(FG_SECONDARY);
            }
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Ingrese un número válido.",
                    "Entrada inválida", JOptionPane.ERROR_MESSAGE);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this,
                    "Error de comunicación con el servidor:\n" + ex.getMessage(),
                    "Fallo remoto", JOptionPane.ERROR_MESSAGE);
        }
    }

    // ── Construcción de la UI ─────────────────────────────────────────────────
    private void buildUI() {
        setTitle("Conversor Distribuido gRPC — Lab 05");
        setSize(680, 780);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setResizable(false);

        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(BG_ROOT);
        root.setBorder(new EmptyBorder(18, 18, 18, 18));

        JPanel card = new JPanel(new BorderLayout());
        card.setBackground(BG_CARD);
        card.setBorder(BorderFactory.createLineBorder(BORDER, 1));

        card.add(buildHeader(),  BorderLayout.NORTH);
        card.add(buildBody(),    BorderLayout.CENTER);
        card.add(buildFooter(),  BorderLayout.SOUTH);

        root.add(card, BorderLayout.CENTER);
        setContentPane(root);
    }

    // ── Encabezado ────────────────────────────────────────────────────────────
    private JPanel buildHeader() {
        JPanel p = new JPanel();
        p.setLayout(new BoxLayout(p, BoxLayout.Y_AXIS));
        p.setBackground(BG_HEADER);
        p.setBorder(new EmptyBorder(14, 16, 14, 16));

        JLabel title = new JLabel("Conversor de Unidades — gRPC");
        title.setFont(F_TITLE);
        title.setForeground(FG_PRIMARY);

        JLabel sub = new JLabel("Laboratorio 05  ·  Ejercicio 02  ·  Sistemas Distribuidos");
        sub.setFont(F_SUB);
        sub.setForeground(FG_SECONDARY);

        // Fila IP + botón
        JPanel row = new JPanel(new BorderLayout(8, 0));
        row.setBackground(BG_HEADER);
        row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));

        txtIP = new JTextField("localhost");
        txtIP.setFont(F_MONO);
        txtIP.setForeground(FG_PRIMARY);
        txtIP.setBackground(BG_CARD);
        txtIP.setCaretColor(FG_PRIMARY);
        txtIP.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER_INPUT, 1),
            new EmptyBorder(5, 9, 5, 9)
        ));

        btnConnect = new JButton("Conectar");
        styleConnectBtn(btnConnect);
        btnConnect.addActionListener(e -> conectar(txtIP.getText().trim()));

        row.add(txtIP, BorderLayout.CENTER);
        row.add(btnConnect, BorderLayout.EAST);

        // Estado
        JPanel statusRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 0));
        statusRow.setBackground(BG_HEADER);
        statusRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 18));

        lblStatusDot = new JLabel("●");
        lblStatusDot.setFont(new Font("Segoe UI", Font.PLAIN, 9));
        lblStatusDot.setForeground(FG_ERR);

        lblStatus = new JLabel("Sin conexión — ingrese la IP del servidor gRPC");
        lblStatus.setFont(F_STATUS);
        lblStatus.setForeground(FG_SECONDARY);

        statusRow.add(lblStatusDot);
        statusRow.add(lblStatus);

        p.add(title);
        p.add(Box.createRigidArea(new Dimension(0, 2)));
        p.add(sub);
        p.add(Box.createRigidArea(new Dimension(0, 12)));
        p.add(row);
        p.add(Box.createRigidArea(new Dimension(0, 7)));
        p.add(statusRow);

        return p;
    }

    private void styleConnectBtn(JButton btn) {
        btn.setFont(F_BTN);
        btn.setBackground(BG_CONNECT);
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorderPainted(false);
        btn.setOpaque(true);
        btn.setBorder(new EmptyBorder(7, 16, 7, 16));
        btn.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        btn.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) { btn.setBackground(BG_BTN_HOVER); }
            public void mouseExited(MouseEvent e)  { btn.setBackground(BG_CONNECT);   }
        });
    }

    // ── Cuerpo: tabla de conversiones ─────────────────────────────────────────
    private JScrollPane buildBody() {
        JPanel body = new JPanel();
        body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));
        body.setBackground(BG_CARD);

        // Cabecera de columnas
        body.add(buildColumnHeader());
        body.add(separator());

        // Grupos de conversiones
        body.add(groupLabel("Temperatura"));
        body.add(buildRow("Celsius (°C)",    "Fahrenheit (°F)", "C_TO_F",   true));
        body.add(buildRow("Fahrenheit (°F)", "Celsius (°C)",    "F_TO_C",   false));
        body.add(separator());

        body.add(groupLabel("Moneda"));
        body.add(buildRow("Soles (PEN)",  "Dólares (USD)", "PEN_TO_USD", true));
        body.add(buildRow("Dólares (USD)","Soles (PEN)",   "USD_TO_PEN", false));
        body.add(separator());

        body.add(groupLabel("Distancia"));
        body.add(buildRow("Kilómetros (km)", "Millas (mi)", "KM_TO_MI", true));
        body.add(buildRow("Millas (mi)",     "Kilómetros (km)", "MI_TO_KM", false));
        body.add(separator());

        body.add(groupLabel("Masa y Tiempo"));
        body.add(buildRow("Kilogramos (kg)", "Libras (lb)",   "KG_TO_LB", true));
        body.add(buildRow("Horas (h)",       "Minutos (min)", "H_TO_MIN", false));

        JScrollPane scroll = new JScrollPane(body);
        scroll.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER));
        scroll.getVerticalScrollBar().setUnitIncrement(12);
        return scroll;
    }

    private JPanel buildColumnHeader() {
        JPanel p = new JPanel(new GridLayout(1, 4, 0, 0));
        p.setBackground(new Color(249, 250, 251));
        p.setBorder(new EmptyBorder(8, 16, 8, 16));

        String[] cols = { "Conversión", "Valor de entrada", "Resultado", "Acción" };
        for (String col : cols) {
            JLabel l = new JLabel(col);
            l.setFont(new Font("Segoe UI", Font.BOLD, 11));
            l.setForeground(FG_SECONDARY);
            p.add(l);
        }
        return p;
    }

    private JPanel buildRow(String fromLabel, String toLabel, String opCode, boolean shade) {
        JPanel p = new JPanel(new GridLayout(1, 4, 8, 0));
        p.setBackground(shade ? BG_ROW_A : BG_ROW_B);
        p.setBorder(new EmptyBorder(10, 16, 10, 16));
        p.setMaximumSize(new Dimension(Integer.MAX_VALUE, 56));

        // Columna 1: etiqueta de conversión
        JPanel labelCol = new JPanel(new BorderLayout(0, 1));
        labelCol.setOpaque(false);
        JLabel lFrom = new JLabel(fromLabel);
        lFrom.setFont(F_LABEL_B);
        lFrom.setForeground(FG_PRIMARY);
        JLabel lArrow = new JLabel("→  " + toLabel);
        lArrow.setFont(F_SUB);
        lArrow.setForeground(FG_SECONDARY);
        labelCol.add(lFrom,  BorderLayout.NORTH);
        labelCol.add(lArrow, BorderLayout.SOUTH);

        // Columna 2: input
        JTextField input = new JTextField();
        input.setFont(F_INPUT);
        input.setForeground(FG_PRIMARY);
        input.setBackground(BG_INPUT);
        input.setCaretColor(FG_PRIMARY);
        input.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER_INPUT, 1),
            new EmptyBorder(4, 8, 4, 8)
        ));
        componentes.add(input);

        // Columna 3: resultado
        JPanel resultCol = new JPanel(new BorderLayout(0, 1));
        resultCol.setOpaque(false);
        JLabel lResult = new JLabel("—");
        lResult.setFont(F_RESULT);
        lResult.setForeground(FG_TERTIARY);
        JLabel lUnit = new JLabel(toLabel);
        lUnit.setFont(F_SUB);
        lUnit.setForeground(FG_TERTIARY);
        resultCol.add(lResult, BorderLayout.NORTH);
        resultCol.add(lUnit,   BorderLayout.SOUTH);

        // Columna 4: botón
        JButton btn = new JButton("Convertir");
        btn.setFont(F_BTN);
        btn.setBackground(BG_BTN);
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorderPainted(false);
        btn.setOpaque(true);
        btn.setBorder(new EmptyBorder(6, 12, 6, 12));
        btn.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        btn.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) { if (btn.isEnabled()) btn.setBackground(BG_BTN_HOVER); }
            public void mouseExited(MouseEvent e)  { btn.setBackground(BG_BTN); }
        });
        btn.addActionListener(e -> convertir(opCode, input, lResult, lUnit));
        componentes.add(btn);

        // Enter en el input también convierte
        input.addActionListener(e -> convertir(opCode, input, lResult, lUnit));

        p.add(labelCol);
        p.add(input);
        p.add(resultCol);
        p.add(btn);
        return p;
    }

    private JPanel groupLabel(String name) {
        JPanel p = new JPanel(new BorderLayout());
        p.setBackground(new Color(239, 246, 255));
        p.setBorder(new EmptyBorder(6, 16, 6, 16));
        p.setMaximumSize(new Dimension(Integer.MAX_VALUE, 30));
        JLabel l = new JLabel(name);
        l.setFont(new Font("Segoe UI", Font.BOLD, 11));
        l.setForeground(new Color(37, 99, 235));
        p.add(l, BorderLayout.WEST);
        return p;
    }

    private JSeparator separator() {
        JSeparator s = new JSeparator();
        s.setForeground(BORDER);
        s.setMaximumSize(new Dimension(Integer.MAX_VALUE, 1));
        return s;
    }

    // ── Pie de página ─────────────────────────────────────────────────────────
    private JPanel buildFooter() {
        JPanel p = new JPanel(new BorderLayout());
        p.setBackground(BG_HEADER);
        p.setBorder(new MatteBorder(1, 0, 0, 0, BORDER));

        JLabel left = new JLabel("UNSA — Ingeniería de Sistemas  ·  Escuela Profesional de Ingeniería de Sistemas");
        left.setFont(F_SUB);
        left.setForeground(FG_SECONDARY);
        left.setBorder(new EmptyBorder(8, 16, 8, 0));

        JLabel right = new JLabel("Puerto 9090");
        right.setFont(F_SUB);
        right.setForeground(FG_SECONDARY);
        right.setBorder(new EmptyBorder(8, 0, 8, 16));

        p.add(left,  BorderLayout.WEST);
        p.add(right, BorderLayout.EAST);
        return p;
    }

    // ── Main ──────────────────────────────────────────────────────────────────
    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}
        SwingUtilities.invokeLater(() -> new ClientGrpcGUI().setVisible(true));
    }
}