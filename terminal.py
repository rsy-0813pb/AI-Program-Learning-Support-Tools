from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QProcess

class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)

        self.setWindowTitle('Terminal')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { background-color: #282C34; color: #ABB2BF; }")
        layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.setStyleSheet("QLineEdit { background-color: #282C34; color: #ABB2BF; }")
        layout.addWidget(self.input)

        self.input.returnPressed.connect(self.write_input)

    def execute_command(self, command):
        self.process.start(command)

    def handle_output(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf8', errors='replace')
        self.output.append(text)

    def write_input(self):
        input_text = self.input.text()
        self.process.write(f'{input_text}\n'.encode())
        self.output.append(f'> {input_text}')
        self.input.clear()

    def clear_output(self):
        self.output.clear()

    def get_output(self):
        return self.output.toPlainText()