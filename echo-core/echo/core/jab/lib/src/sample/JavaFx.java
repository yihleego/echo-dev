import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

public class JavaFx extends Application {

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        // 创建一个文本输入框
        TextField textField = new TextField();

        // 创建一个按钮
        Button button = new Button("Click");

        // 设置按钮点击事件
        button.setOnAction(e -> {
            String inputText = textField.getText();
            System.out.println("用户输入: " + inputText);
        });

        CheckBox checkBox =new CheckBox("Haha");

        // Create a ToggleGroup to group the radio buttons
        ToggleGroup toggleGroup = new ToggleGroup();

        // Create RadioButtons
        RadioButton radioButton1 = new RadioButton("Option 1");
        radioButton1.setToggleGroup(toggleGroup); // Add to the ToggleGroup

        RadioButton radioButton2 = new RadioButton("Option 2");
        radioButton2.setToggleGroup(toggleGroup); // Add to the ToggleGroup

        RadioButton radioButton3 = new RadioButton("Option 3");
        radioButton3.setToggleGroup(toggleGroup); // Add to the ToggleGroup

        // Set default selection (optional)
        toggleGroup.selectToggle(radioButton1);

        // 创建一个垂直布局并将输入框和按钮添加到其中
        VBox layout = new VBox(10);
        layout.getChildren().addAll(textField, button, checkBox, radioButton1, radioButton2, radioButton3);

        // 创建场景并将布局添加到场景中
        Scene scene = new Scene(layout, 300, 200);

        // 设置舞台的标题和场景
        primaryStage.setTitle("Simple FX");
        primaryStage.setScene(scene);

        // 显示舞台
        primaryStage.show();
    }
}
