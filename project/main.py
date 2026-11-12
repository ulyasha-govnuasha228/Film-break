import sys
import os
import shutil
import uuid
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import bcrypt
from src.fill_db import init_database
import phonenumbers
from src.ui_forms.registration_window import Ui_Form
from src.code.main_kod import MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox, QCompleter, QFileDialog
from src.fill_db import init_database, add


class RegistrationWindow(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()

        init_database()
        add()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'film_break.db')

        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

        self.setupUi(self)
        self.setMinimumSize(800, 600)
        for combo in self.findChildren(QComboBox):
            placeholder = combo.currentText()
            combo.setPlaceholderText(placeholder)
            combo.setCurrentIndex(-1)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.avatar_path = os.path.join(base_dir, 'src', 'images', 'photo_profile.jpg')

        self.btn_upload_photo.clicked.connect(self.choose_file)
        self.pushbutton_entrance.clicked.connect(self.entrance)
        self.pushbutton_zaregestrirovat.clicked.connect(self.regist)
        self.pushbutton.clicked.connect(self.open_add_dialog)
        self.load_data_to_combobox()

        self.load_names_to_combobox(
            self.combobox_regisers,
            'Directors',
            'director_name',
            'director_id'
        )

        self.load_names_to_combobox(
            self.combobox_acters,
            'Actors',
            'actor_name',
            'actor_id'
        )

        self.load_names_to_combobox(
            self.combobox_scenario,
            'screenwriters',
            'screenwriter_name',
            'screenwriter_id'
        )

        self.load_names_to_combobox(
            self.combobox_uchastnik,
            'otherfilmpeople',
            'person_name',
            'person_id'
        )

        self.setup_combo_search(self.combobox_kino)
        self.setup_combo_search(self.combobox_regisers)
        self.setup_combo_search(self.combobox_acters)
        self.setup_combo_search(self.combobox_scenario)
        self.setup_combo_search(self.combobox_uchastnik)

    def open_add_dialog(self):
        from src.code.add_films import AddDialog
        dialog = AddDialog(self.con, self.cur)
        if dialog.exec():
            self.load_data_to_combobox()
            self.load_names_to_combobox(self.combobox_acters, 'Actors', 'actor_name', 'actor_id')
            self.load_names_to_combobox(self.combobox_regisers, 'Directors', 'director_name', 'director_id')

    def entrance(self):
        from src.code.entrance import Entrance
        self.next_window = Entrance(self.con, self.cur)
        self.next_window.show()
        self.close()

        for combobox in self.findChildren(QComboBox):
            self.setup_combo_search(combobox)

    def setup_combo_search(self, combo):
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        completer = QCompleter(combo.model(), combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        combo.setCompleter(completer)
        combo.setCurrentIndex(-1)
        combo.lineEdit().clear()
        combo.activated.connect(
            lambda: combo.setEditable(False)
        )

    def load_data_to_combobox(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_dir, 'film_break.db')

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute('SELECT film_id, title, release_year FROM films')
        rows = cursor.fetchall()

        connection.close()

        self.combobox_kino.clear()
        for row in rows:
            film_id = row[0]
            title = row[1]
            year = row[2]
            if title:
                display_text = f'{title} {year}'
                self.combobox_kino.addItem(display_text, film_id)

        self.combobox_kino.setEditable(True)
        self.combobox_kino.setCurrentIndex(-1)

        self.combobox_kino.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )

        completer = QCompleter(self.combobox_kino.model(), self.combobox_kino)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        self.combobox_kino.setCompleter(completer)
        self.combobox_kino.activated.connect(self.select_movie_text)
        self.combobox_kino.activated.connect(
            lambda: self.combobox_kino.setEditable(False)
        )
        self.combobox_kino.lineEdit().textEdited.connect(
            self.reset_movie_selection
        )

    def load_names_to_combobox(self, combobox, table, column, id_column):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_dir, 'film_break.db')

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute(f'SELECT {id_column}, {column} FROM {table}')
        rows = cursor.fetchall()

        connection.close()

        combobox.clear()

        for row in rows:
            item_id = row[0]
            name = row[1]
            if name:
                combobox.addItem(name, item_id)

        combobox.setCurrentIndex(-1)

        self.setup_combo_search(combobox)

    def reset_movie_selection(self, text):
        if self.combobox_kino.currentIndex() != -1:
            self.combobox_kino.setCurrentIndex(-1)
            self.combobox_kino.setEditText(text)
    
    def select_movie_text(self):
        line_edit = self.combobox_kino.lineEdit()
        if line_edit is not None:
            line_edit.selectAll()

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Изображения (*.png *.jpg *.jpeg)"
        )

        if file_path:
            ext = os.path.splitext(file_path)[1]
            new_filename = f"avatar_{uuid.uuid4().hex}{ext}"
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dest_path = os.path.join(base_dir, 'src', 'images', new_filename)
            
            shutil.copy(file_path, dest_path)
            self.avatar_path = dest_path

            pixmap = QPixmap(self.avatar_path)
            if not pixmap.isNull():
                self.labe_foto.setPixmap(pixmap)
                self.labe_foto.setScaledContents(True)

    def regist(self):
        if len(self.lineedit_name.text()) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина имени не должна превышать 20 символов')
            return
        if self.lineedit_name.text().strip() == '':
            QMessageBox.warning(self, 'Ошибка', 'Имя должно содержать какие-либо символы помимо пробелов')
            return
        if self.lineedit_nickname.text().strip() == '':
            QMessageBox.warning(self, 'Ошибка', 'Никнейм должно содержать какие-либо символы помимо пробелов')
            return
            
        name = self.lineedit_name.text().strip()
        nickname = self.lineedit_nickname.text().strip()

        if len(self.lineedit_nickname.text()) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина никнейма не должна превышать 20 символов')
            return
            
        birth_date = self.dateedit_dr.date().toString('yyyy-MM-dd')
        phone = self.lineedit_number.text().strip()
        
        try:
            number = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(number):
                QMessageBox.warning(self, "Ошибка", "Введите корректный номер телефона!")
                return
            phone = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            QMessageBox.warning(self, "Ошибка", "Введите номер с кодом страны, например +37120123456")
            return

        password = self.lineedit_password.text().strip()
        if password == '':
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен содержать какие-либо символы помимо пробелов')
            return
        
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        self.cur.execute(
            "SELECT 1 FROM users WHERE nickname = ? LIMIT 1",
            (nickname,)
        )
        if self.cur.fetchone():
            QMessageBox.warning(self, 'Ошибка', 'Такой никнейм уже существует')
            return

        self.cur.execute(
            "SELECT phone FROM users WHERE phone = ?",
            (phone,)
        )

        existing_phone = self.cur.fetchone()

        if existing_phone:
            QMessageBox.warning(
                self,
                "Ошибка регистрации",
                "Пользователь с таким номером телефона уже зарегистрирован!"
            )
            return

        self.cur.execute("INSERT INTO users(name, nickname, phone, birth_date, password_hash, avatar_path) VALUES(?, ?, ?, ?, ?, ?)", (name, nickname, phone, birth_date, password_hash, self.avatar_path, ))
        self.con.commit()

        user_id = self.cur.lastrowid
        
        try:
            kino = self.combobox_kino.currentData()
            if kino:
                self.cur.execute("INSERT INTO userfavoritefilms(user_id, film_id) VALUES(?, ?)", (user_id, kino))
                
            actor = self.combobox_acters.currentData()
            if actor:
                self.cur.execute("INSERT INTO userfavoriteactors(user_id, actor_id) VALUES(?, ?)", (user_id, actor))
                
            director = self.combobox_regisers.currentData()
            if director:
                self.cur.execute("INSERT INTO userfavoritedirectors(user_id, director_id) VALUES(?, ?)", (user_id, director))
                
            scenario = self.combobox_scenario.currentData()
            if scenario:
                self.cur.execute("INSERT INTO userfavoritescreenwriters(user_id, screenwriter_id) VALUES(?, ?)", (user_id, scenario))
                
            uchastnik = self.combobox_uchastnik.currentData()
            if uchastnik:
                self.cur.execute("INSERT INTO userfavoriteotherpeople(user_id, person_id) VALUES(?, ?)", (user_id, uchastnik))
                
            self.con.commit()
        except sqlite3.IntegrityError:
            pass

        self.next_window = MainWindow(user_id, self.con, self.cur)
        self.next_window.resize(1200, 750)
        self.next_window.show()
        self.close()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
    