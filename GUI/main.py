import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QStackedWidget, QMessageBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from utils import createCombinations, createPOSCARs, generateCIFs, read_file


class HomePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.titleLabel = QLabel("ChemML")
        self.titleLabel.setFont(QFont("Arial", 28, QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.titleLabel)

        self.continueButton = QPushButton("Continue")
        self.continueButton.setFont(QFont("Arial", 14))
        self.continueButton.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        self.continueButton.clicked.connect(self.goToNextPage)
        layout.addWidget(self.continueButton, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def goToNextPage(self):
        self.stacked_widget.setCurrentIndex(1)


class ChemMLPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        self.titleLabel = QLabel("ChemML")
        self.titleLabel.setFont(QFont("Arial", 28, QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.titleLabel)

        self.baseInput = QLineEdit()
        self.baseInput.setPlaceholderText("Enter base structure formula here...")
        self.baseInput.setFont(QFont("Arial", 12))
        self.baseInput.setStyleSheet(
            """
            QLineEdit {
                background-color: white;        /* Light background color */
                color: black;                   /* Black text color */
                border: 1px solid #4CAF50;     /* Border color */
                padding: 8px;                  /* Padding around the text */
                border-radius: 5px;            /* Rounded corners */
            }
            QLineEdit:focus {
                border: 1px solid #3E8E41;     /* Darker border on focus */
            }
            """
        )
        layout.addWidget(self.baseInput)
        self.baseInput.textChanged.connect(self.enableUploadButton)

        # File upload button
        self.uploadButton = QPushButton("Upload Base Structure (POSCAR)")
        self.uploadButton.setEnabled(False)
        self.uploadButton.setFont(QFont("Arial", 12))
        self.uploadButton.setStyleSheet(self.buttonStyle())
        self.uploadButton.clicked.connect(self.openFileDialog)
        layout.addWidget(self.uploadButton)

        self.createCombButton = QPushButton("Create Combinations")
        self.createCombButton.setEnabled(False)
        self.createCombButton.setFont(QFont("Arial", 12))
        self.createCombButton.setStyleSheet(self.buttonStyle())
        self.createCombButton.clicked.connect(lambda: self.handleAction(0))
        layout.addWidget(self.createCombButton)

        self.createPoscarsButton = QPushButton("Create POSCARs")
        self.createPoscarsButton.setEnabled(False)
        self.createPoscarsButton.setFont(QFont("Arial", 12))
        self.createPoscarsButton.setStyleSheet(self.buttonStyle())
        self.createPoscarsButton.clicked.connect(lambda: self.handleAction(1))
        layout.addWidget(self.createPoscarsButton)

        self.generateCifsButton = QPushButton("Generate CIFs")
        self.generateCifsButton.setEnabled(False)
        self.generateCifsButton.setFont(QFont("Arial", 12))
        self.generateCifsButton.setStyleSheet(self.buttonStyle())
        self.generateCifsButton.clicked.connect(lambda: self.handleAction(2))
        layout.addWidget(self.generateCifsButton)

        self.featurizeButton = QPushButton("Featurize")
        self.featurizeButton.setEnabled(False)
        self.featurizeButton.setFont(QFont("Arial", 12))
        self.featurizeButton.setStyleSheet(self.buttonStyle())
        self.featurizeButton.clicked.connect(lambda: self.handleAction(3))
        layout.addWidget(self.featurizeButton)

        main_layout.addLayout(layout)

        activity_log_layout = QVBoxLayout()

        self.titleLabel = QLabel("Activity Log")
        self.titleLabel.setFont(QFont("Arial", 16, QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("color: #4CAF50;")
        activity_log_layout.addWidget(self.titleLabel)

        self.activityLog = QTextEdit()
        self.activityLog.setReadOnly(True)
        self.activityLog.setFont(QFont("Arial", 10))
        self.activityLog.setStyleSheet(
            "background-color: lightgrey; color: black; padding: 10px;"
        )
        activity_log_layout.addWidget(self.activityLog)

        main_layout.addLayout(activity_log_layout)

        self.setLayout(main_layout)

    def buttonStyle(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #E0E0E0;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
        """

    def enableUploadButton(self):
        self.uploadButton.setEnabled(bool(self.baseInput.text().strip()))

    def openFileDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Choose POSCAR File", "", "POSCAR Files (*)", options=options)
        if filePath:
            QMessageBox.information(
                self, "File Selected", f"POSCAR File Uploaded: {filePath.split('/')[-1]}")
            self.logActivity(
                f"POSCAR File Uploaded: {filePath.split('/')[-1]}")
            self.poscar_file_path = filePath
            self.createCombButton.setEnabled(True)

    def handleAction(self, index):
        buttons = [self.createCombButton, self.createPoscarsButton,
                   self.generateCifsButton, self.featurizeButton]

        buttons[index].setText("Loading...")
        buttons[index].setEnabled(False)

        if index == 0:
            self.createCombinations()
        elif index == 1:
            self.createPOSCARs()
        elif index == 2:
            self.generateCIFs()
        elif index == 3:
            self.featurize()

        QTimer.singleShot(2000, lambda: self.completeAction(index))

    def completeAction(self, index):
        buttons = [self.createCombButton, self.createPoscarsButton,
                   self.generateCifsButton, self.featurizeButton]

        buttons[index].setText(
            buttons[index].text().replace("Loading...", "Completed"))
        if index + 1 < len(buttons):
            buttons[index + 1].setEnabled(True)

    def createCombinations(self):
        formula = self.baseInput.text().strip()
        result = createCombinations(formula)
        self.logActivity(f"Combinations created for formula: {formula}")
        QMessageBox.information(self, "Combinations Created", f"{result}")

    def createPOSCARs(self):
        if hasattr(self, 'poscar_file_path'):
            content = read_file(self.poscar_file_path)
            result = createPOSCARs(content)
            self.logActivity("POSCARs created from uploaded file.")
            QMessageBox.information(
                self, "POSCARs Created", f"{result}")
        else:
            self.logActivity("Failed to create POSCARs: No file selected.")
            QMessageBox.warning(self, "No File Selected",
                                "Please upload a POSCAR file first.")

    def generateCIFs(self):
        if hasattr(self, 'poscar_file_path'):
            content = read_file(self.poscar_file_path)
            result = generateCIFs(content)
            self.logActivity("CIFs generated from POSCAR content.")
            QMessageBox.information(self, "CIFs Generated", f"{result}")
        else:
            self.logActivity("Failed to generate CIFs: No file selected.")
            QMessageBox.warning(self, "No File Selected",
                                "Please upload a POSCAR file first.")

    def featurize(self):
        self.logActivity("Featurization started.")
        QMessageBox.information(
            self, "Featurize", "Featurization is not yet implemented.")

    def logActivity(self, message):
        self.activityLog.append(message)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemML")
        self.setGeometry(100, 100, 600, 350)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#F0F0F0"))
        self.setPalette(palette)

        self.stacked_widget = QStackedWidget(self)
        self.home_page = HomePage(self.stacked_widget)
        self.chemml_page = ChemMLPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.chemml_page)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
