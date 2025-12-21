import os
import sys
from pathlib import Path
import sqlite3
import time


from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
)
from PySide6.QtCore import QFile, QIODevice, QObject, Signal

from openai import OpenAI
from dotenv import load_dotenv

from models.ai import CreateCourseInput

load_dotenv()


class NewCourseWindow(QObject):
    course_was_created = Signal(int)

    def __init__(self, app: QApplication, db: sqlite3.Connection):
        super().__init__()
        self.app = app
        self.window: QMainWindow = None
        self.openai_client: OpenAI = None
        self.openai_url_input: QLineEdit = None
        self.openai_api_key_input: QLineEdit = None

        self.db = db
        self.cursor = self.db.cursor()

        ui_file_name = str(Path(__file__).parent / "new_course.ui")
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

        self.prompt_input = self.window.prompt_input
        assert isinstance(self.prompt_input, QPlainTextEdit)

        self.openai_url_input = self.window.openai_url_input
        assert isinstance(self.openai_url_input, QLineEdit)
        self.openai_url_input.setText(os.environ.get("OPENAI_BASE_URL", ""))

        self.openai_api_key_input = self.window.openai_api_key_input
        assert isinstance(self.openai_api_key_input, QLineEdit)
        self.openai_api_key_input.setText(os.environ.get("OPENAI_API_KEY", ""))

        self.submit_button = self.window.submit_button
        assert isinstance(self.submit_button, QPushButton)
        self.submit_button.clicked.connect(self.on_prompt_submitted)

    def on_prompt_submitted(self):
        self.openai_client = OpenAI(
            api_key=self.openai_api_key_input.text(),
            base_url=self.openai_url_input.text(),
        )
        prompt = self.prompt_input.toPlainText()
        response = self.openai_client.chat.completions.parse(
            # model="openai/gpt-oss-20b",
            model="gpt-5-mini",
            # model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a learning material generator that generates learning materials based on the user's prompt."
                    + " You will generate a list of 3-5 questions and answers that the user can use to learn the content."
                    + " Always generate multiple questions (at least 3) to provide comprehensive coverage of the topic.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=CreateCourseInput,
        )

        course = response.choices[0].message.parsed

        print(course)

        self.cursor.execute(
            "INSERT INTO course (name, description, created_at) VALUES (?, ?, ?)",
            (course.name, course.description, int(time.time())),
        )
        self.db.commit()
        course_id = self.cursor.lastrowid

        assert isinstance(course_id, int)

        for item in course.questions:
            self.cursor.execute(
                "INSERT INTO question (course_id, question, answer, choices, explanation, difficulty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    course_id,
                    item.question,
                    item.answer,
                    str(item.choices),
                    item.explanation,
                    item.difficulty,
                    int(time.time()),
                ),
            )

        self.db.commit()

        self.course_was_created.emit(course_id)

        self.window.close()
