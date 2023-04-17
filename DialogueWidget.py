import os
from sys import exit

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QPushButton


class DialogueWidget(QWidget):
    """
    Base class for showing a dialogue box, including support for dynamic buttons, text,
    and an exit button
    """

    active_buttons = []

    def __init__(self, width, height, *args, **kwargs):
        super(DialogueWidget, self).__init__(*args, **kwargs)

        self.width = width
        self.height = height
        self.resize(self.width, self.height)

        # Set up background image
        image = Image.open(os.path.join("Images", "DialogueBox.png"))
        image = image.resize((self.width - 200, 150))
        self.background_label = QLabel(parent=self)
        self.background_label.setPixmap(QPixmap.fromImage(ImageQt(image)))
        self.background_label.move(200, 50)

        # Create the text box
        self.text_label = QLabel(parent=self.background_label)
        self.text_label.resize(360, 140)
        self.text_label.move(10, 6)
        self.text_label.setStyleSheet('font-size: 24px; color: white;')
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.text_label.setWordWrap(True)

        # Create the exit button
        self.exit_button = QPushButton(parent=self.background_label)
        self.exit_button.resize(32, 32)
        self.exit_button.move(self.width - 40 - 200, 8)
        self.exit_button.clicked.connect(exit)
        self.exit_button.setText("ⓧ")
        self.exit_button.setStyleSheet('background: transparent; font-size: 24px; color: white')

        # Create all our buttons
        for index, button in enumerate(range(1, 4)):
            button_widget = QPushButton(parent=self.background_label)
            button_widget.move(10 + (index * 130), 110)
            button_widget.resize(120, 30)
            button_widget.setStyleSheet('font-size: 18px')
            button_widget.hide()
            self.active_buttons.append(button_widget)

    def set_buttons(self, buttons):
        """
        Switches the buttons up to a new set to change the layout
        :param buttons - New buttons to display
        """
        # Hide all buttons in case there's less buttons on this next screen
        for button in self.active_buttons:
            button.hide()

        # Show the current button, then wire it up to the new function
        # We must disconnect, otherwise both the new and old function will appear
        for index, button in enumerate(buttons):
            self.active_buttons[index].show()
            self.active_buttons[index].setText(button.text)
            self.active_buttons[index].disconnect()
            self.active_buttons[index].clicked.connect(button.function)

    def set_dialogue(self, dialogue):
        self.text_label.setText(dialogue)
