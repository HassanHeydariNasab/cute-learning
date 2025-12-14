from pathlib import Path
import sqlite3
import sys
from PySide6.QtWidgets import QApplication

from windows.courses import CoursesWindow
from windows.new_course import NewCourseWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    db = sqlite3.connect(Path(__file__).parent / "db.sqlite3")
    cursor = db.cursor()

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS course (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            """
    )
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                choices TEXT NOT NULL,
                explanation TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
            );
            """
    )
    db.commit()

    courses = db.execute(
        "SELECT id, name FROM course ORDER BY created_at DESC"
    ).fetchall()

    newCourseWindow = NewCourseWindow(app, db)
    coursesWindow = CoursesWindow(app, db)

    newCourseWindow.created_course.connect(coursesWindow.on_course_created)
    coursesWindow.open_new_course_window.connect(newCourseWindow.window.show)

    coursesWindow.window.show()

    if len(courses) == 0:
        newCourseWindow.window.show()

    sys.exit(app.exec())
