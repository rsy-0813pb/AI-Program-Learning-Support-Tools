from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QProcess

class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        
        # QProcessオブジェクトを作成
        self.process = QProcess(self)
        
        # プロセスのチャンネルモードをマージモードに設定
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        
        # プロセスの標準出力の準備完了時にハンドラを接続
        self.process.readyReadStandardOutput.connect(self.handle_output)

        # ウィンドウタイトルを設定
        self.setWindowTitle('Terminal')
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 出力用のQTextEditを作成
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { background-color: #282C34; color: #ABB2BF; }")
        layout.addWidget(self.output)

        # 入力用のQLineEditを作成
        self.input = QLineEdit()
        self.input.setStyleSheet("QLineEdit { background-color: #282C34; color: #ABB2BF; }")
        layout.addWidget(self.input)

        # 入力欄でEnterが押されたときにハンドラを接続
        self.input.returnPressed.connect(self.write_input)

    def execute_command(self, command):
        # コマンドを実行
        self.process.start(command)

    def handle_output(self):
        # プロセスの出力を取得してテキストに追加
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf8', errors='replace')
        self.output.append(text)

    def write_input(self):
        # 入力されたテキストを取得
        input_text = self.input.text()
        
        # テキストをプロセスに書き込む
        self.process.write(f'{input_text}\n'.encode())
        
        # 入力されたテキストを出力欄に追加
        self.output.append(f'> {input_text}')
        
        # 入力欄をクリア
        self.input.clear()

    def clear_output(self):
        # 出力欄をクリア
        self.output.clear()

    def get_output(self):
        # 出力欄のテキストを取得
        return self.output.toPlainText()