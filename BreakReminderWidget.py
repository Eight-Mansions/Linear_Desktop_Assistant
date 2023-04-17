import os

from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QSequentialAnimationGroup, QTimer, QEasingCurve, \
    QParallelAnimationGroup

from DesktopAssistant.LinearAnimatedBreak import LinearAnimatedBreak
from DesktopAssistant.DesktopButton import DesktopButton
from DesktopAssistant.DialogueWidget import DialogueWidget


class BreakReminderWidget(QWidget):
    """
    Handles the animation of linear leaning in and asking the user to take a break
    """
    SLIDE_DURATION = 2_000
    work_count = 0

    dialogue_box = None
    dialogue_fade_in_animation = None
    dialogue_fade_out_animation = None
    active_timer = QTimer()
    stand_timer = QTimer()

    def __init__(self, width, height, config, *args, **kwargs):
        super(BreakReminderWidget, self).__init__(*args, **kwargs)

        self.config = config
        self.active_timer.setSingleShot(True)
        self.stand_timer.setSingleShot(True)
        self.stand_timer.timeout.connect(self.show_stand_dialog)

        # Set our widget to the size specified
        self.width = width
        self.height = height
        self.resize(self.width, self.height)

        # Load and create the main character image
        image = Image.open(os.path.join("Images", "Linear_Wall", "head.png"))
        image = image.resize((400, 400))
        self.main_character_image_label = QLabel(parent=self)
        self.main_character_image_label.setPixmap(QPixmap.fromImage(ImageQt(image)))
        self.main_character_image_label.move(600, 200)

        # Load and create the hands image
        image = Image.open(os.path.join("Images", "Linear_Wall", "hands.png"))
        image = image.resize((400, 400))
        self.hands_character_image_label = QLabel(parent=self)
        self.hands_character_image_label.setPixmap(QPixmap.fromImage(ImageQt(image)))
        self.hands_character_image_label.move(600, 200)

        # Create main body slide
        self.main_character_slide_in_anim = QPropertyAnimation(self.main_character_image_label, b"pos")
        self.main_character_slide_in_anim.setEndValue(QPoint(200, 200))
        self.main_character_slide_in_anim.setDuration(self.SLIDE_DURATION)
        self.main_character_slide_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.main_character_slide_out_anim = QPropertyAnimation(self.main_character_image_label, b"pos")
        self.main_character_slide_out_anim.setEndValue(QPoint(600, 200))
        self.main_character_slide_out_anim.setDuration(self.SLIDE_DURATION)
        self.main_character_slide_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        # Create hand slide
        self.hands_character_slide_in_anim = QPropertyAnimation(self.hands_character_image_label, b"pos")
        self.hands_character_slide_in_anim.setEndValue(QPoint(200, 200))
        self.hands_character_slide_in_anim.setDuration(self.SLIDE_DURATION)
        self.hands_character_slide_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hands_character_slide_out_anim = QPropertyAnimation(self.hands_character_image_label, b"pos")
        self.hands_character_slide_out_anim.setEndValue(QPoint(600, 200))
        self.hands_character_slide_out_anim.setDuration(self.SLIDE_DURATION)
        self.hands_character_slide_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        # Create the break animated portrait
        self.break_portrait = LinearAnimatedBreak(self.width, self.height, os.path.join("Images", "Linear"),
                                                  parent=self)
        self.break_portrait.hide()

        # Create the dialogue box
        self.dialogue_box = DialogueWidget(self.width, self.height, parent=self)
        self.create_startup_dialog_box()

        # Create dialogue box show animation
        self.dialogue_fade_in_animation = QPropertyAnimation(self.dialogue_box, b"pos")
        self.dialogue_fade_in_animation.setEndValue(QPoint(0, 0))
        self.dialogue_fade_in_animation.setDuration(1000)
        self.dialogue_fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.dialogue_fade_out_animation = QPropertyAnimation(self.dialogue_box, b"pos")
        self.dialogue_fade_out_animation.setEndValue(QPoint(0, -200))
        self.dialogue_fade_out_animation.setDuration(1000)
        self.dialogue_fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # Create a sequential animation slide group
        self.character_slide_enter_anim_group = QSequentialAnimationGroup()
        self.character_slide_enter_anim_group.addAnimation(self.hands_character_slide_in_anim)
        self.character_slide_enter_anim_group.addAnimation(self.main_character_slide_in_anim)
        self.character_slide_enter_anim_group.addAnimation(self.dialogue_fade_in_animation)

        self.character_slide_exit_anim_group = QParallelAnimationGroup()
        self.character_slide_exit_anim_group.addAnimation(self.hands_character_slide_out_anim)
        self.character_slide_exit_anim_group.addAnimation(self.main_character_slide_out_anim)
        self.character_slide_exit_anim_group.addAnimation(self.dialogue_fade_out_animation)

        # Create a break progress bar
        self.break_progress_bar = QProgressBar(parent=self)
        self.break_progress_bar.resize(self.width - 200, 15)
        self.break_progress_bar.move(200, self.height - 15)
        self.break_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.break_progress_bar.setFormat("")
        self.break_progress_bar_animation = QPropertyAnimation(self.break_progress_bar, b"value")
        self.break_progress_bar_animation.setEndValue(100)
        self.break_progress_bar_animation.setDuration(self.config.get_break_length())
        self.break_progress_bar.hide()

    def create_break_dialog_box(self):
        # Create a dialogue box
        buttons = [DesktopButton("Take Break", self.begin_break),
                   DesktopButton("Snooze", self.begin_snooze),
                   DesktopButton("Just Starting", self.begin_work)]

        self.dialogue_box.set_buttons(buttons)
        self.dialogue_box.set_dialogue(self.config.get_break_prompt_text())

    def create_startup_dialog_box(self):
        # Create a dialogue box
        buttons = [DesktopButton("Start", self.begin_work)]

        self.dialogue_box.set_buttons(buttons)
        self.dialogue_box.set_dialogue(self.config.get_work_start_text())

    def create_stand_dialog_box(self):
        # Create a dialogue box
        buttons = [DesktopButton("Fine...", self.hide_scene)]

        self.dialogue_box.set_buttons(buttons)
        self.dialogue_box.set_dialogue(self.config.get_stand_up_text())

    def show_start_dialog(self):
        self.update_image_default()

        # Set the image back and hide the progress bar
        image = Image.open(os.path.join("Images", "Linear_Wall", "head.png"))
        image = image.resize((400, 400))
        self.main_character_image_label.setPixmap(QPixmap.fromImage(ImageQt(image)))

        self.break_progress_bar.hide()

        self.create_startup_dialog_box()
        self.show_scene()

    def show_break_dialog(self):
        self.create_break_dialog_box()

        # Stop any active timers in case we skipped here manually
        self.active_timer.stop()

        self.show_scene()

    def show_stand_dialog(self):
        self.update_image_happy()
        self.create_stand_dialog_box()
        self.show_scene()

    def begin_work(self):
        self.update_image_happy()
        self.work_count += 1

        if self.config.get_stand_frequency() > 0 and self.work_count % self.config.get_stand_frequency() == 0:
            self.schedule_stand_notification()

        self.hide_scene()
        self.active_timer.timeout.connect(self.show_break_dialog)
        self.active_timer.start(self.config.get_work_length())

    def begin_snooze(self):
        self.update_image_sad()
        self.hide_scene()
        self.active_timer.timeout.connect(self.show_break_dialog)
        self.active_timer.start(self.config.get_break_length())

    def begin_break(self):
        self.break_portrait.show()
        self.main_character_image_label.hide()
        self.hands_character_image_label.hide()
        self.break_progress_bar.show()
        self.break_progress_bar.setValue(0)
        self.break_progress_bar_animation.start()
        self.dialogue_box.hide()

        self.active_timer.timeout.disconnect()
        self.active_timer.timeout.connect(self.show_start_dialog)
        self.active_timer.start(self.config.get_break_length())

    def schedule_stand_notification(self):
        start_time = self.config.get_work_length() - self.config.get_stand_length()
        self.stand_timer.start(start_time)

    def show_scene(self):
        self.break_portrait.hide()
        self.main_character_image_label.move(600, 200)
        self.main_character_image_label.show()
        self.hands_character_image_label.move(600, 200)
        self.hands_character_image_label.show()
        self.dialogue_box.move(0, -200)
        self.dialogue_box.show()
        self.character_slide_enter_anim_group.start()

    def hide_scene(self):
        self.break_portrait.hide()
        self.main_character_image_label.move(200, 200)
        self.hands_character_image_label.move(200, 200)
        self.dialogue_box.move(0, 0)
        self.character_slide_exit_anim_group.start()

    def update_image_happy(self):
        self.update_image("head_happy.png")

    def update_image_default(self):
        self.update_image("head.png")

    def update_image_sad(self):
        self.update_image("head_sad.png")

    def update_image(self, image_name):
        image = Image.open(os.path.join("Images", "Linear_Wall", image_name))
        image = image.resize((400, 400))
        self.main_character_image_label.setPixmap(QPixmap.fromImage(ImageQt(image)))
