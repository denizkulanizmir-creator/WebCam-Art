from PIL import Image, ImageDraw, ImageFilter
import math
import random

WIDTH = 1400
HEIGHT = 1000

data = {
    "hue": 60,
    "saturation": 1.79,
    "lightness": 43.92,
    "luminosity": 44.60,
    "brightness": 44.18,
    "colors": 144354,
    "resolution": (1280, 720),
    "bitrate": 7.7,
    "fps": 15,
    "quality": 238,
    "png_size": 1.36,
    "jpeg_size": 516.46,
}

hue = data["hue"]
sat = data["saturation"]
light = data["lightness"]
colors_count = data["colors"]
bitrate = data["bitrate"]
fps = data["fps"]
quality = data["quality"]

import colorsys

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
    return (int(r * 255), int(g * 255), int(b * 255))

base_hue = hue
base_sat = max(sat, 15)
base_val = light

c1 = hsv_to_rgb(base_hue, base_sat + 40, base_val + 20)
c2 = hsv_to_rgb((base_hue + 30) % 360, base_sat + 25, base_val + 10)
c3 = hsv_to_rgb((base_hue - 40) % 360, base_sat + 35, base_val + 15)
c4 = hsv_to_rgb((base_hue + 180) % 360, base_sat + 45, base_val + 5)

img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
draw = ImageDraw.Draw(img, 'RGBA')

for y in range(HEIGHT):
    ratio = y / HEIGHT
    r = int(c1[0] * (1 - ratio) + c4[0] * ratio) // 4
    g = int(c1[1] * (1 - ratio) + c4[1] * ratio) // 4
    b = int(c1[2] * (1 - ratio) + c4[2] * ratio) // 4
    for x in range(WIDTH):
        img.putpixel((x, y), (r, g, b))

cx = WIDTH // 2
cy = HEIGHT // 2
max_radius = min(WIDTH, HEIGHT) // 2 - 60

rings = int(10 + quality / 30)
for i in range(rings):
    t = i / rings
    radius = max_radius * (1 - t * 0.9)
    r_ch = int(c1[0] * (1 - t) + c3[0] * t)
    g_ch = int(c1[1] * (1 - t) + c3[1] * t)
    b_ch = int(c1[2] * (1 - t) + c3[2] * t)
    width = max(2, int(bitrate * (1 - t) * 1.5))
    alpha = int(200 * (1 - t * 0.5))
    offset = int(math.sin(t * 6.28) * 15)
    draw.ellipse(
        [cx - radius + offset, cy - radius + offset,
         cx + radius + offset, cy + radius + offset],
        outline=(r_ch, g_ch, b_ch, alpha),
        width=width
    )

rays = int(8 + fps * 1.2)
for i in range(rays):
    angle = (i / rays) * 2 * math.pi
    inner = max_radius * 0.4
    outer = max_radius * (1.1 + math.sin(i) * 0.15)
    x1 = cx + math.cos(angle) * inner
    y1 = cy + math.sin(angle) * inner
    x2 = cx + math.cos(angle) * outer
    y2 = cy + math.sin(angle) * outer
    cc = hsv_to_rgb((base_hue + i * 15) % 360, base_sat + 50, base_val + 25)
    draw.line([(x1, y1), (x2, y2)], fill=(*cc, 180), width=int(bitrate / 2) + 1)

random.seed(int(colors_count))
particle_count = int(colors_count / 150)
for _ in range(particle_count):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0, max_radius * 1.15)
    px = cx + math.cos(angle) * dist
    py = cy + math.sin(angle) * dist

    if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
        continue

    size = random.uniform(1, 4)
    cc = hsv_to_rgb(
        (base_hue + random.uniform(-60, 60)) % 360,
        base_sat + random.uniform(0, 40),
        base_val + random.uniform(0, 30)
    )
    alpha = random.randint(60, 220)
    draw.ellipse(
        [px - size, py - size, px + size, py + size],
        fill=(*cc, alpha)
    )

wave_lines = int(light / 3)
for w in range(wave_lines):
    points = []
    amplitude = (100 - light) * 2 + 20
    freq = 0.008 + w * 0.001
    phase = w * 0.7
    for x in range(0, WIDTH, 4):
        y = cy + math.sin(x * freq + phase) * amplitude * (1 - w / wave_lines)
        points.append((x, y))
    cc = hsv_to_rgb((base_hue + w * 8) % 360, base_sat + 30, base_val + 20)
    alpha = int(120 * (1 - w / wave_lines))
    if len(points) > 1:
        draw.line(points, fill=(*cc, alpha), width=2)

core_r = int(max_radius * 0.25 * (quality / 250))
for i in range(5, 0, -1):
    r = core_r * i / 5
    cc = hsv_to_rgb((base_hue + i * 10) % 360, base_sat + 60, base_val + 30)
    alpha = int(100 / i)
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        fill=(*cc, alpha)
    )

img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

draw2 = ImageDraw.Draw(img, 'RGBA')

for i in range(6):
    r = core_r * (i + 1) / 6
    cc = hsv_to_rgb((base_hue + 20 + i * 5) % 360, 90, 95)
    draw2.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(*cc, 200),
        width=2
    )

resolution_ratio = data["resolution"][0] / data["resolution"][1]
box_w = int(max_radius * 1.8)
box_h = int(box_w / resolution_ratio)
box_x = cx - box_w // 2
box_y = cy - box_h // 2
draw2.rectangle(
    [box_x, box_y, box_x + box_w, box_y + box_h],
    outline=(255, 255, 255, 80),
    width=1
)

img.save("webcam_art.png", "PNG")
print("✅ Kaydedildi: webcam_art.png")