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
        primaryStage.setTitle("JavaFX Example");
        primaryStage.setScene(scene);

        TextField textField = new TextField();

        Button button = new Button("Click");

        button.setOnAction(e -> {
            String inputText = textField.getText();
            System.out.println("Input Text: " + inputText);
        });

        CheckBox checkBox =new CheckBox("Enable Feature");

        ToggleGroup toggleGroup = new ToggleGroup();
        RadioButton radioButton1 = new RadioButton("Option 1");
        RadioButton radioButton2 = new RadioButton("Option 2");
        RadioButton radioButton3 = new RadioButton("Option 3");
        radioButton1.setToggleGroup(toggleGroup);
        radioButton2.setToggleGroup(toggleGroup);
        radioButton3.setToggleGroup(toggleGroup);
        toggleGroup.selectToggle(radioButton1);

        VBox layout = new VBox(10);
        layout.getChildren().addAll(textField, button, checkBox, radioButton1, radioButton2, radioButton3);

        Scene scene = new Scene(layout, 300, 200);

        primaryStage.show();
    }
}
