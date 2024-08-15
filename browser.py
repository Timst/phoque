import logging
from time import sleep
import subprocess
import re

class Browser:
    def launch_browser_windows(self):
        layout = self.get_monitor_layout()

        public_monitor, admin_monitor = (layout[0], layout[1]) if layout[0]["height"] == 1080 else (layout[1], layout[0])

        logging.debug("Opening windows")
        admin_id = self.open_window("localhost:5000/admin", 1)
        public_id = self.open_window("localhost:5000/public", 2)

        logging.debug("Moving windows")
        self.move_window_to_monitor(admin_id, admin_monitor)
        self.move_window_to_monitor(public_id, public_monitor)

    def get_monitor_layout(self):
        output = subprocess.check_output(["xrandr"]).decode()
        monitors = []
        for line in output.split('\n'):
            if ' connected' in line:
                match = re.search(r'(\S+) connected (?:primary )?([-\d+]+)x([-\d+]+)\+(\d+)\+(\d+)', line)
                if match:
                    name, width, height, x, y = match.groups()
                    monitors.append({
                        'name': name,
                        'width': int(width),
                        'height': int(height),
                        'x': int(x),
                        'y': int(y)
                    })

        return monitors

    def open_window(self, url: str, expected_windows: int) -> str:
        subprocess.Popen(["firefox-esr", "-new-window", url])
        logging.debug("Open firefox on " + url)

        window_ids = []

        while len(window_ids) < expected_windows:
            logging.debug("Looking for browser window...")
            wmctrl_output = subprocess.check_output(["/bin/bash", "-c", "(wmctrl -l | grep Firefox | cut -d \" \" -f 1) || true"]).decode()
            if wmctrl_output != '':
                window_ids = wmctrl_output.strip().split("\n")
            sleep(1)

        logging.debug("Window ID:" + window_ids[-1])
        return window_ids[-1]

    def move_window_to_monitor(self, window_id: str, monitor):
        # Move and resize the window
        subprocess.run(["wmctrl", "-ir", window_id, "-e", f"0,{monitor['x']},{monitor['y']},{monitor['width']},{monitor['height']}"])
        logging.debug(f"Moved to {monitor['x']}, {monitor['y']} on monitor with height {monitor['height']} and width {monitor['width']}")

        subprocess.Popen(["/usr/bin/wmctrl", "-i", "-r", window_id, "-b", "add,fullscreen"])
        logging.debug("Maximized window")
