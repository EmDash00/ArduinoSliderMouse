#!/usr/bin/env python

import argparse
import struct
from threading import Thread

import cv2
import mss
import numpy as np
from mss.models import Monitor
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

# import mouse
from pynput.mouse import Controller
from serial import Serial

DEFAULT_SLIDER_MAX = 663


def select_monitor() -> tuple[int, Monitor]:
    """
    Displays labeled screenshots of several monitors. The user is
    prompted to select one.
    """

    with mss.mss() as sct:
        selected_monitor_index = 0

        def get_monitor_selection():
            nonlocal selected_monitor_index

            while True:
                print(
                    "Pick the monitor you will play the game on. Previews are "
                    f"shown above [1-{len(sct.monitors) - 1}]: ",
                    end="",
                )
                selection = input()

                if len(selection) > 1:
                    print("Please input a monitor number.")
                    continue

                if not selection.isdigit():
                    print("Please input a monitor number.")
                    continue

                index = int(selection)
                if index <= 0 or index >= len(sct.monitors):
                    print("Invalid monitor number.")
                    continue

                selected_monitor_index = index

                break

        if len(sct.monitors) == 2:
            return 1, sct.monitors[1]

        # Skip the first monitor as that's the whole screen (all monitors)
        for i, monitor in enumerate(sct.monitors[1:]):
            screenshot = np.array(sct.grab(monitor))

            # Resize the screenshots to be smallish while maintaining aspect ratio
            aspect_ratio = screenshot.shape[1] / screenshot.shape[0]
            resize_height = 300
            resize_width = int(resize_height * aspect_ratio)
            cv2.imshow(
                f"Monitor {i + 1}",
                cv2.resize(
                    screenshot,
                    (resize_width, resize_height),
                    interpolation=cv2.INTER_AREA,
                ),
            )

        thread = Thread(target=get_monitor_selection)
        thread.start()

        # Keep the windows open until the monitor is selected
        while selected_monitor_index == 0:
            # sleep for 20 ms at a time by waiting for a key with timeout of 20 ms
            cv2.waitKey(20)

        cv2.destroyAllWindows()

        return selected_monitor_index, sct.monitors[selected_monitor_index]


def slider_to_mouse(pos, monitor: Monitor, y0: int):
    if y0 < 0:
        y0 = int(monitor["top"] + 0.5 * monitor["height"])
    return (
        int(monitor["left"] + monitor["width"] * pos),
        y0
    )


class Slider:
    def __init__(
        self,
        port: str,
        baud: int,
        lims: tuple[int, int],
        reverse: bool = False,
    ) -> None:
        self._arduino = Serial(port, baud, timeout=1)
        self._pos = 0
        self._reverse = reverse
        self._min, self._max = lims
        self._range = self._max - self._min

    def get_position(self):
        data = self._arduino.readline()

        if len(data) < 6:
            return -1

        _, _, raw_slider_pos = struct.unpack("hhh", data[:6])
        # print(raw_slider_pos)

        if self._reverse:
            slider_pos = self._max - raw_slider_pos
        else:
            slider_pos = raw_slider_pos - self._min

        # print(slider_pos)

        self._pos = slider_pos / self._range

        return self._pos

    @property
    def pos(self):
        return self._pos

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._arduino.close()


def main():
    parser = argparse.ArgumentParser(
        description="Use an arduino slider as a mouse. Toggable with F1."
    )
    parser.add_argument("port", type=str, help="USB Port")
    parser.add_argument("--baud", "-b", type=int, help="Baud rate", default=9600)
    parser.add_argument(
        "--y_pos", "-y", type=int, help="Mouse y position", default=-1
    )
    parser.add_argument(
        "--slider_min",
        "-m",
        type=int,
        help="Minimum slider value",
        default=0,
    )
    parser.add_argument(
        "--slider_max",
        "-M",
        type=int,
        help="Maximum slider value",
        default=DEFAULT_SLIDER_MAX,
    )
    args = parser.parse_args()
    port, baud = args.port, args.baud
    SLIDER_MIN, SLIDER_MAX = args.slider_min, args.slider_max
    y0 = args.y_pos

    mouse = Controller()
    _, monitor = select_monitor()

    enabled = True

    def toggle_hotkey(key: Key | KeyCode | None):
        nonlocal enabled

        if key == keyboard.Key.f12:
            enabled = not enabled

        print(f"Slider enabled: {enabled}")

    listener = keyboard.Listener(on_press=toggle_hotkey)
    listener.start()

    with Slider(port, baud, lims=(SLIDER_MIN, SLIDER_MAX), reverse=True) as slider:
        while True:
            if (pos := slider.get_position()) < 0:
                continue

            if enabled:
                mouse.position = slider_to_mouse(pos, monitor, y0)


if __name__ == "__main__":
    main()
