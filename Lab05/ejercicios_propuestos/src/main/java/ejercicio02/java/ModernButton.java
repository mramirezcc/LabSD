package ejercicio02.java;

import javax.swing.*;
import java.awt.*;

public class ModernButton extends JButton {
    public ModernButton(String text, Color color) {
        super(text);
        setFocusPainted(false);
        setForeground(Color.WHITE);
        setBackground(color);
        setFont(new Font("Segoe UI", Font.BOLD, 13));
        setCursor(new Cursor(Cursor.HAND_CURSOR));
        setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
    }
}
