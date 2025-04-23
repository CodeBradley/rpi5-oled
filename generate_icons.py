#!/usr/bin/env python3
"""
Script to generate default icons for the Raspberry Pi 5 OLED display application.
This creates simple monochrome icons for SSH and Docker status.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory if it doesn't exist
icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

# Icon size (8x8 pixels)
ICON_SIZE = (8, 8)

# Create SSH active icon
ssh_active = Image.new("1", ICON_SIZE, 0)  # 0 = black background
draw = ImageDraw.Draw(ssh_active)
draw.rectangle([(0, 0), (7, 7)], outline=1)  # 1 = white outline
draw.text((1, 0), "S", fill=1, font=ImageFont.load_default())
ssh_active.save(os.path.join(icons_dir, "ssh_active.png"))

# Create SSH inactive icon
ssh_inactive = Image.new("1", ICON_SIZE, 0)
draw = ImageDraw.Draw(ssh_inactive)
draw.rectangle([(0, 0), (7, 7)], outline=1)
draw.line([(0, 0), (7, 7)], fill=1)  # X mark
draw.line([(0, 7), (7, 0)], fill=1)
ssh_inactive.save(os.path.join(icons_dir, "ssh_inactive.png"))

# Create Docker active icon
docker_active = Image.new("1", ICON_SIZE, 0)
draw = ImageDraw.Draw(docker_active)
draw.rectangle([(0, 0), (7, 7)], outline=1)
draw.text((1, 0), "D", fill=1, font=ImageFont.load_default())
docker_active.save(os.path.join(icons_dir, "docker_active.png"))

# Create Docker inactive icon
docker_inactive = Image.new("1", ICON_SIZE, 0)
draw = ImageDraw.Draw(docker_inactive)
draw.rectangle([(0, 0), (7, 7)], outline=1)
draw.line([(0, 0), (7, 7)], fill=1)  # X mark
draw.line([(0, 7), (7, 0)], fill=1)
docker_inactive.save(os.path.join(icons_dir, "docker_inactive.png"))

print("Icons generated successfully in the 'icons' directory.")
