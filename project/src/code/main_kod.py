from PyQt6.QtWidgets import QStackedWidget
import sqlite3
from .watched import WatchedPage
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QDate, Qt, QSize
import os
from .add_films import AddDialog
from PyQt6.QtWidgets import (QMainWindow, QWidget, QComboBox, QCompleter, QMessageBox, QAbstractSpinBox, QLabel, QVBoxLayout, QPushButton, QInputDialog, QDialog, QRadioButton)
from ..ui_forms.main_okno import Ui_MainWindow
from ..ui_forms.profile_window import Ui_Form_profile
from ..ui_forms.watchlater_window import Ui_Form as Ui_Watchlist


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, user_id, con=None, cur=None):
        super().__init__()
        self.user_id = user_id
        self.con = con
        self.cur = cur
        self.setupUi(self)

        self.cur.execute("SELECT name FROM users WHERE id = ?", (self.user_id,))
        user_row = self.cur.fetchone()

        if user_row:
            self.label.setText(f"Здравствуйте, {user_row[0]}!")
            self.label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, 'src', 'images', 'background_registration.png').replace('\\', '/')

        self.setStyleSheet(f"""
            QMainWindow {{
                background-image: url("{bg_path}");
                background-repeat: no-repeat;
                background-position: center;
            }}
            QWidget {{
                background-color: transparent;
            }}
            QMessageBox, QDialog {{ background-color: white; }}
            QMessageBox QLabel, QDialog QLabel {{ color: black; }}
            QMessageBox QPushButton, QDialog QPushButton {{ background-color: #e0e0e0; color: black; }}
        """)

        self.initUI()
        self.setup_profile_combos()
        self.load_all_favorites()

    def initUI(self):
        self.home_page = self.centralWidget()

        self.profile_page = QWidget()
        self.profile_ui = Ui_Form_profile()
        self.profile_ui.setupUi(self.profile_page)

        self.watchlist_page = QWidget()
        self.watchlist_ui = Ui_Watchlist()
        self.watchlist_ui.setupUi(self.watchlist_page)
        self.watchlist_ui.pushButton.clicked.connect(self.add_to_watchlist_dialog)
        self.watched_page = WatchedPage(self.user_id, self.con, self.cur)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.profile_page)
        self.pages.addWidget(self.watchlist_page)
        self.pages.addWidget(self.watched_page)

        self.setCentralWidget(self.pages)

        self.profile_ui.btn_settings.clicked.connect(self.open_settings)
        self.profile_ui.dateedit.setReadOnly(True)
        self.profile_ui.dateedit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.btn_profile.triggered.connect(self.open_profile)
        self.btn_watched.triggered.connect(self.open_watchlist)
        self.btn_realwatched.triggered.connect(self.open_watched)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        images_dir = os.path.join(base_dir, 'src', 'images')

        self.btn_watched.setIcon(QIcon(os.path.join(images_dir, 'popcorn.webp')))
        self.btn_profile.setIcon(QIcon(os.path.join(images_dir, 'photka.png')))
        self.btn_realwatched.setIcon(QIcon(os.path.join(images_dir, 'cup_game_geek_minecraft_mug_video_icon_183182-edited-free (carve.photos).png')))

        self.setIconSize(QSize(32, 32))
        
    def open_watchlist(self):
        self.pages.setCurrentWidget(self.watchlist_page)
        self.load_watchlist()

    def load_watchlist(self):
        scroll_content = self.watchlist_ui.scrollAreaWidgetContents
        layout = scroll_content.layout()

        if layout is None:
            layout = QVBoxLayout(scroll_content)

        while layout.count():
            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        self.cur.execute(
            "SELECT f.film_id, f.title, f.release_year "
            "FROM watchlist w "
            "JOIN films f ON f.film_id = w.film_id "
            "WHERE w.user_id = ? "
            "ORDER BY f.title",
            (self.user_id,)
        )

        movies = self.cur.fetchall()

        if not movies:
            label = QLabel("Ваш список пока пуст")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; color: white;")
            layout.addWidget(label)
        else:
            for film_id, title, year in movies:
                button = QPushButton(f"{title} ({year})")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setMinimumHeight(45)
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
                    lambda checked=False, fid=film_id: self.remove_from_watchlist(fid)
                )
                layout.addWidget(button)

        layout.addStretch()

    def add_to_watchlist_dialog(self):
        self.cur.execute(
            "SELECT film_id, title, release_year FROM films ORDER BY title"
        )
        films = self.cur.fetchall()

        if not films:
            QMessageBox.warning(self, "Ошибка", "В базе пока нет фильмов!")
            return

        film_titles = [f"{f[1]} ({f[2]})" for f in films]

        title, ok = QInputDialog.getItem(
            self,
            "Хочу посмотреть",
            "Выберите фильм:",
            film_titles,
            0,
            False
        )

        if ok and title:
            film_id = films[film_titles.index(title)][0]

            self.cur.execute(
                "SELECT film_id FROM watchlist WHERE user_id = ? AND film_id = ?",
                (self.user_id, film_id)
            )

            if self.cur.fetchone():
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Этот фильм уже есть в вашем списке!"
                )
                return

            try:
                self.cur.execute(
                    "INSERT INTO watchlist (user_id, film_id) VALUES (?, ?)",
                    (self.user_id, film_id)
                )
                self.con.commit()
                self.load_watchlist()

            except sqlite3.Error as e:
                self.con.rollback()
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось добавить фильм:\n{e}"
                )

    def remove_from_watchlist(self, film_id):
        reply = QMessageBox.question(
            self,
            "Удалить фильм?",
            'Вы уверены, что хотите удалить этот фильм из списка "Хочу посмотреть"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cur.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND film_id = ?",
                (self.user_id, film_id)
            )
            self.con.commit()
            self.load_watchlist()

    def open_watched(self):
        self.pages.setCurrentWidget(self.watched_page)
        self.watched_page.open_page()

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки темы")
        dialog.setFixedSize(250, 150)
        dialog.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: black; }
            QRadioButton { color: black; }
            QPushButton {
                background-color: #ddd;
                color: black;
                border: 1px solid #999;
            }
        """)

        layout = QVBoxLayout(dialog)

        lbl = QLabel("Выберите цветовую тему:")
        layout.addWidget(lbl)

        radio_pink = QRadioButton("Розовая тема")
        radio_blue = QRadioButton("Голубая тема")

        layout.addWidget(radio_pink)
        layout.addWidget(radio_blue)

        btn_apply = QPushButton("Применить")
        layout.addWidget(btn_apply)

        def apply_theme():
            if radio_pink.isChecked():
                self.setStyleSheet("""
                    QWidget { background-color: #ffd1dc; color: #333; }
                    QPushButton {
                        background-color: #ff69b4;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QLineEdit, QComboBox, QTextEdit, QScrollArea {
                        background-color: #ffe4e1;
                        color: #333;
                    }
                """)

            elif radio_blue.isChecked():
                self.setStyleSheet("""
                    QWidget { background-color: #e0f7fa; color: #333; }
                    QPushButton {
                        background-color: #00bcd4;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QLineEdit, QComboBox, QTextEdit, QScrollArea {
                        background-color: #f0f8ff;
                        color: #333;
                    }
                """)

            dialog.accept()

        btn_apply.clicked.connect(apply_theme)
        dialog.exec()

    def setup_profile_combos(self):
        self.film_combos = [
            self.profile_ui.btn_film,
            self.profile_ui.btn_film2,
            self.profile_ui.btn_film3
        ]

        self.actor_combos = [
            self.profile_ui.btn_actor,
            self.profile_ui.btn_actor2,
            self.profile_ui.btn_actor3
        ]

        self.dir_combos = [
            self.profile_ui.btn_reg,
            self.profile_ui.btn_reg2,
            self.profile_ui.btn_reg3
        ]

        self.scen_combos = [
            self.profile_ui.btn_scen,
            self.profile_ui.btn_scen2,
            self.profile_ui.btn_scen3
        ]

        self.other_combos = [
            self.profile_ui.btn_uch,
            self.profile_ui.btn_uch2,
            self.profile_ui.btn_uch3
        ]

        for combo in self.film_combos:
            self.setup_combo_search(combo)
            combo.activated.connect(
                lambda _, c=combo: self.save_favorite('userfavoritefilms', 'film_id', c)
            )

        for combo in self.actor_combos:
            self.setup_combo_search(combo)
            combo.activated.connect(
                lambda _, c=combo: self.save_favorite('userfavoriteactors', 'actor_id', c)
            )

        for combo in self.dir_combos:
            self.setup_combo_search(combo)
            combo.activated.connect(
                lambda _, c=combo: self.save_favorite('userfavoritedirectors', 'director_id', c)
            )

        for combo in self.scen_combos:
            self.setup_combo_search(combo)
            combo.activated.connect(
                lambda _, c=combo: self.save_favorite('userfavoritescreenwriters', 'screenwriter_id', c)
            )

        for combo in self.other_combos:
            self.setup_combo_search(combo)
            combo.activated.connect(
                lambda _, c=combo: self.save_favorite('userfavoriteotherpeople', 'person_id', c)
            )

    def setup_combo_search(self, combo):
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        completer = QCompleter(combo.model(), combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        combo.setCompleter(completer)
        combo.activated.connect(lambda: combo.setEditable(False))

    def open_profile(self):
        self.pages.setCurrentWidget(self.profile_page)

        self.cur.execute(
            "SELECT name, nickname, phone, birth_date, avatar_path "
            "FROM users WHERE id = ?",
            (self.user_id,)
        )

        row = self.cur.fetchone()

        if row:
            name, nickname, phone, birth_date, avatar_path = row

            self.profile_ui.label_nickname.setText(nickname)
            self.profile_ui.label_name.setText(name)
            self.profile_ui.label_number.setText(phone)
            self.profile_ui.dateedit.setDate(
                QDate.fromString(birth_date, "yyyy-MM-dd")
            )

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            default_avatar = os.path.join(base_dir, 'src', 'images', 'photo_profile.png')

            if avatar_path and os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
            else:
                pixmap = QPixmap(default_avatar)

            self.profile_ui.label.setPixmap(pixmap)
            self.profile_ui.label.setScaledContents(True)

    def save_favorite(self, table, id_column, combo):
        text = combo.currentText().strip()
        item_id = combo.currentData()

        if not text and item_id is None:
            return

        if item_id is None:
            if table == "userfavoritefilms":
                items_table = "films"
                name_column = "title"
            elif table == "userfavoriteactors":
                items_table = "actors"
                name_column = "actor_name"
            elif table == "userfavoritedirectors":
                items_table = "directors"
                name_column = "director_name"
            elif table == "userfavoritescreenwriters":
                items_table = "screenwriters"
                name_column = "screenwriter_name"
            else:
                items_table = "otherfilmpeople"
                name_column = "person_name"

            self.cur.execute(
                f"SELECT {id_column} FROM {items_table} WHERE {name_column} = ?",
                (text,)
            )

            row = self.cur.fetchone()

            if row:
                item_id = row[0]
            else:
                try:
                    if items_table == "films":
                        self.cur.execute(
                            "INSERT INTO films(title, release_year, description, film_type, age_rating) VALUES(?, 0, '', 'Фильм', '0+')",
                            (text,)
                        )
                    else:
                        self.cur.execute(
                            f"INSERT INTO {items_table}({name_column}) VALUES(?)",
                            (text,)
                        )

                    self.con.commit()
                    item_id = self.cur.lastrowid

                except sqlite3.IntegrityError:
                    self.cur.execute(
                        f"SELECT {id_column} FROM {items_table} WHERE {name_column} = ?",
                        (text,)
                    )
                    row = self.cur.fetchone()
                    item_id = row[0] if row else None

        if item_id is None:
            return

        try:
            self.cur.execute(
                f"INSERT INTO {table}(user_id, {id_column}) VALUES(?, ?)",
                (self.user_id, item_id)
            )
            self.con.commit()

        except sqlite3.IntegrityError:
            pass

        self.load_all_favorites()

    def _fill_available(self, combo, favorites_table, id_column, items_table, name_column):
        if items_table == "films":
            query = (
                f"SELECT i.{id_column}, i.{name_column}, i.release_year "
                f"FROM {items_table} i "
                f"WHERE i.{id_column} NOT IN "
                f"(SELECT {id_column} FROM {favorites_table} WHERE user_id = ?) "
                f"ORDER BY i.{name_column}"
            )

            self.cur.execute(query, (self.user_id,))
            rows = self.cur.fetchall()

            combo.clear()

            for item_id, name, year in rows:
                combo.addItem(f"{name} ({year})", item_id)

        else:
            query = (
                f"SELECT i.{id_column}, i.{name_column} "
                f"FROM {items_table} i "
                f"WHERE i.{id_column} NOT IN "
                f"(SELECT {id_column} FROM {favorites_table} WHERE user_id = ?) "
                f"ORDER BY i.{name_column}"
            )

            self.cur.execute(query, (self.user_id,))
            rows = self.cur.fetchall()

            combo.clear()

            for item_id, name in rows:
                combo.addItem(name, item_id)

        combo.setCurrentIndex(-1)
        self.setup_combo_search(combo)

    def load_all_favorites(self):
        self.load_films()
        self.load_actors()
        self.load_directors()
        self.load_screenwriters()
        self.load_otherpeople()

    def load_films(self):
        self.cur.execute(
            "SELECT i.film_id, i.title, i.release_year "
            "FROM userfavoritefilms uf "
            "JOIN films i ON i.film_id = uf.film_id "
            "WHERE uf.user_id = ? "
            "ORDER BY i.title",
            (self.user_id,)
        )

        favs = self.cur.fetchall()

        for idx, combo in enumerate(self.film_combos):
            combo.clear()

            if idx < len(favs):
                combo.addItem(
                    f"{favs[idx][1]} ({favs[idx][2]})",
                    favs[idx][0]
                )
                combo.setCurrentIndex(0)
                combo.setEditable(False)

            else:
                self._fill_available(
                    combo,
                    'userfavoritefilms',
                    'film_id',
                    'films',
                    'title'
                )

    def load_actors(self):
        self.cur.execute(
            "SELECT i.actor_id, i.actor_name "
            "FROM userfavoriteactors uf "
            "JOIN actors i ON i.actor_id = uf.actor_id "
            "WHERE uf.user_id = ? "
            "ORDER BY i.actor_name",
            (self.user_id,)
        )

        favs = self.cur.fetchall()

        for idx, combo in enumerate(self.actor_combos):
            combo.clear()

            if idx < len(favs):
                combo.addItem(favs[idx][1], favs[idx][0])
                combo.setCurrentIndex(0)
                combo.setEditable(False)

            else:
                self._fill_available(
                    combo,
                    'userfavoriteactors',
                    'actor_id',
                    'actors',
                    'actor_name'
                )

    def load_directors(self):
        self.cur.execute(
            "SELECT i.director_id, i.director_name "
            "FROM userfavoritedirectors uf "
            "JOIN directors i ON i.director_id = uf.director_id "
            "WHERE uf.user_id = ? "
            "ORDER BY i.director_name",
            (self.user_id,)
        )

        favs = self.cur.fetchall()

        for idx, combo in enumerate(self.dir_combos):
            combo.clear()

            if idx < len(favs):
                combo.addItem(favs[idx][1], favs[idx][0])
                combo.setCurrentIndex(0)
                combo.setEditable(False)

            else:
                self._fill_available(
                    combo,
                    'userfavoritedirectors',
                    'director_id',
                    'directors',
                    'director_name'
                )

    def load_screenwriters(self):
        self.cur.execute(
            "SELECT i.screenwriter_id, i.screenwriter_name "
            "FROM userfavoritescreenwriters uf "
            "JOIN screenwriters i ON i.screenwriter_id = uf.screenwriter_id "
            "WHERE uf.user_id = ? "
            "ORDER BY i.screenwriter_name",
            (self.user_id,)
        )

        favs = self.cur.fetchall()

        for idx, combo in enumerate(self.scen_combos):
            combo.clear()

            if idx < len(favs):
                combo.addItem(favs[idx][1], favs[idx][0])
                combo.setCurrentIndex(0)
                combo.setEditable(False)

            else:
                self._fill_available(
                    combo,
                    'userfavoritescreenwriters',
                    'screenwriter_id',
                    'screenwriters',
                    'screenwriter_name'
                )

    def load_otherpeople(self):
        self.cur.execute(
            "SELECT i.person_id, i.person_name "
            "FROM userfavoriteotherpeople uf "
            "JOIN otherfilmpeople i ON i.person_id = uf.person_id "
            "WHERE uf.user_id = ? "
            "ORDER BY i.person_name",
            (self.user_id,)
        )

        favs = self.cur.fetchall()

        for idx, combo in enumerate(self.other_combos):
            combo.clear()

            if idx < len(favs):
                combo.addItem(favs[idx][1], favs[idx][0])
                combo.setCurrentIndex(0)
                combo.setEditable(False)

            else:
                self._fill_available(
                    combo,
                    'userfavoriteotherpeople',
                    'person_id',
                    'otherfilmpeople',
                    'person_name'
                )
