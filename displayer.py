import os
import sys
import inspect

import keyboard
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtWidgets import (QTextEdit, QWidget, QPushButton, QHBoxLayout, QApplication,
        QLineEdit, QVBoxLayout, QMessageBox, QInputDialog)
from PySide6.QtCore import QVariantAnimation, Slot, QTimer, Signal, QStringConverterBase
from PySide6.QtGui import QAction, QShortcut, QKeySequence, QFont
import qdarktheme


longText = "\n".join(["{}: long text - auto scrolling ".format(i) for i in range(20)])



#! TBD add enough /n to fill screen, remove them to add value and 
#! then put the \n back
#! TBD make speed variable, depends on number of characters in a line
#! check different screen sizes, font sizes



class AnimationTextEdit(QTextEdit):
    is_paused = False
    speed = 20

    def __init__(self, *args, **kwargs):
        QTextEdit.__init__(self, *args, **kwargs)
        self.setReadOnly(True)
        self.animation = QVariantAnimation(self)
        self.animation.valueChanged.connect(self.moveToLine)
        
        self.animation.setStartValue(0)
        
        self.animation.setLoopCount(-1)
        self.setFont(QFont("Arial", 20))

    @Slot()
    def moveToLine(self, i):
        #print(self.animation.state().name)
        #print(self.animation.state().value)
        self.verticalScrollBar().setValue(i)

    @Slot()
    def add_text(self, input:str):
        print(self.document().lineCount(), self.verticalScrollBar().maximum())
        #self.undo() # Remove all \n last appended
        self.animation.stop()
        self.append(input) 
        #self.append("\n\n\n\n\n\n\n\n\n\n\n\n") # Append \n for visibility

        self.animation.setStartValue(0)
        self.animation.setEndValue(self.verticalScrollBar().maximum())
        self.animation.setDuration(self.animation.endValue()*20)
        self.animation.start()

    #@Slot()
    #def add_text(self, input:str):
    #    #print(self.document().lineCount(), self.verticalScrollBar().maximum())
    #    self.append(input)
    #    self.animation.setEndValue(self.verticalScrollBar().maximum()) 
    #    self.animation.setDuration((self.animation.endValue() - self.verticalScrollBar().value())*self.speed)
    #    if self.animation.state().name == "Stopped":
    #        self.animation.setStartValue(0)
    #        self.animation.start()

    @Slot()
    def pause_toggle(self, pause):
        # if self.animation.state().name == "Paused"
        # if self.animation.state().name == "Running"
        if pause:
            self.animation.pause()
            self.is_paused = True
        else:
            self.animation.resume()
            self.is_paused = False

class LineEdit(QLineEdit):
    new_input = Signal(str)
    def __init__(self):
        QLineEdit.__init__(self)
        keyboard.add_hotkey('Enter', self.next_line)

    @Slot(str)
    def next_line(self):
        if len(self.text()) > 0:
            self.new_input.emit(" - " + self.text())
            #! TO UNCOMMENT:
            #self.clear()


class PauseButton(QPushButton):
    pause_sig = Signal(bool)

    def __init__(self):
        super(PauseButton, self).__init__()
        self.setText("pause scrolling")
        self.setCheckable(True)
        self.clicked.connect(self.on_click_function)

    def on_click_function(self, check):
        if not check:
            self.setText("pause scrolling")
            self.pause_sig.emit(check)
        else:
            self.setText("resume scrolling")
            self.pause_sig.emit(check)

class SpeedButtons(QVBoxLayout):
    speed_delta_sig = Signal(int)
    
    def __init__(self):
        super(SpeedButtons, self).__init__()

        self.layout.addWidget()


class ButtonsWidget(QWidget):
    def __init__(self):
        super(ButtonsWidget, self).__init__()
        self.layout = QVBoxLayout(self)

        self.pauseButton = PauseButton()
        self.layout.addWidget(self.pauseButton)

        #self.pauseButton.pause_sig.connect()

class Displayer(QWidget):
    def __init__(self):
        super(Displayer, self).__init__()
        #self.setFixedSize(600, 400)
        self.setGeometry(0, 0, 800, 800)
        self.showMaximized()

        # Create objects
        self.txt = AnimationTextEdit(self)
        self.inputBox = LineEdit()
        #!self.txt.append(longText)
        self.buttonsWidget = ButtonsWidget()

        # Connecting signals and slots
        self.inputBox.new_input.connect(self.txt.add_text)
        self.buttonsWidget.pauseButton.pause_sig.connect(self.txt.pause_toggle)

        # Layout
        self.layout = QHBoxLayout(self)
        self.text_layout = QVBoxLayout()
        self.text_layout.addWidget(self.txt)
        self.text_layout.addWidget(self.inputBox)
        self.layout.addLayout(self.text_layout, 75)
        self.layout.addWidget(self.buttonsWidget, 25)




    def savefunc(self, title):
        text_to_save = self.txt.toPlainText()
        # write to txt
        txtfilepath = os.path.join(self.save_folder, title + ".txt")
        with open(txtfilepath, 'w') as f:
            f.write(text_to_save)
        # write to png
        #pngfilepath = os.path.join(self.save_folder, title + ".png")
        #img = Image.new("RGB", (800, 400))
        #fontpath = os.path.join(self.file_folder, "GemunuLibre.ttf")
        ##fnt = ImageFont.load(fontpath)
        ##fnt = ImageFont.load_default()
        #fnt = ImageFont.truetype(fontpath, 20)
        #d = ImageDraw.Draw(img)
        #d.multiline_text((10, 10), text_to_save, fill=(255, 255, 255)) # , font = fnt
        #img.save(pngfilepath)

    def get_save_title(self):
        title_is_valid = False
        self.file_folder = os.path.dirname(inspect.stack()[1].filename)
        self.save_folder = os.path.join(self.file_folder, "data")
        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)
            print(f"Folder data created! Data will be stored here:\n {os.path.abspath(self.save_folder)}")
        list_files_in_folder = os.listdir(self.save_folder)
        inputbox_msg = "Enter title for saving:"
        while not title_is_valid:
            title_inputbox, ok = QInputDialog.getText(None, "", inputbox_msg)
            if not ok:
                continue
            if title_inputbox not in list_files_in_folder:
                title_is_valid = True
            else:
                inputbox_msg = f"{title_inputbox} already among saved files! choose another."
        return title_inputbox

    def closeEvent(self, event):
        quit_msg = "Do you want to save?"
        reply = QMessageBox.question(self, "", 
                            quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            title_inputbox = self.get_save_title()
            self.savefunc(title_inputbox)
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = Displayer()
    window.show()
    sys.exit(app.exec())