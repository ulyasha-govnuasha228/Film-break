from ..ui_forms.entrance_window import Ui_Form
from PyQt6.QtWidgets import QWidget, QMessageBox
import bcrypt


class Entrance(QWidget, Ui_Form):
    def __init__(self, con, cur):
        super().__init__()
        self.setupUi(self)
        self.con = con
        self.cur = cur
        self.pushbutton_zaregestrirovat.clicked.connect(self.entrancing)
    
    def entrancing(self):
        nickname = self.lineedit_nickname.text().strip()
        password = self.lineedit_password.text().strip()

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
            "SELECT id, password_hash FROM users WHERE nickname = ?",
            (nickname,)
        )
        user = self.cur.fetchone()
        
        if user is None:
            QMessageBox.warning(self, 'Ошибка', 'Такого никнейма не существует')
            return
            
        user_id = user[0]
        password_hash = user[1]

        password_hash_vv = bcrypt.checkpw(password.encode(), password_hash.encode())
        if not password_hash_vv:
            QMessageBox.warning(self, 'Ошибка', 'Неверный пароль')
            return
            
        from src.code.main_kod import MainWindow 
        
        self.next_window = MainWindow(user_id, self.con, self.cur)
        self.next_window.show()
        self.close()