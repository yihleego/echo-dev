import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class JavaSwing {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Java Swing Example");
        frame.setSize(300, 150);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        JPanel panel = new JPanel();

        JTextField textField = new JTextField(20);

        JButton button = new JButton("Click");

        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String inputText = textField.getText();
                System.out.println("Input Text: " + inputText);
            }
        });

        JCheckBox checkBox = new JCheckBox("Enable Feature");

        checkBox.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                boolean selected = checkBox.isSelected();
                if (selected) {
                    System.out.println("Feature is enabled");
                } else {
                    System.out.println("Feature is disabled");
                }
            }
        });

        ButtonGroup buttonGroup = new ButtonGroup();
        JRadioButton radioButton1 = new JRadioButton("Option 1");
        JRadioButton radioButton2 = new JRadioButton("Option 2");
        JRadioButton radioButton3 = new JRadioButton("Option 3");
        buttonGroup.add(radioButton1);
        buttonGroup.add(radioButton2);
        buttonGroup.add(radioButton3);

        panel.add(textField);
        panel.add(button);
        panel.add(checkBox);
        panel.add(radioButton1);
        panel.add(radioButton2);
        panel.add(radioButton3);

        frame.add(panel);

        frame.setVisible(true);
    }
}
