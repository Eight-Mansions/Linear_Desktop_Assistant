import os
import shutil
from pathlib import Path
from sys import argv
from sys import exit

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu

from DesktopAssistant.BreakReminderWidget import BreakReminderWidget
from DesktopAssistant.ConfigReader import ConfigReader


class DesktopAssistantGUI:
    WIDTH = 600
    HEIGHT = 600
    TASKBAR_HEIGHT = 40

    def __init__(self):

        self.config = ConfigReader()
        self.app = QApplication(argv)

        # Create a transparent main window that's always on top
        # QtCore.Qt.Tool removes the icon from the taskbar
        self.window = QWidget()
        self.window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                                   | Qt.WindowType.Tool)

        # Create the widget itself
        self.reminder = BreakReminderWidget(self.WIDTH, self.HEIGHT, self.config, parent=self.window)

        self.reminder.show_scene()

        # Create a system tray icon
        self.system_tray = QSystemTrayIcon()
        icon = QIcon(os.path.join("Images", "wrinkle.png"))
        self.system_tray.setIcon(icon)
        self.system_tray.setVisible(True)

        # Create various system tray menu options
        self.system_tray_menu = QMenu()

        exit_action = QAction("Exit")
        exit_action.triggered.connect(exit)

        open_config_action = QAction("Edit Config")
        open_config_action.triggered.connect(self.open_config_file)

        end_work_action = QAction("Take Break Early")
        end_work_action.triggered.connect(self.reminder.show_break_dialog)

        self.remaining_time_action = QAction(f"Remaining Time: Loading...")
        self.system_tray_menu.aboutToShow.connect(self.update_timer_display)

        self.system_tray_menu.addAction(self.remaining_time_action)
        self.system_tray_menu.addSeparator()

        self.system_tray_menu.addAction(end_work_action)
        self.system_tray_menu.addAction(open_config_action)
        self.system_tray_menu.addSeparator()

        position_menu = self.system_tray_menu.addMenu("Window Position")
        saved_position = self.config.get_saved_position()
        self.default_position_action = QAction("Default Position")
        self.default_position_action.setCheckable(True)
        self.default_position_action.triggered.connect(self.change_position_default)

        if saved_position == 0:
            self.default_position_action.setChecked(True)

        self.position_one_action = QAction("Position One")
        self.position_one_action.setCheckable(True)
        self.position_one_action.triggered.connect(self.change_position_one)

        if saved_position == 1:
            self.position_one_action.setChecked(True)

        self.position_two_action = QAction("Position Two")
        self.position_two_action.setCheckable(True)
        self.position_two_action.triggered.connect(self.change_position_two)

        if saved_position == 2:
            self.position_two_action.setChecked(True)

        position_menu.addAction(self.default_position_action)
        position_menu.addAction(self.position_one_action)
        position_menu.addAction(self.position_two_action)

        self.system_tray_menu.addSeparator()
        self.system_tray_menu.addAction(exit_action)
        self.system_tray_menu.addSeparator()
        self.system_tray.setContextMenu(self.system_tray_menu)

        # Determine bottom right corner of screen, then place the window
        # Reads any saved offsets from the config file and loads the last used
        self.set_position_from_config()

        self.window.show()
        self.app.exec()

    def update_timer_display(self):
        """
        Updates the timer that appears in the system tray for remaining work time
        :return:
        """
        remaining_time = self.reminder.active_timer.remainingTime()

        # If no timer is running, just report that
        if remaining_time < 0:
            self.remaining_time_action.setText(f"Remaining Time: None")
            return

        # Otherwise format it nicely
        minutes = int((remaining_time / 1000) // 60)
        seconds = int(remaining_time / 1000) % 60

        self.remaining_time_action.setText(f"Remaining Time: {minutes}:{seconds:02}")

    def open_config_file(self):
        """
        Opens the local config file in a text editor to edit
        :return:
        """

        # If a local config doesn't exist, create it
        if not Path("local-config.txt").exists():
            shutil.copyfile("base-config.txt", "local-config.txt")

        os.startfile("local-config.txt")

    def set_position_from_config(self):
        """
        Reads the last used position from the local config file and uses it
        :return:
        """
        if self.config.get_saved_position() == 1:
            self.change_position_one()
        elif self.config.get_saved_position() == 2:
            self.change_position_two()
        else:
            self.change_position_default()

    def change_position_default(self):
        self.config.set_current_position(0)
        self.change_position((0, 0))
        self.default_position_action.setChecked(True)
        self.position_one_action.setChecked(False)
        self.position_two_action.setChecked(False)

    def change_position_one(self):
        self.config.set_current_position(1)
        self.change_position(self.config.get_position_one_offsets())
        self.default_position_action.setChecked(False)
        self.position_one_action.setChecked(True)
        self.position_two_action.setChecked(False)

    def change_position_two(self):
        self.config.set_current_position(2)
        self.change_position(self.config.get_position_two_offsets())
        self.default_position_action.setChecked(False)
        self.position_one_action.setChecked(False)
        self.position_two_action.setChecked(True)

    def change_position(self, offsets):
        """
        Positions the widget using the primary screen's bottom left as a starting point,
        then uses the defined offsets to reposition

        Changing the monitor was too hard, sorry :P
        :param offsets:
        :return:
        """
        offset_x = offsets[0]
        offset_y = offsets[1]

        screen_geometry = self.app.primaryScreen().availableGeometry()
        x = screen_geometry.width() - self.WIDTH + offset_x
        y = screen_geometry.height() - self.HEIGHT - self.TASKBAR_HEIGHT + offset_y
        self.window.setGeometry(x, y, self.WIDTH, self.HEIGHT)


# Start!
DesktopAssistantGUI()
