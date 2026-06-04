# ArduinoSliderMouse

Use an Arduino slider (like a potentiometer or slide potentiometer) as a mouse
controller for any PC game or application.

## Overview

This script reads positional slider data from an Arduino connected over serial and
running the provided sketch, mapping the slider's position horizontal mouse
movements  on a selected monitor. Designed for user in Prof. Burden's lab for
ongoing research at UW.

## Quick Start

```bash
pip install git+https://github.com/EmDash00/ArduinoSliderMouse.git
```

```bash
slider_mouse -h
usage: slider-mouse [-h] [--baud BAUD] [--slider_min SLIDER_MIN] [--slider_max SLIDER_MAX] port

Use an arduino slider as a mouse. Toggable with F1.

positional arguments:
  port                  USB Port

options:
  -h, --help            show this help message and exit
  --baud, -b BAUD       Baud rate
  --slider_min, -m SLIDER_MIN
                        Minimum slider value
  --slider_max, -M SLIDER_MAX
                        Maximum slider value
```

## How It Works

The Arduino sends 6-byte packets containing three 16-bit integers
(`hhh` struct format). The script:

1. Reads the slider position data

2. Maps the position (0-663) to the width of your selected monitor

3. Moves the mouse cursor horizontally across the screen at a fixed vertical
position (middle of the monitor)
