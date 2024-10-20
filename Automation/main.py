# Inputs:
### Base Structure Formula
### Base Structure Poscar

# Process:
### Step 1: Create all formulas
### Step 2: Create all poscars
### Step 3: Generate CIFs files from poscars
### Step 4: Featurize with jarvis using cif files

# Outputs:
### CSV File with all correct records from ICSD, CIFs and Jarvis Features

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()
