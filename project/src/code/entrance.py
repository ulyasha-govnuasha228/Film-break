from ..ui_forms.entrance_window import Ui_Form
from PyQt6.QtWidgets import QWidget, QMessageBox
import bcrypt


class Entrance(QWidget, Ui_Form):
    def __init__(self, con, cur):
        super().__init__()
        self.setupUi(self)
        self.con = con
        self.cur = cur
        self.pushButton_zaregestrirovat.clicked.connect(self.entrancing)
    
    def entrancing(self):
        nickname = self.lineEdit_nickname.text().strip()
        password = self.lineEdit_password.text().strip()

        if nickname == '':
            QMessageBox.warning(self, 'Ошибка', 'Никнейм должен содержать какие-либо символы помимо пробелов')
            return
        if password == '':
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен содержать какие-либо символы помимо пробелов')
            return
        if len(nickname) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина никнейма не должна превышать 20 символов')
            return
        if len(password) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Длина пароля не должна превышать 20 символов')
            return
        self.cur.execute(
            "SELECT * FROM Users WHERE nickname = ?",
            (nickname,)
        )
        user = self.cur.fetchone()
        if user is None:
            QMessageBox.warning(self, 'Ошибка', 'Такого никнейма не существует')
            return
        self.cur.execute(
            "SELECT password_hash FROM users WHERE nickname = ?",
            (nickname,)
        )

        password_hash = self.cur.fetchone()[0]
        password_hash_vv = bcrypt.checkpw(password.encode(), password_hash.encode())
        if not password_hash_vv:
            QMessageBox.warning(self, 'Ошибка', 'Неверный пароль')
            return
        from Main_Window.main_kod import MainWindow
        self.next_window = MainWindow()
        self.next_window.show()
        self.close()
