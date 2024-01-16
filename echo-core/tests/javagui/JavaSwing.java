import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class JavaSwing {
    public static void main(String[] args) {
        // 创建主窗口
        JFrame frame = new JFrame("Swing Example");
        frame.setSize(300, 150);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        // 创建面板
        JPanel panel = new JPanel();

        // 创建输入框
        JTextField textField = new JTextField(20);

        // 创建按钮
        JButton button = new JButton("Click");

        // 添加按钮点击事件监听器
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // 处理按钮点击事件，这里可以获取输入框中的文本
                String inputText = textField.getText();
                System.out.println("Button clicked! Input Text: " + inputText);
            }
        });

        // Create a checkbox
        JCheckBox checkBox = new JCheckBox("Enable Feature");

        // Add an ActionListener to handle checkbox events
        checkBox.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Check the state of the checkbox
                boolean selected = checkBox.isSelected();

                // Perform actions based on the checkbox state
                if (selected) {
                    System.out.println("Feature is enabled");
                } else {
                    System.out.println("Feature is disabled");
                }
            }
        });

        JRadioButton radioButton1 = new JRadioButton("Option 1");
        JRadioButton radioButton2 = new JRadioButton("Option 2");
        JRadioButton radioButton3 = new JRadioButton("Option 3");

        // Create a ButtonGroup to make the radio buttons mutually exclusive
        ButtonGroup buttonGroup = new ButtonGroup();
        buttonGroup.add(radioButton1);
        buttonGroup.add(radioButton2);
        buttonGroup.add(radioButton3);


        // 将输入框和按钮添加到面板
        panel.add(textField);
        panel.add(button);

        // Add the checkbox to the panel
        panel.add(checkBox);

        panel.add(radioButton1);
        panel.add(radioButton2);
        panel.add(radioButton3);

        // 将面板添加到主窗口
        frame.add(panel);

        // 设置主窗口可见
        frame.setVisible(true);
    }
}
