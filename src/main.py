import os
import sys
from pathlib import Path


from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
)
from PySide6.QtCore import QFile, QIODevice

from openai import OpenAI
from dotenv import load_dotenv

from models.ai import Learning

load_dotenv()


class MainWindow:
    def __init__(self, app: QApplication):
        self.app = app
        self.window: QMainWindow = None
        self.openai_client: OpenAI = None
        self.openai_url_input: QLineEdit = None
        self.openai_api_key_input: QLineEdit = None

        ui_file_name = str(Path(__file__).parent / "main.ui")
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.promptInput = self.window.promptInput
        assert isinstance(self.promptInput, QPlainTextEdit)

        self.openai_url_input = self.window.openaiUrlInput
        assert isinstance(self.openai_url_input, QLineEdit)
        self.openai_url_input.setText(os.environ.get("OPENAI_BASE_URL", ""))

        self.openai_api_key_input = self.window.openaiApiKeyInput
        assert isinstance(self.openai_api_key_input, QLineEdit)
        self.openai_api_key_input.setText(os.environ.get("OPENAI_API_KEY", ""))

        self.submitButton = self.window.submitButton
        assert isinstance(self.submitButton, QPushButton)
        self.submitButton.clicked.connect(self.on_prompt_submitted)

    def on_prompt_submitted(self):
        self.openai_client = OpenAI(
            api_key=self.openai_api_key_input.text(),
            base_url=self.openai_url_input.text(),
        )
        response = self.openai_client.chat.completions.parse(
            # model="openai/gpt-oss-20b",
            model="gpt-5-mini",
            # model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a learning materials generator that generates learning materials based on the user's prompt."
                    + " You will generate a list of 3-5 questions and answers that the user can use to learn the content."
                    + " Always generate multiple items (at least 3) to provide comprehensive coverage of the topic.",
                },
                {"role": "user", "content": self.promptInput.toPlainText()},
            ],
            response_format=Learning,
        )
        print(response.choices[0].message.parsed)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MainWindow(app)
    mainWindow.window.show()

    sys.exit(app.exec())
