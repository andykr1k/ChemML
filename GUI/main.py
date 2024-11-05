import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QStackedWidget, QMessageBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from utils import createCombinations, createPOSCARs, generateCIFs, read_file
import os


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
        self.titleLabel.setStyleSheet("color: #254E70;")
        layout.addWidget(self.titleLabel)

        self.continueButton = QPushButton("Continue")
        self.continueButton.setFont(QFont("Arial", 14))
        self.continueButton.setStyleSheet(
            """
            QPushButton {
                background-color: #254E70;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #37718E;
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
        self.titleLabel.setStyleSheet("color: #254E70;")
        layout.addWidget(self.titleLabel)

        self.baseInput = QLineEdit()
        self.baseInput.setPlaceholderText(
            "Enter base structure formula here...")
        self.baseInput.setFont(QFont("Arial", 12))
        self.baseInput.setStyleSheet(
            """
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #254E70;
                padding: 8px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #3E8E41;
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

        # Loading label for upload status
        self.uploadStatusLabel = QLabel("")
        self.uploadStatusLabel.setFont(QFont("Arial", 10))
        self.uploadStatusLabel.setStyleSheet("color: #37718E;")
        layout.addWidget(self.uploadStatusLabel)

        # Other processing buttons with loading labels
        self.createCombButton = QPushButton("Create Combinations")
        self.createCombButton.setEnabled(False)
        self.createCombButton.setFont(QFont("Arial", 12))
        self.createCombButton.setStyleSheet(self.buttonStyle())
        self.createCombButton.clicked.connect(lambda: self.handleAction(0))
        layout.addWidget(self.createCombButton)

        self.createCombStatus = QLabel("")  # Loading label
        layout.addWidget(self.createCombStatus)

        self.createPoscarsButton = QPushButton("Create POSCARs")
        self.createPoscarsButton.setEnabled(False)
        self.createPoscarsButton.setFont(QFont("Arial", 12))
        self.createPoscarsButton.setStyleSheet(self.buttonStyle())
        self.createPoscarsButton.clicked.connect(lambda: self.handleAction(1))
        layout.addWidget(self.createPoscarsButton)

        self.createPoscarsStatus = QLabel("")  # Loading label
        layout.addWidget(self.createPoscarsStatus)

        self.generateCifsButton = QPushButton("Generate CIFs")
        self.generateCifsButton.setEnabled(False)
        self.generateCifsButton.setFont(QFont("Arial", 12))
        self.generateCifsButton.setStyleSheet(self.buttonStyle())
        self.generateCifsButton.clicked.connect(lambda: self.handleAction(2))
        layout.addWidget(self.generateCifsButton)

        self.generateCifsStatus = QLabel("")  # Loading label
        layout.addWidget(self.generateCifsStatus)

        self.featurizeButton = QPushButton("Featurize")
        self.featurizeButton.setEnabled(False)
        self.featurizeButton.setFont(QFont("Arial", 12))
        self.featurizeButton.setStyleSheet(self.buttonStyle())
        self.featurizeButton.clicked.connect(lambda: self.handleAction(3))
        layout.addWidget(self.featurizeButton)

        self.featurizeStatus = QLabel("")  # Loading label
        layout.addWidget(self.featurizeStatus)

        main_layout.addLayout(layout)

        activity_log_layout = QVBoxLayout()

        self.activityLogLabel = QLabel(
            "Activity Log")  # Renamed to avoid conflict
        self.activityLogLabel.setFont(QFont("Arial", 16, QFont.Bold))
        self.activityLogLabel.setAlignment(Qt.AlignCenter)
        self.activityLogLabel.setStyleSheet("color: #254E70;")
        activity_log_layout.addWidget(self.activityLogLabel)

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
                background-color: #254E70;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:disabled {
                background-color: #254E70;
                color: #E0E0E0;
            }
            QPushButton:hover:!disabled {
                background-color: #37718E;
            }
        """

    def enableUploadButton(self):
        self.uploadButton.setEnabled(bool(self.baseInput.text().strip()))

    def openFileDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Choose POSCAR File", "", "POSCAR Files (*)", options=options)
        if filePath:
            self.uploadButton.setText("Completed")
            self.uploadStatusLabel.setText(
                "POSCAR file uploaded successfully.")
            self.logActivity(
                f"POSCAR File Uploaded: {filePath.split('/')[-1]}")
            self.poscar_file_path = filePath
            self.createCombButton.setEnabled(True)

    def handleAction(self, index):
        buttons = [self.createCombButton, self.createPoscarsButton,
                   self.generateCifsButton, self.featurizeButton]
        labels = [self.createCombStatus, self.createPoscarsStatus,
                  self.generateCifsStatus, self.featurizeStatus]

        buttons[index].setText("Loading...")
        labels[index].setText("Processing...")
        buttons[index].setEnabled(False)

        if index == 0:
            self.createCombinations()
        elif index == 1:
            self.createPOSCARs()
        elif index == 2:
            self.generateCIFs()
        elif index == 3:
            self.featurize()

        # Increased duration
        QTimer.singleShot(3000, lambda: self.completeAction(index))

    def completeAction(self, index):
        buttons = [self.createCombButton, self.createPoscarsButton,
                   self.generateCifsButton, self.featurizeButton]
        labels = [self.createCombStatus, self.createPoscarsStatus,
                  self.generateCifsStatus, self.featurizeStatus]

        buttons[index].setText("Completed")
        labels[index].setText("")
        if index + 1 < len(buttons):
            buttons[index + 1].setEnabled(True)

    def createCombinations(self):
        formula = self.baseInput.text().strip()
        result, self.combinations_file = createCombinations(formula)
        self.logActivity(f"Combinations created for formula: {formula}")
        QMessageBox.information(self, "Combinations Created", f"{result}")

    def createPOSCARs(self):
        if hasattr(self, 'poscar_file_path'):
            result = createPOSCARs(self.poscar_file_path,
                                   self.combinations_file)
            self.logActivity("POSCARs created from uploaded file.")
            QMessageBox.information(self, "POSCARs Created", f"{result}")
        else:
            self.logActivity("Failed to create POSCARs: No file selected.")
            QMessageBox.warning(self, "Error", "Upload a POSCAR file first.")

    def generateCIFs(self):
        result = generateCIFs(self.combinations_file)
        self.logActivity("CIFs generated from combinations.")
        QMessageBox.information(self, "CIFs Generated", f"{result}")

    def featurize(self):
        result = "Featurization started. Check the activity log for updates."
        self.logActivity(result)

    def logActivity(self, message):
        self.activityLog.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    homePage = HomePage(stacked_widget)
    chemmlPage = ChemMLPage()
    stacked_widget.addWidget(homePage)
    stacked_widget.addWidget(chemmlPage)
    stacked_widget.setFixedWidth(800)
    stacked_widget.setFixedHeight(600)
    stacked_widget.show()
    sys.exit(app.exec_())
