# coding: utf-8

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout,  QGraphicsOpacityEffect, QApplication, QFrame
from PySide6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, Slot, QSize
from PySide6.QtGui import QPainter, QColor, QPen
import sys
import multiprocessing
import psutil

class SpinnerWidget(QWidget):
    def __init__(self, base_size=64, lines=12, color="#4c94f4", parent=None):
        super().__init__(parent)
        self._lines = lines
        self._current = 0
        self._color = QColor(color)
        self._base_size = base_size  # tamanho de referência
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

        # inicializa com base_size
        self.setFixedSize(base_size, base_size)

    def resize_for_parent(self, parent_size: QSize):
        """Ajusta dinamicamente o tamanho do spinner com base no parent."""
        side = min(parent_size.width(), parent_size.height())
        size = max(46, int(side * 0.13))  # ocupa ~13% do menor lado
        self.setFixedSize(size, size)
        self.update()

    def start(self):
        if not self._timer.isActive():
            self._timer.start(80)
        self.update()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()
        self.update()

    @Slot()
    def _rotate(self):
        self._current = (self._current + 1) % self._lines
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)

        radius = min(w, h) / 2 - 4
        inner = radius * 0.5
        line_length = radius - inner
        pen_width = max(2, int(radius * 0.12))

        for i in range(self._lines):
            painter.save()
            angle = 360 * i / self._lines
            painter.rotate(angle)

            idx = (i + self._current) % self._lines
            alpha = 40 + int(215 * idx / max(1, self._lines - 1))

            color = QColor(self._color)
            color.setAlpha(alpha)

            pen = QPen(color)
            pen.setWidth(pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, -inner, 0, -inner - line_length)
            painter.restore()

class LoadingOverlay(QWidget):
    def __init__(self, parent_widget, backdrop=20):
        super().__init__(parent_widget)
        self._parent = parent_widget
        self._active = False
        self._backdrop_color = self._parse_backdrop(backdrop)

        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner = QWidget(self)
        inner.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner responsivo
        self.spinner = SpinnerWidget(parent=inner)
        inner_layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignCenter)

        # Label responsiva
        self.label = QLabel("", inner)
        self.label.setStyleSheet("color: #4c94f4; margin-top: 8px; background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.hide()
        inner_layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(inner, 0, Qt.AlignmentFlag.AlignCenter)

        if parent_widget:
            self.setGeometry(0, 0, parent_widget.width(), parent_widget.height())
            parent_widget.installEventFilter(self)

        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(200)

        self.hide()

    def _parse_backdrop(self, backdrop):
        backdrop = (0, 0, 0, backdrop)
        r, g, b, a = map(float, backdrop)
        if 0.0 <= a <= 1.0:
            a = int(a * 255)
        else:
            a = int(a)
        r, g, b = int(r), int(g), int(b)
        return QColor(r, g, b, max(0, min(255, a)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self._backdrop_color)
        super().paintEvent(event)

    def eventFilter(self, watched, event):
        if watched is self._parent:
            if event.type() in (QEvent.Type.Resize, QEvent.Type.Move):
                self.setGeometry(0, 0, self._parent.width(), self._parent.height())
                self._update_responsiveness()
        return super().eventFilter(watched, event)

    def _update_responsiveness(self):
        """Atualiza dinamicamente spinner e label conforme tamanho do parent."""
        if self._parent:
            parent_size = self._parent.size()
            self.spinner.resize_for_parent(parent_size)

    def start(self, text: str = "", with_fade=True):
        self._active = True
        if self._parent:
            self.setGeometry(0, 0, self._parent.width(), self._parent.height())
        self.raise_()
        self.show()

        if text.strip():
            self.label.setText(text.strip())
            self.label.show()
        else:
            self.label.hide()

        self._update_responsiveness()
        self.spinner.start()

        if with_fade:
            self._anim.stop()
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._effect.setOpacity(1.0)

    def stop(self, with_fade=True):
        self._active = False
        if with_fade:
            self._anim.stop()
            self._anim.setStartValue(self._effect.opacity())
            self._anim.setEndValue(0.0)

            def on_finished():
                self._anim.finished.disconnect(on_finished)
                self.spinner.stop()
                self.hide()

            self._anim.finished.connect(on_finished)
            self._anim.start()
        else:
            self.spinner.stop()
            self.hide()

    def delete(self, with_fade=True):
        self.stop(with_fade)
        self.setParent(None)
        self.deleteLater()

def overlay_process(pipe_conn, main_pid, backdrop=20):
    app = QApplication([])

    overlay = LoadingOverlay(parent_widget=None, backdrop=backdrop)
    overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
    overlay.setAttribute(Qt.WA_TranslucentBackground)
    overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
 
    overlay.show()

    overlay_requested = False

    def check_pipe():
        nonlocal overlay_requested

        if not is_process_alive(main_pid):
            print('LoadingOverlayApp closed')
            app.quit()
            return

        while pipe_conn.poll():
            cmd = pipe_conn.recv()
            action = cmd.get("action")
            if action == "show":
                geom = cmd["geometry"]
                text = cmd.get("text", "")
                overlay.setGeometry(*geom)
                overlay.spinner.resize_for_parent(QSize(geom[2], geom[3]))
                overlay.start(text=text)
                overlay_requested = True
            elif action == "hide":
                overlay.stop()
                overlay_requested = False
            elif action == "exit":
                app.quit()

        if overlay_requested and is_main_active(main_pid):
            if not overlay.isVisible():
                overlay.show()
        else:
            overlay.hide()

    def is_process_alive(pid):
        return psutil.pid_exists(pid)

    def is_main_active(pid):
        if sys.platform != "win32":
            return True
        try:
            import win32gui
            import win32process
            foreground = win32gui.GetForegroundWindow()
            _, fg_pid = win32process.GetWindowThreadProcessId(foreground)
            return fg_pid == pid
        except:
            return True

    # Timer para verificar mensagens do pipe
    timer = QTimer()
    timer.timeout.connect(check_pipe)
    timer.start(50)

    sys.exit(app.exec())

# ---------------- Overlay Wrapper ----------------
class LoadingOverlayApp:
    def __init__(self, main_pid : int, backdrop : int = 20):
        self._parent_conn, child_conn = multiprocessing.Pipe()
        self._proc = multiprocessing.Process(
            target=overlay_process, args=(child_conn, main_pid, backdrop), daemon=True
        )
        self._proc.start()

    def start(self, x, y, width, height, text="Loading..."):
        self._parent_conn.send({"action": "show", "geometry": (x, y, width, height), "text": text})

    def stop(self):
        self._parent_conn.send({"action": "hide"})

    def close(self):
        self._parent_conn.send({"action": "exit"})
        self._proc.join()
