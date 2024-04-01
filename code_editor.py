from PyQt5.QtGui import QFont
from pyqode.core.api import ColorScheme
from pyqode.python.backend import server
from pyqode.python.widgets import PyCodeEdit
from pyqode.python.modes import PyAutoIndentMode, PyAutoCompleteMode, PythonSH

class CodeEditor(PyCodeEdit):
    def __init__(self):
        super().__init__()
        
        # バックエンドサーバーを起動
        self.backend.start(server.__file__)
        
        # 行の折り返しを無効化
        self.setLineWrapMode(self.NoWrap)
        
        # オートインデントモードを追加
        self.modes.append(PyAutoIndentMode())
        
        # オートコンプリートモードを追加
        self.modes.append(PyAutoCompleteMode())
        
        # シンタックスハイライトにMonokaiカラースキームを設定
        self.syntax_highlighter.color_scheme = ColorScheme('monokai')
        
        # フォントをCourier、サイズ12に設定
        self.setFont(QFont('Courier', 12))