from PyQt5.QtGui import QFont
from pyqode.core.api import ColorScheme
from pyqode.python.backend import server
from pyqode.python.widgets import PyCodeEdit
from pyqode.python.modes import PyAutoIndentMode, PyAutoCompleteMode, PythonSH

class CodeEditor(PyCodeEdit):
    def __init__(self):
        super().__init__()
        self.backend.start(server.__file__)
        self.setLineWrapMode(self.NoWrap)
        self.modes.append(PyAutoIndentMode())
        self.modes.append(PyAutoCompleteMode())
        self.syntax_highlighter.color_scheme = ColorScheme('monokai')
        self.setFont(QFont('Courier', 12))