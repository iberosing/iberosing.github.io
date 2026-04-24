from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont

root = Path('.')
img = Image.open(root / 'assets' / 'banner_new.png').convert('RGB')
W, H = img.size
half = W // 2
out_size = (2400, 800)

font_c_bold = ['/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
font_c_reg = ['/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']

bold_p = next((p for p in font_c_bold if Path(p).exists()), None)
reg_p = next((p for p in font_c_reg if Path(p).exists()), bold_p)

def font(p, s):
    return ImageFont.truetype(p, s) if p else ImageFont.load_default()

def fit(draw, text, max_w, p):
    s = 20
    while True:
        f = font(p, s)
        w = draw.textlength(text, font=f)
        if w > max_w:
            return font(p, s-2), s-2
        s += 4

for cfg in [
    {'name': 'banner_zaragoza.png', 'side': 'left', 'city': 'ZARAGOZA', 'date': 'June 29 – July 3, 2026', 'box': (0,0,half,H)},
    {'name': 'banner_andorra.png', 'side': 'right', 'city': 'ANDORRA', 'date': 'July 6 – 8, 2026', 'box': (half,0,W,H)}
]:
    side = cfg['side']
    part = img.crop(cfg['box'])
    
    bg = ImageOps.fit(part, out_size, method=Image.Resampling.LANCZOS, centering=(0.5,0.5))
    bg = bg.filter(ImageFilter.GaussianBlur(35))
    bg = ImageEnhance.Color(bg).enhance(1.1)
    bg = ImageEnhance.Brightness(bg).enhance(0.4) 
    
    canvas = bg.convert('RGBA')

    panel_size = 720
    panel = part.resize((panel_size, panel_size), Image.Resampling.LANCZOS)
    panel_rgba = ImageEnhance.Sharpness(panel).enhance(1.2).convert('RGBA')

    m = Image.new('L', (panel_size, panel_size), 0)
    ImageDraw.Draw(m).rounded_rectangle((0,0,panel_size, panel_size), 40, fill=255)
    framed = Image.new('RGBA', (panel_size, panel_size), (0,0,0,0))
    framed.paste(panel_rgba, (0,0), m)

    shadow = Image.new('RGBA', (panel_size + 100, panel_size + 100), (0,0,0,0))
    ImageDraw.Draw(shadow).rounded_rectangle((30,30,panel_size+30,panel_size+30), 50, fill=(0,0,0,160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))

    img_x = 40 if side == 'left' else out_size[0] - panel_size - 40
    img_y = (out_size[1] - panel_size) // 2
    canvas.alpha_composite(shadow, (img_x - 30, img_y - 20))
    canvas.alpha_composite(framed, (img_x, img_y))

    draw = ImageDraw.Draw(canvas)
    text_w = out_size[0] - panel_size - 160
    tx = img_x + panel_size + 80 if side == 'left' else 80

    p_font, p_s = fit(draw, "Registration for", text_w * 0.5, reg_p)
    c_font, c_s = fit(draw, cfg['city'] + " EVENT", text_w * 0.98, bold_p)
    d_font, d_s = fit(draw, cfg['date'], text_w * 0.7, bold_p)

    ph = draw.textbbox((0,0), "Ay", font=p_font)[3] - draw.textbbox((0,0), "Ay", font=p_font)[1]
    ch = draw.textbbox((0,0), "Ay", font=c_font)[3] - draw.textbbox((0,0), "Ay", font=c_font)[1]
    dh = draw.textbbox((0,0), "Ay", font=d_font)[3] - draw.textbbox((0,0), "Ay", font=d_font)[1]

    while (ph + 15 + ch + 35 + dh) > 740:
        p_s -= 2; c_s -= 3; d_s -= 2
        p_font = font(reg_p, max(10, p_s))
        c_font = font(bold_p, max(10, c_s))
        d_font = font(bold_p, max(10, d_s))
        ph = draw.textbbox((0,0), "Ay", font=p_font)[3] - draw.textbbox((0,0), "Ay", font=p_font)[1]
        ch = draw.textbbox((0,0), "Ay", font=c_font)[3] - draw.textbbox((0,0), "Ay", font=c_font)[1]
        dh = draw.textbbox((0,0), "Ay", font=d_font)[3] - draw.textbbox((0,0), "Ay", font=d_font)[1]

    total_h = ph + 15 + ch + 35 + dh
    ty = (out_size[1] - total_h) // 2

    so = 6
    draw.text((tx+so, ty+so), "Registration for", font=p_font, fill=(0,0,0,180))
    draw.text((tx+so, ty + ph + 15 + so), cfg['city'] + " EVENT", font=c_font, fill=(0,0,0,200))
    draw.text((tx+so, ty + ph + 15 + ch + 35 + so), cfg['date'], font=d_font, fill=(0,0,0,180))

    draw.text((tx, ty), "Registration for", font=p_font, fill=(220, 240, 255, 255))
    draw.text((tx, ty + ph + 15), cfg['city'] + " EVENT", font=c_font, fill=(255, 255, 255, 255))
    draw.text((tx, ty + ph + 15 + ch + 35), cfg['date'], font=d_font, fill=(160, 220, 255, 255))

    out = canvas.convert('RGB')
    out.save(root / 'assets' / cfg['name'], quality=96)
    print(f"saved {cfg['name']} text width: {text_w} | city font: {c_s}")
