import sys
import os
import sqlite3
from PyQt6.QtCore import Qt
import bcrypt
from src.fill_db import init_database
import phonenumbers
from pathlib import Path
from src.ui_forms.registration_window import Ui_Form
from src.code.main_kod import MainWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox, QCompleter, QFileDialog
from src.code.database import init_database, add


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
        for combo in self.findChildren(QComboBox):
            placeholder = combo.currentText()
            combo.setPlaceholderText(placeholder)
            combo.setCurrentIndex(-1)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.avatar_path = os.path.join(base_dir, 'src', 'images', 'photo_profile.jpg')

        self.btn_upload_photo.clicked.connect(self.choose_file)
        self.pushButton_entrance.clicked.connect(self.entrance)
        self.pushButton_zaregestrirovat.clicked.connect(self.regist)
        self.load_data_to_combobox()

        self.load_names_to_combobox(
            self.comboBox_regisers,
            'Directors',
            'director_name'
        )

        self.load_names_to_combobox(
            self.comboBox_acters,
            'Actors',
            'actor_name'
        )

        self.load_names_to_combobox(
            self.comboBox_scenario,
            'screenwriters',
            'screenwriter_name'
        )

        self.load_names_to_combobox(
            self.comboBox_uchastnik,
            'otherfilmpeople',
            'person_name'
        )

        self.setup_combo_search(self.comboBox_kino)
        self.setup_combo_search(self.comboBox_regisers)
        self.setup_combo_search(self.comboBox_acters)
        self.setup_combo_search(self.comboBox_scenario)
        self.setup_combo_search(self.comboBox_uchastnik)

    def entrance(self):
        from src.code.entrance import Entrance
        self.next_window = Entrance(self.con, self.cur)
        self.next_window.show()
        self.close()

        for combobox in self.findChildren(QComboBox):
            self.setup_combo_search(combobox)

    def load_directors_to_combobox(self):
        connection = sqlite3.connect('film_break.db')
        cursor = connection.cursor()

        cursor.execute('SELECT director_name FROM Directors')
        rows = cursor.fetchall()

        self.comboBox_regisers.clear()

        for row in rows:
            self.comboBox_regisers.addItem(row[0])

        connection.close()
    
    def load_actors_to_combobox(self):
        connection = sqlite3.connect('film_break.db')
        cursor = connection.cursor()

        cursor.execute('SELECT actor_name FROM Actors')
        rows = cursor.fetchall()

        self.comboBox_acters.clear()

        for row in rows:
            self.comboBox_acters.addItem(row[0])

        connection.close()

    
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

    def check_text():
        text = combo.currentText().strip()
        index = combo.findText(
            text,
            Qt.MatchFlag.MatchFixedString
        )

        if index != -1:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(-1)
            combo.lineEdit().clear()

        combo.lineEdit().editingFinished.connect(check_text)
        
    def load_data_to_combobox(self):

        project_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_dir, 'film_break.db')

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute('SELECT title, release_year FROM films')
        rows = cursor.fetchall()

        items_list = []
        for row in rows:
            title = row[0]
            year = row[1]
            if title:
                display_text = f'{title} {year}'
                items_list.append(display_text)

        connection.close()

        self.comboBox_kino.clear()
        self.comboBox_kino.addItems(items_list)

        self.comboBox_kino.setEditable(True)
        self.comboBox_kino.setCurrentIndex(-1)

        self.comboBox_kino.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )

        completer = QCompleter(self.comboBox_kino.model(), self.comboBox_kino)

        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)

        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        self.comboBox_kino.setCompleter(completer)

        self.comboBox_kino.activated.connect(
            self.select_movie_text
        )

        self.comboBox_kino.activated.connect(
            lambda: self.comboBox_kino.setEditable(False)
        )

        self.comboBox_kino.lineEdit().textEdited.connect(
        self.reset_movie_selection
        )

    def load_names_to_combobox(self, combobox, table, column):

        project_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_dir, 'film_break.db')

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute(f'SELECT {column} FROM {table}')
        rows = cursor.fetchall()

        connection.close()

        combobox.clear()

        for row in rows:
            if row[0]:
                combobox.addItem(row[0])

        combobox.setCurrentIndex(-1)

        self.setup_combo_search(combobox)

    def reset_movie_selection(self, text):
        if self.comboBox_kino.currentIndex() != -1:
            self.comboBox_kino.setCurrentIndex(-1)
            self.comboBox_kino.setEditText(text)
    
    def select_movie_text(self):
        line_edit = self.comboBox_kino.lineEdit()

        if line_edit is not None:
            line_edit.selectAll()

    from PyQt6.QtWidgets import QFileDialog

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Изображения (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.avatar_path = file_path

    def regist(self):
        if len(self.lineEdit_name.text()) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина имени не должна превышать 20 символов')
            return
        if self.lineEdit_name.text().strip() == '':
            QMessageBox.warning(self, 'Ошибка', 'Имя должно содержать какие-либо символы помимо пробелов')
            return
        if self.lineEdit_nickname.text().strip() == '':
            QMessageBox.warning(self, 'Ошибка', 'Никнейм должно содержать какие-либо символы помимо пробелов')
            return
        name = self.lineEdit_name.text().strip()

        nickname = self.lineEdit_nickname.text()

        if len(self.lineEdit_nickname.text()) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина никнейма не должна превышать 20 символов')
            return
        birth_date = self.dateEdit_dr.date().toString('yyyy-MM-dd')
        phone = self.lineEdit_number.text().strip()
        try:
            number = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(number):
                QMessageBox.warning(self, "Ошибка", "Введите корректный номер телефона!")
                return
            phone = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            QMessageBox.warning(self, "Ошибка", "Введите номер с кодом страны, например +37120123456")
            return

        password = self.lineEdit_password.text().strip()
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

        self.cur.execute("INSERT INTO users(name, nickname, phone, birth_date, password_hash, avatar_path) VALUES(?, ?, ?, ?, ?, ?)", (nickname, name, phone, birth_date, password_hash, self.avatar_path, ))
        self.con.commit()
        self.con.close()

        self.name = name
        self.nickname = nickname


        self.next_window = MainWindow()
        self.next_window.show()
        self.close()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
