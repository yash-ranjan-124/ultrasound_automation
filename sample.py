from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QRubberBand, QApplication, QVBoxLayout


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        for text in 'One Two Three Four Five'.split():
            layout.addWidget(QPushButton(text, self))
        self.rubberband = QRubberBand(
            QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())
        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            selected = []
            rect = self.rubberband.geometry()
            for child in self.findChildren(QPushButton):
                if rect.intersects(child.geometry()):
                    selected.append(child)
            print('Selection Contains:\n '),
            if selected:
                print('  '.join(
                    'Button: %s\n' % child.text() for child in selected))
            else:
                print(' Nothing\n')
        QWidget.mouseReleaseEvent(self, event)


if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
