import sys
from pathlib import Path
import sqlite3
import json


from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QFile, QIODevice, QObject, Slot, Signal

from dotenv import load_dotenv

from models.db import Course, Question

load_dotenv()


class CourseWindowWidget:
    WELCOME = 0
    QUESTION_FORM = 1
    ANSWER_FORM = 2


class CourseWindow(QObject):
    open_new_course_window = Signal()
    open_courses_window = Signal()

    def __init__(self, app: QApplication, db: sqlite3.Connection):
        super().__init__()
        self.app = app
        self.window: QMainWindow = None
        self.course: Course = None
        self.question: Question = None
        self.questions: list[Question] = []

        self.welcome: QWidget = None
        self.new_course_button: QPushButton = None
        self.courses_button: QPushButton = None

        self.question_form: QWidget = None
        self.question_form_layout: QVBoxLayout = None
        self.question_form_question: QLabel = None
        self.question_form_choice0: QPushButton = None
        self.question_form_choice1: QPushButton = None
        self.question_form_choice2: QPushButton = None
        self.question_form_choice3: QPushButton = None

        self.answer_form: QWidget = None
        self.answer_form_layout: QGridLayout = None
        self.answer_form_answer: QLabel = None
        self.answer_form_explanation: QLabel = None
        self.answer_form_incorrect_answer: QLabel = None
        self.answer_form_continue_button: QPushButton = None

        self.stacked_widget: QStackedWidget = None

        self.db = db
        self.cursor = self.db.cursor()

        ui_file_name = str(Path(__file__).parent / "course.ui")
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

        self.stacked_widget = self.window.stacked_widget
        assert isinstance(self.stacked_widget, QStackedWidget)

        ui_file_name = str(Path(__file__).parent / "welcome.ui")
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.welcome = loader.load(ui_file)
        ui_file.close()
        if not self.welcome:
            print(loader.errorString())
            sys.exit(-1)

        self.new_course_button = self.welcome.new_course_button
        assert isinstance(self.new_course_button, QPushButton)
        self.new_course_button.clicked.connect(self.on_new_course_clicked)

        self.courses_button = self.welcome.courses_button
        assert isinstance(self.courses_button, QPushButton)
        self.courses_button.clicked.connect(self.on_courses_clicked)

        question_form_file_name = str(Path(__file__).parent / "questionForm.ui")
        question_form_file = QFile(question_form_file_name)
        if not question_form_file.open(QIODevice.ReadOnly):
            print(
                f"Cannot open {question_form_file_name}: {question_form_file.errorString()}"
            )
            sys.exit(-1)
        loader = QUiLoader()
        self.question_form = loader.load(question_form_file)
        question_form_file.close()
        if not self.question_form:
            print(loader.errorString())
            sys.exit(-1)

        self.question_form_layout = self.question_form.layout()
        assert isinstance(self.question_form_layout, QVBoxLayout)

        self.question_form_question = self.question_form.question
        assert isinstance(self.question_form_question, QLabel)

        self.question_form_choice0 = self.question_form.choice0
        assert isinstance(self.question_form_choice0, QPushButton)

        self.question_form_choice1 = self.question_form.choice1
        assert isinstance(self.question_form_choice1, QPushButton)

        self.question_form_choice2 = self.question_form.choice2
        assert isinstance(self.question_form_choice2, QPushButton)

        self.question_form_choice3 = self.question_form.choice3
        assert isinstance(self.question_form_choice3, QPushButton)

        self.question_form_choice0.clicked.connect(lambda: self.on_choice_clicked(0))
        self.question_form_choice1.clicked.connect(lambda: self.on_choice_clicked(1))
        self.question_form_choice2.clicked.connect(lambda: self.on_choice_clicked(2))
        self.question_form_choice3.clicked.connect(lambda: self.on_choice_clicked(3))

        answer_form_file_name = str(Path(__file__).parent / "answerForm.ui")
        answer_form_file = QFile(answer_form_file_name)
        if not answer_form_file.open(QIODevice.ReadOnly):
            print(
                f"Cannot open {answer_form_file_name}: {answer_form_file.errorString()}"
            )
            sys.exit(-1)
        loader = QUiLoader()
        self.answer_form = loader.load(answer_form_file)
        answer_form_file.close()
        if not self.answer_form:
            print(loader.errorString())
            sys.exit(-1)

        self.answer_form_layout = self.answer_form.layout()
        assert isinstance(self.answer_form_layout, QGridLayout)

        self.answer_form_answer = self.answer_form.answer
        assert isinstance(self.answer_form_answer, QLabel)

        self.answer_form_explanation = self.answer_form.explanation
        assert isinstance(self.answer_form_explanation, QLabel)

        self.answer_form_incorrect_answer = self.answer_form.incorrect_answer
        assert isinstance(self.answer_form_incorrect_answer, QLabel)

        self.answer_form_continue_button = self.answer_form.continue_button
        assert isinstance(self.answer_form_continue_button, QPushButton)
        self.answer_form_continue_button.clicked.connect(self.load_next_question)

        self.stacked_widget.insertWidget(CourseWindowWidget.WELCOME, self.welcome)
        self.stacked_widget.insertWidget(
            CourseWindowWidget.QUESTION_FORM, self.question_form
        )
        self.stacked_widget.insertWidget(
            CourseWindowWidget.ANSWER_FORM, self.answer_form
        )
        self.stacked_widget.setCurrentIndex(CourseWindowWidget.WELCOME)

    def fetch_course(self, course_id: int):
        self.cursor.execute(
            "SELECT id, name, description, created_at FROM course WHERE id = ?",
            (course_id,),
        )
        course = self.cursor.fetchone()
        if course:
            return Course(
                id=course[0],
                name=course[1],
                description=course[2],
                created_at=course[3],
            )
        else:
            return None

    def fetch_questions(self, course_id: int):
        self.cursor.execute(
            "SELECT id, question, answer, choices, explanation, difficulty, created_at, course_id FROM question WHERE course_id = ?",
            (course_id,),
        )
        questions = self.cursor.fetchall()

        return list(
            map(
                lambda question: Question(
                    id=question[0],
                    question=question[1],
                    answer=question[2],
                    choices=json.loads(question[3].replace("'", '"')),
                    explanation=question[4],
                    difficulty=question[5],
                    created_at=question[6],
                    course_id=question[7],
                ),
                questions,
            )
        )

    @Slot()
    def load_course(self, course_id: int):
        course = self.fetch_course(course_id)
        self.questions = self.fetch_questions(course_id)
        if course is not None and len(self.questions) > 0:
            self.stacked_widget.setCurrentIndex(CourseWindowWidget.QUESTION_FORM)
            self.window.setWindowTitle(course.name)

            # TODO: shuffle
            self.answer_form_continue_button.clicked.connect(self.load_next_question)
            self.load_next_question()
            self.window.show()
        else:
            dialog = QDialog()
            dialog.setWindowTitle("No questions found")
            dialog.show()

    @Slot()
    def load_next_question(self):
        if len(self.questions) > 0:
            self.question = self.questions.pop(0)

            self.question_form_question.setText(self.question.question)

            self.question_form_choice0.setVisible(False)
            self.question_form_choice1.setVisible(False)
            self.question_form_choice2.setVisible(False)
            self.question_form_choice3.setVisible(False)

            if len(self.question.choices) > 0:
                self.question_form_choice0.setText(self.question.choices[0])
                self.question_form_choice0.setVisible(True)
            if len(self.question.choices) > 1:
                self.question_form_choice1.setText(self.question.choices[1])
                self.question_form_choice1.setVisible(True)
            if len(self.question.choices) > 2:
                self.question_form_choice2.setText(self.question.choices[2])
                self.question_form_choice2.setVisible(True)
            if len(self.question.choices) > 3:
                self.question_form_choice3.setText(self.question.choices[3])
                self.question_form_choice3.setVisible(True)

            self.answer_form_answer.setText(self.question.answer)
            self.answer_form_explanation.setText(self.question.explanation)
            self.answer_form_incorrect_answer.setVisible(False)

            self.stacked_widget.setCurrentIndex(CourseWindowWidget.QUESTION_FORM)
        else:
            self.stacked_widget.setCurrentIndex(CourseWindowWidget.WELCOME)

    def on_choice_clicked(self, choice_index: int):
        self.answer_form_answer.setText(self.question.answer)
        self.answer_form_explanation.setText(self.question.explanation)

        if self.question.choices[choice_index] == self.question.answer:
            self.answer_form_incorrect_answer.setVisible(False)
        else:
            self.answer_form_incorrect_answer.setText(
                self.question.choices[choice_index]
            )
            self.answer_form_incorrect_answer.setVisible(True)
        self.stacked_widget.setCurrentIndex(CourseWindowWidget.ANSWER_FORM)

    def on_new_course_clicked(self):
        self.open_new_course_window.emit()

    def on_courses_clicked(self):
        self.open_courses_window.emit()
