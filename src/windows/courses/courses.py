import sys
from pathlib import Path
import sqlite3


from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)
from PySide6.QtCore import QFile, QIODevice, QObject, Signal, Slot

from dotenv import load_dotenv

load_dotenv()


class CoursesWindow(QObject):
    open_new_course_window = Signal()
    open_course_window = Signal(int)

    def __init__(self, app: QApplication, db: sqlite3.Connection):
        super().__init__()
        self.app = app
        self.window: QMainWindow = None
        self.courses_scroll_area: QScrollArea = None

        self.db = db
        self.cursor = self.db.cursor()

        ui_file_name = str(Path(__file__).parent / "courses.ui")
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

        self.new_course_button = self.window.new_course_button
        assert isinstance(self.new_course_button, QPushButton)
        self.new_course_button.clicked.connect(self.on_new_course_clicked)

        self.courses_scroll_area = self.window.courses_scroll_area
        assert isinstance(self.courses_scroll_area, QScrollArea)

        self.load_courses()

    def load_courses(self):
        self.cursor.execute(
            "SELECT id, name FROM course ORDER BY created_at DESC",
        )
        courses = self.cursor.fetchall()
        print(courses)
        self.courses_scroll_area.setLayout(QVBoxLayout())
        for course in courses:
            button = QPushButton(course[1])
            button.clicked.connect(
                lambda _, course_id=course[0]: self.on_course_clicked(course_id)
            )
            self.courses_scroll_area.layout().addWidget(button)

    def on_new_course_clicked(self):
        self.open_new_course_window.emit()

    def on_course_clicked(self, course_id: int):
        self.window.hide()
        self.open_course_window.emit(course_id)

    @Slot(int)
    def on_course_created(self, course_id: int):
        self.load_courses()
