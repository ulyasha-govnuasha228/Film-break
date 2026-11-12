
import sqlite3
import csv
import os

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QDialog,
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from ..ui_forms.watchlater_window import Ui_Form as Ui_Watchlist


class WatchedPage(QWidget):
    def __init__(self, user_id, con, cur):
        super().__init__()
        self.user_id = user_id
        self.con = con
        self.cur = cur

        self.ui = Ui_Watchlist()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.choose_film)

        self.export_button = QPushButton("Экспортировать в CSV")
        self.layout().addWidget(self.export_button)
        self.export_button.clicked.connect(self.export_csv)

    def open_page(self):
        self.load_watched()

    def load_watched(self):
        layout = self.ui.scrollAreaWidgetContents.layout()

        if layout is None:
            layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cur.execute(
            "SELECT f.film_id, f.title, f.release_year "
            "FROM watchedfilms w "
            "JOIN films f ON f.film_id = w.film_id "
            "WHERE w.user_id = ? "
            "ORDER BY f.title",
            (self.user_id,)
        )

        films = self.cur.fetchall()

        if not films:
            label = QLabel("Вы пока не добавили просмотренные фильмы")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; color: white;")
            layout.addWidget(label)

        for film_id, title, year in films:
            button = QPushButton(f"{title} ({year})")
            button.setMinimumHeight(45)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(40, 40, 40, 180);
                    color: white;
                    border: 1px solid #888;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 15px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(90, 90, 90, 200);
                }
            """)
            button.clicked.connect(
                lambda checked=False, fid=film_id: self.show_film(fid, False)
            )
            layout.addWidget(button)

        layout.addStretch()

    def choose_film(self):
        self.cur.execute(
            "SELECT film_id, title, release_year FROM films ORDER BY title"
        )
        films = self.cur.fetchall()

        if not films:
            QMessageBox.warning(self, "Ошибка", "В каталоге пока нет фильмов!")
            return

        titles = [f"{film[1]} ({film[2]})" for film in films]

        title, ok = QInputDialog.getItem(
            self, "Просмотрено", "Выберите фильм:", titles, 0, False
        )

        if ok and title:
            film_id = films[titles.index(title)][0]

            self.cur.execute(
                "SELECT id FROM watchedfilms WHERE user_id = ? AND film_id = ?",
                (self.user_id, film_id)
            )

            if self.cur.fetchone():
                QMessageBox.warning(self, "Ошибка", "Этот фильм уже просмотрен!")
                return

            self.show_film(film_id, True)

    def show_film(self, film_id, can_add):
        self.cur.execute(
            """
            SELECT f.title, f.release_year, f.description,
                   f.poster_path, f.film_type, f.age_rating,
                   (SELECT group_concat(a.actor_name, ', ')
                    FROM filmactors fa
                    JOIN actors a ON a.actor_id = fa.actor_id
                    WHERE fa.film_id = f.film_id),
                   (SELECT group_concat(d.director_name, ', ')
                    FROM filmdirectors fd
                    JOIN directors d ON d.director_id = fd.director_id
                    WHERE fd.film_id = f.film_id)
            FROM films f
            WHERE f.film_id = ?
            """,
            (film_id,)
        )

        film = self.cur.fetchone()

        if not film:
            return

        title, year, description, poster, film_type, age, actors, directors = film

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(450, 550)

        layout = QVBoxLayout(dialog)

        if poster and os.path.exists(poster):
            image = QLabel()
            pixmap = QPixmap(poster)
            image.setPixmap(
                pixmap.scaled(
                    200, 280,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image)

        info = QLabel(
            f"<h2>{title} ({year})</h2>"
            f"<b>Тип:</b> {film_type or 'Не указан'}<br>"
            f"<b>Возраст:</b> {age or 'Не указан'}<br>"
            f"<b>Режиссёр:</b> {directors or 'Не указан'}<br>"
            f"<b>Актёры:</b> {actors or 'Не указаны'}<br><br>"
            f"<b>Описание:</b><br>{description or 'Описание отсутствует'}"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        if can_add:
            add_button = QPushButton("Добавить в просмотренное")
            layout.addWidget(add_button)

            def add_film():
                try:
                    self.cur.execute(
                        "INSERT INTO watchedfilms (user_id, film_id) VALUES (?, ?)",
                        (self.user_id, film_id)
                    )
                    self.con.commit()
                    dialog.accept()
                    self.load_watched()
                    QMessageBox.information(
                        self, "Готово", "Фильм добавлен в просмотренное!"
                    )

                except sqlite3.Error as e:
                    self.con.rollback()
                    QMessageBox.warning(self, "Ошибка", str(e))

            add_button.clicked.connect(add_film)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить список просмотренного",
            "watched_films.csv",
            "CSV-файлы (*.csv)"
        )

        if not file_path:
            return

        self.cur.execute(
            """
            SELECT f.title, f.release_year, f.film_type, w.rating
            FROM watchedfilms w
            JOIN films f ON f.film_id = w.film_id
            WHERE w.user_id = ?
            ORDER BY f.title
            """,
            (self.user_id,)
        )

        films = self.cur.fetchall()

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(["Название", "Год", "Тип", "Оценка"])
                writer.writerows(films)

            QMessageBox.information(
                self, "Готово", "Список просмотренного сохранён в CSV!"
            )

        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
