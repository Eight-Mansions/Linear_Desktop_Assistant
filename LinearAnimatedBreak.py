import random
from pathlib import Path

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel


class LinearAnimatedBreak(QWidget):
    """
    Widget that shows Linear reading a book during the break. Has a lot of specific timing
    information for when she should look at you and smile and blink, it's kind of silly
    amounts of little tweaks
    """

    def __init__(self, width, height, image_dir, *args, **kwargs):
        super(LinearAnimatedBreak, self).__init__(*args, **kwargs)

        self.width = width
        self.height = height
        self.resize(self.width, self.height)

        self.current_index = 0
        self.page_read_counter = 0
        self.current_name = ""
        self.PAGE_READ_SPEED = 5
        self.ANIMATION_SPEED = 500
        self.BLINK_MIN = 4
        self.BLINK_MAX = 10
        self.next_blink = random.randint(self.BLINK_MIN, self.BLINK_MAX)

        # Create main stage label
        self.image_label = QLabel(parent=self)
        self.image_label.move(200, 270)

        # Load all the images from the base directory
        self.images = {}
        self.images_closed = {}
        for path in Path(image_dir).glob("*.png"):
            # Filenames are in the format of "Descriptive_Title_EyeStatus_Index.png"
            name = "".join(path.name.split("_")[:-2])
            eye_status = path.name.split("_")[-2]
            index = int(path.name.split(".")[0][-1:])

            if name not in self.images:
                self.images[name] = {}
                self.images_closed[name] = {}

            # Load the image, then save off the reference
            image = Image.open(path.absolute())
            image = image.resize((400, 400))

            if eye_status == "Closed":
                self.images_closed[name][index] = image
            else:
                self.images[name][index] = image

        # Load up a random default image
        self.randomize_image_name()
        self.update_image()

        # Set up the update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animation_update)
        self.timer.start(self.ANIMATION_SPEED)

    def randomize_image_name(self):
        """
        Sets the current image to use during the render step. Favors reading more than looking at the user.
        """
        # Artificial weight to make staring less common
        for x in range(1, 4):
            self.current_name = random.choice(list(self.images.keys()))
            if "Smile" not in self.current_name:
                break

    def animation_update(self):
        """
        Updates the current index and frame names to be used by the update_image function
        """
        # Delay so Linear reads the current page for a while
        if self.current_index == 0:
            if self.page_read_counter < self.PAGE_READ_SPEED:
                self.page_read_counter += 1

                # Update the image so that blinking can happen during the reading phase
                self.update_image()
                return

            # If page reading is finished, reset the counter and start the page turn animation
            self.page_read_counter = 0

        # Check to see if we're at the end of the animation
        self.current_index += 1
        if self.current_index >= len(self.images[self.current_name]):
            self.current_index = 0
            self.randomize_image_name()

        self.update_image()

    def update_image(self):
        """
        Renders the next image in the animation sequence. If the blink timer is reached,
        the blink version of the frame is used and a new blink timer is set.
        """
        self.next_blink -= 1
        if self.next_blink <= 0:
            self.next_blink = random.randint(self.BLINK_MIN, self.BLINK_MAX)
            image = self.images_closed[self.current_name][self.current_index]
        else:
            image = self.images[self.current_name][self.current_index]
        self.image_label.setPixmap(QPixmap.fromImage(ImageQt(image)))

    def hide(self):
        """
        Overrides the default hide to turn off the animation timer first.
        """
        self.timer.stop()
        super(LinearAnimatedBreak, self).hide()

    def show(self):
        """
        Overrides the default show to turn on the animation timer first
        """
        self.timer.start(self.ANIMATION_SPEED)
        super(LinearAnimatedBreak, self).show()
