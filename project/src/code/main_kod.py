from ..ui_forms.main_okno import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QWidget
from ..ui_forms.profile_window import Ui_Form_profile


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.home_page = self.centralWidget()

        self.profile_page = QWidget()
        self.profile_ui = Ui_Form_profile()
        self.profile_ui.setupUi(self.profile_page)

        self.btn_profile.triggered.connect(self.open_profile)

    def open_profile(self):
        self.setCentralWidget(self.profile_page)