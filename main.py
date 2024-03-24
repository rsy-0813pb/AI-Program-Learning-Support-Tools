import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QLineEdit, QSplitter, QScrollArea, QMessageBox
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt
from code_editor import CodeEditor
from terminal import Terminal
from google_gemini import check_solution, set_api_key

CONFIG_FILE = 'config.json'

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple IDE')
        layout = QVBoxLayout()
        self.setLayout(layout)

        main_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(main_splitter)

        top_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(top_splitter)

        self.editor = CodeEditor()
        self.editor.setFont(QFont('Consolas', 12))
        top_splitter.addWidget(self.editor)

        right_splitter = QSplitter(Qt.Vertical)
        top_splitter.addWidget(right_splitter)

        api_key_layout = QHBoxLayout()
        api_key_widget = QWidget()
        api_key_widget.setLayout(api_key_layout)
        right_splitter.addWidget(api_key_widget)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Google Gemini API Keyを入力してください...")
        api_key_layout.addWidget(self.api_key_input)

        update_api_key_button = QPushButton('APIキーの更新')
        update_api_key_button.clicked.connect(self.update_api_key)
        update_api_key_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        api_key_layout.addWidget(update_api_key_button)

        self.question_text = QTextEdit()
        self.question_text.setPlaceholderText("ここに問題文を書く...")
        right_splitter.addWidget(self.question_text)

        bottom_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(bottom_splitter)

        self.terminal = Terminal()
        bottom_splitter.addWidget(self.terminal)

        right_bottom_widget = QWidget()
        right_bottom_layout = QVBoxLayout()
        right_bottom_widget.setLayout(right_bottom_layout)
        bottom_splitter.addWidget(right_bottom_widget)

        self.result_label = ScrollLabel()
        right_bottom_layout.addWidget(self.result_label)

        button_layout = QHBoxLayout()
        right_bottom_layout.addLayout(button_layout)

        run_button = QPushButton('Run')
        run_button.clicked.connect(self.run_code)
        run_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        button_layout.addWidget(run_button)

        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.terminal.clear_output)
        clear_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        button_layout.addWidget(clear_button)

        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_file)
        self.open_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        button_layout.addWidget(self.open_button)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        button_layout.addWidget(self.save_button)

        check_button = QPushButton('Check')
        check_button.clicked.connect(self.check_solution)
        check_button.setStyleSheet("QPushButton { background-color: #3E4451; color: #ABB2BF; }")
        right_bottom_layout.addWidget(check_button)

        self.load_config()
        self.set_dark_titlebar()
        self.update_save_button_state()

    def run_code(self):
        code = self.editor.toPlainText()
        with open('temp.py', 'w', encoding='utf-8') as f:
            f.write(code)
        self.terminal.execute_command('python temp.py')

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.load_content(content)
                    self.current_file = file_name
                    self.update_save_button_state()
            except UnicodeDecodeError:
                QMessageBox.warning(self, "エンコーディングエラー", "ファイルのエンコーディングがUTF-8ではありません。\nファイルを UTF-8 で保存し直してください。")

    def save_file(self):
        if hasattr(self, 'current_file'):
            file_name = self.current_file
            self.save_file_as(file_name)
        else:
            self.save_file_as()

    def save_file_as(self, file_name=None):
        if not file_name:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)", options=options)

        if file_name:
            content = self.get_content()
            gemini_answer = self.result_label.label.text()

            file_name = file_name.replace(' ok.py', '.py').replace(' retry.py', '.py')

            if "正解です!" in gemini_answer:
                file_name = file_name.replace('.py', ' ok.py')
            elif "間違っています。" in gemini_answer:
                file_name = file_name.replace('.py', ' retry.py')

            if hasattr(self, 'current_file') and self.current_file != file_name:
                os.remove(self.current_file)

            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)

            self.current_file = file_name
            self.update_save_button_state()

    def check_solution(self):
        api_key = self.api_key_input.text()
        set_api_key(api_key)
        problem_statement = self.question_text.toPlainText()
        code = self.editor.toPlainText()
        output = self.terminal.get_output()
        result = check_solution(problem_statement, code, output)
        result = result.replace('<error>間違っています。</error>', '').replace('error', '')
        self.result_label.setText(result)

    def update_api_key(self):
        api_key = self.api_key_input.text()
        self.save_config(api_key)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key', '')
                self.api_key_input.setText(api_key)

    def save_config(self, api_key):
        config = {'api_key': api_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def get_content(self):
        problem_statement = self.question_text.toPlainText()
        code = self.editor.toPlainText()
        output = self.terminal.get_output()
        gemini_answer = self.result_label.label.text()

        content = f'"""\nProblem Statement:\n{problem_statement}\n\nCode:\n{code}\n\nTerminal Output:\n{output}\n\nGemini Answer:\n{gemini_answer}\n"""\n\n{code}'
        return content

    def load_content(self, content):
        parts = content.split('"""')
        if len(parts) > 1:
            meta_content = parts[1].strip()
            code_content = parts[2].strip()

            problem_statement = self.extract_part(meta_content, 'Problem Statement:')
            code = self.extract_part(meta_content, 'Code:')
            output = self.extract_part(meta_content, 'Terminal Output:')
            gemini_answer = self.extract_part(meta_content, 'Gemini Answer:')

            self.question_text.setPlainText(problem_statement)
            self.editor.setPlainText(code_content)
            self.terminal.clear_output()
            self.terminal.output.append(output)
            self.result_label.setText(gemini_answer)
        else:
            self.editor.setPlainText(content)

    def extract_part(self, content, header):
        parts = content.split(header)
        if len(parts) > 1:
            return parts[1].split('\n\n')[0].strip()
        return ''

    def update_save_button_state(self):
        if hasattr(self, 'current_file'):
            self.save_button.setText('Save')
            self.save_button.setEnabled(True)
        else:
            self.save_button.setText('Save As...')
            self.save_button.setEnabled(True)

    def set_dark_titlebar(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, QColor(40, 44, 52))
    palette.setColor(palette.WindowText, QColor(171, 178, 191))
    palette.setColor(palette.Base, QColor(40, 44, 52))
    palette.setColor(palette.AlternateBase, QColor(53, 57, 69))
    palette.setColor(palette.ToolTipBase, QColor(40, 44, 52))
    palette.setColor(palette.ToolTipText, QColor(171, 178, 191))
    palette.setColor(palette.Text, QColor(171, 178, 191))
    palette.setColor(palette.Button, QColor(62, 68, 81))
    palette.setColor(palette.ButtonText, QColor(171, 178, 191))
    palette.setColor(palette.BrightText, QColor(253, 128, 95))
    palette.setColor(palette.Link, QColor(91, 123, 204))
    palette.setColor(palette.Highlight, QColor(91, 123, 204))
    palette.setColor(palette.HighlightedText, QColor(40, 44, 52))
    app.setPalette(palette)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())