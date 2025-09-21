# Made and developed by gneval9 Software
# 01-07-2025 (versión con doble buffering)

import mmap
import os
import struct
import time

# Colores ARGB
RED     = 0xFFFF0000
GREEN   = 0xFF00FF00
BLUE    = 0xFF0000FF
WHITE   = 0xFFFFFFFF
BLACK   = 0xFF000000
YELLOW  = 0xFFFFFF00
CYAN    = 0xFF00FFFF
MAGENTA = 0xFFFF00FF
GRAY    = 0xFF888888
ORANGE  = 0xFFFFA500

# Variables globales
fb = None
fb_mem = None
screen_width = 0
screen_height = 0
bits_per_pixel = 32
buffer = None   # Doble buffer en RAM
fb_size = 0


def init():
    """Inicializa el framebuffer y crea el buffer en RAM"""
    global fb, fb_mem, screen_width, screen_height, bits_per_pixel, buffer, fb_size
    fb = os.open("/dev/fb0", os.O_RDWR)

    try:
        with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
            res = f.read().strip()
            screen_width, screen_height = map(int, res.split(","))
    except Exception as e:
        raise RuntimeError(f"No se pudo obtener la resolución del framebuffer: {e}")

    bits_per_pixel = 32
    fb_size = screen_width * screen_height * (bits_per_pixel // 8)

    fb_mem = mmap.mmap(fb, fb_size, mmap.MAP_SHARED,
                       mmap.PROT_WRITE | mmap.PROT_READ, offset=0)

    buffer = bytearray(fb_size)


def draw_pixel(x, y, color):
    """Dibuja un píxel en el buffer virtual (RAM)"""
    try:
        if buffer is None:
            raise RuntimeError("init() no ha sido llamada o framebuffer cerrado.")
        if 0 <= x < screen_width and 0 <= y < screen_height:
            offset = (y * screen_width + x) * 4
            struct.pack_into('I', buffer, offset, color)
    except Exception as e:
        print("FrameDirect ERROR en draw_pixel:", e)


def draw_line(x1, y1, x2, y2, color):
    """Dibuja una línea con el algoritmo DDA"""
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        draw_pixel(x1, y1, color)
        return

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1

    for _ in range(steps + 1):
        draw_pixel(round(x), round(y), color)
        x += x_inc
        y += y_inc


def draw_circle(cx, cy, radius, color):
    """Dibuja un círculo con píxeles"""
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            dist2 = (x - cx) ** 2 + (y - cy) ** 2
            if (radius - 1) ** 2 <= dist2 <= (radius + 1) ** 2:
                draw_pixel(x, y, color)


def fill(color=BLACK):
    """Limpia el buffer con un color sólido"""
    global buffer
    if buffer is None:
        raise RuntimeError("init() no ha sido llamada.")
    pixel = struct.pack('I', color)
    for i in range(0, len(buffer), 4):
        buffer[i:i+4] = pixel


def update():
    """Copia el buffer virtual al framebuffer real"""
    if fb_mem is None or buffer is None:
        raise RuntimeError("init() no ha sido llamada o framebuffer cerrado.")
    fb_mem.seek(0)
    fb_mem.write(buffer)
    time.sleep(1/30)


def resolution():
    """Muestra la resolución actual"""
    print(screen_width, "x", screen_height)


def close():
    """Cierra el framebuffer y libera memoria"""
    global fb, fb_mem, buffer
    if fb_mem is not None:
        fb_mem.close()
        fb_mem = None
    if fb is not None:
        os.close(fb)
        fb = None
    buffer = None

