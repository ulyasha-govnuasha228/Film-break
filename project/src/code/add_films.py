from PyQt6.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from ..ui_forms.add_dialog import Ui_Dialog
from PyQt6.QtCore import Qt


class AddDialog(QDialog, Ui_Dialog):
    def __init__(self, con, cur):
        super().__init__()
        self.setupUi(self)
        self.poster_path = None
        self.btn_poster.clicked.connect(self.choose_poster)
        self.con = con
        self.cur = cur

        self.combo_type.clear()
        self.combo_type.addItems(["Фильм", "Сериал", "Мультфильм", "Аниме"])

        self.combo_age.clear()
        self.combo_age.addItems(["0+", "6+", "12+", "16+", "18+"])

        self.buttons.accepted.connect(self.save_data)

    def choose_poster(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите постер", "", "Изображения (*.png *.jpg *.jpeg *.webp)")

        if file_path:
            self.poster_path = file_path
            pixmap = QPixmap(file_path)
            self.label_poster.setPixmap(pixmap.scaled(self.label_poster.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.label_poster.setText("")

    def get_or_create_person(self, table, id_column, name_column, name_text):
        self.cur.execute(
            f"SELECT {id_column} FROM {table} WHERE {name_column} = ?",
            (name_text,)
        )
        row = self.cur.fetchone()

        if row:
            return row[0]

        self.cur.execute(
            f"INSERT INTO {table} ({name_column}) VALUES (?)",
            (name_text,)
        )
        self.con.commit()
        return self.cur.lastrowid

    def save_data(self):
        title = self.line_name.text().strip()
        year_text = self.line_year.text().strip()
        desc = self.text_description.toPlainText().strip()
        film_type = self.combo_type.currentText()
        age_rating = self.combo_age.currentText()
        actors_text = self.line_actors.text().strip()
        directors_text = self.line_directors.text().strip()

        if not title or not year_text:
            QMessageBox.warning(self, "Ошибка", "Название и год обязательны!")
            return

        try:
            year = int(year_text)
            if year < 1888 or year > 2100:
                QMessageBox.warning(self, "Ошибка", "Введите корректный год!")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Год должен быть числом!")
            return

        try:
            self.cur.execute(
                "INSERT OR IGNORE INTO films (title, release_year, description, film_type, age_rating) VALUES (?, ?, ?, ?, ?)",
                (title, year, desc, film_type, age_rating)
            )
            self.con.commit()

            self.cur.execute(
                "SELECT film_id FROM films WHERE title = ? AND release_year = ?",
                (title, year)
            )
            row = self.cur.fetchone()

            if not row:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить фильм.")
                return

            film_id = row[0]

            if actors_text:
                for actor in [a.strip() for a in actors_text.split(",") if a.strip()]:
                    actor_id = self.get_or_create_person(
                        "actors", "actor_id", "actor_name", actor
                    )
                    self.cur.execute(
                        "INSERT OR IGNORE INTO filmactors (film_id, actor_id) VALUES (?, ?)",
                        (film_id, actor_id)
                    )

            if directors_text:
                for director in [d.strip() for d in directors_text.split(",") if d.strip()]:
                    director_id = self.get_or_create_person(
                        "directors", "director_id", "director_name", director
                    )
                    self.cur.execute(
                        "INSERT OR IGNORE INTO filmdirectors (film_id, director_id) VALUES (?, ?)",
                        (film_id, director_id)
                    )

            self.con.commit()
            QMessageBox.information(self, "Успех", "Фильм успешно добавлен!")
            self.accept()

        except Exception as e:
            self.con.rollback()
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить фильм:\n{e}")
