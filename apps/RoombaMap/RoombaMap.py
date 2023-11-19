import hassapi as hass
import csv
import os
from PIL import Image, ImageDraw#, ImageFont

# You can adjust colors and style here
LINE_THICKNESS = 2
LINE_COLOR_RGB = (255, 0, 0)

POINT_COLOR_RUNNING = (0, 255, 0)
POINT_COLOR_RETURN = (255, 255, 0)
POINT_COLOR_STUCK = (0, 0, 255)
POINT_COLOR_DOCKED = (255, 255, 255)

VACUUM_LOG_RAW_PATH = "{tmp_path}/vacuum_{name}/vacuum.log"
MAP_OUTPUT_RAW_PATH = "{tmp_path}/vacuum_{name}/map.png"

#font = ImageFont.truetype("fonts/Arimo-Bold.ttf", size=32)


class Generate(hass.Hass):
    """
    Generates a map of the area cleaned by Roomba.
    """

    def initialize(self):
        self.log("Initializing RoombaMap..")
        # Init arguments
        self.debug = bool(self.args['debug']) if 'debug' in self.args else False

        self.vacuum_entity = self.get_entity(self.args['vacuum_entity'])
        self.vacuum_entity_id = self.args['vacuum_entity']

        self.map_base_image = self.args['map_base_image']
        self.map_offset_x = int(self.args['map_offset_x'])
        self.map_offset_y = int(self.args['map_offset_y'])
        self.map_rotation = int(self.args['map_rotation'])

        self.tmp_path = self.args['tmp_path']

        # Init vars
        self.line_space = 0
        self.draw = None

        self.vacuum_cords = []
        self.draw_last_x = 0
        self.draw_last_y = 0
        self.write_log_to_file = True

        self.vacuum_name = self.vacuum_entity_id.split(".")[1]
        self.vacuum_log_path = (VACUUM_LOG_RAW_PATH
                                .replace("{tmp_path}", self.tmp_path)
                                .replace("{name}", self.vacuum_name))
        self.map_output_path = (MAP_OUTPUT_RAW_PATH
                                .replace("{tmp_path}", self.tmp_path)
                                .replace("{name}", self.vacuum_name))

        # Prepare paths
        os.makedirs(name=os.path.dirname(self.vacuum_log_path), exist_ok=True)
        os.makedirs(name=os.path.dirname(self.map_output_path), exist_ok=True)
        if not os.path.exists(self.vacuum_log_path):
            open(self.vacuum_log_path, "x")

        # Load app
        self.load_log()
        self.generate_image(preparing=True)

        # Listeners
        self.run_every(self.generate_image, start="now+10", interval=10)
        self.entity_vacuum.listen_state(self.write_log, attribute="position")
        self.entity_vacuum.listen_state(self.clear_log, old="docked", new="cleaning", duration=10)
        self.entity_vacuum.listen_state(self.save_log, new="docked")

        self.log("RoombaMap initialized!")

    def clog(self, msg):
        if self.debug:
            self.log(msg)

    """
    Coords logging UTILS
    """
    def load_log(self):
        """
        Loads the log from file.
        """
        self.clog("Loading log file..")

        with open(self.vacuum_log_path, 'r') as f:
            reader = csv.reader(f, delimiter=",")

            for row in reader:
                x = int(row[0])
                y = int(row[1])
                self.vacuum_cords.append([x, y])

    def save_log(self, entity=None, attribute=None, old=None, new=None, kwargs=None):
        """
        Save the log to file.
        """
        self.clog("Saving log..")
        with open(self.vacuum_log_path, "r+") as f:
            f.truncate(0)

        with open(self.vacuum_log_path, "a") as f:
            for c in self.vacuum_cords:
                f.write(f"{c[0]},{c[1]}\n")

    def write_log(self, entity, attribute, old, new, kwargs):
        """
        Add current coords to log. This doesn't save the log to file.
        """
        vacuum_position = new.strip("()").split(', ')
        x = int(vacuum_position[0])
        y = int(vacuum_position[1])

        self.vacuum_cords.append([x, y])

        # Save log after every write for debug
        if self.debug:
            with open(self.vacuum_log_path, "a") as f:
                f.write(f"{x},{y}\n")

    def clear_log(self, entity=None, attribute=None, old=None, new=None, kwargs=None):
        """
        Clears the coords array and the file
        """
        self.clog("Clearing log..")
        self.vacuum_cords = []
        with open(self.vacuum_log_path, 'r+') as f:
            f.truncate(0)

    """
    Image tools
    """

    def draw_point(self, x, y, color, size=35):
        x2 = x + size
        y2 = y + size

        self.draw.ellipse([(x, y), (x2, y2)], color)

    """
    Generate Map Image
    """

    def generate_image(self, entity=None, attribute=None, old=None, new=None, kwargs=None, preparing=False):
        """
        Generates the image and saves it to disk.
        """
        # Get current vacuum state
        vacuum_state = self.vacuum_entity.get_state()

        # Stop updating the image if Roomba is docked since one minute or longer to reduce processor use and storage wear.
        docked_since_one_min = self.render_template(
            "{{ is_state('" + self.vacuum_entity_id + "', 'docked') and (now() > states." + self.vacuum_entity_id + ".last_changed + timedelta(minutes=1)) }}")
        # self.clog("Image will be generated: "+str(not docked_since_one_min))
        if not preparing and docked_since_one_min:
            return

        # Load base image
        image = Image.open(self.map_base_image)
        image = image.rotate(self.map_rotation)
        self.draw = ImageDraw.Draw(image)

        # Draw lines
        first_run = True
        for c in self.vacuum_cords:
            x = c[0] + self.offset_cords_x
            y = c[1] + self.offset_cords_y

            if first_run:
                first_run = False
            else:
                self.draw.line([(y, x), (self.draw_last_y, self.draw_last_x)], width=LINE_THICKNESS,
                               fill=LINE_COLOR_RGB)

            self.draw_last_x = x
            self.draw_last_y = y

        # Draw dot of current location
        if vacuum_state == "docked":
            self.draw_point(self.draw_last_y, self.draw_last_x, POINT_COLOR_DOCKED)
        elif vacuum_state == "return":
            self.draw_point(self.draw_last_y, self.draw_last_x, POINT_COLOR_RETURN)
        elif vacuum_state == "stuck":
            self.draw_point(self.draw_last_y, self.draw_last_x, POINT_COLOR_STUCK)
        else:
            self.draw_point(self.draw_last_y, self.draw_last_x, POINT_COLOR_RUNNING)

        # Rotate image back to default & save
        image = image.rotate(-self.map_rotation)
        image.save(self.map_output_path, "PNG")
