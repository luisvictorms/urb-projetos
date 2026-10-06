"""Grava em MP4 uma página animada do site, quadro a quadro (tempo exato, sem travadas).

uso: python ferramentas/exportar-video.py <url> <saida.mp4> [segundos=15] [fps=30]
     python ferramentas/exportar-video.py <url> <folha.png> --folha 0.5,1,2,7,14,14.6

A página precisa definir window.pronto = true quando as animações estiverem montadas.
Cada quadro: pausa todas as animações (document.getAnimations) no instante t e tira um print.
Usa o Edge instalado (playwright, channel msedge) e o ffmpeg do PATH.
"""
import sys, subprocess
from playwright.sync_api import sync_playwright

url, saida = sys.argv[1], sys.argv[2]
folha = '--folha' in sys.argv
args = [a for a in sys.argv[3:] if a != '--folha']
SEG = float(args[0]) if args and not folha else 15
FPS = int(args[1]) if len(args) > 1 and not folha else 30

SEEK = """t => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; } }"""

with sync_playwright() as p:
    nav = p.chromium.launch(channel='msedge')
    pg = nav.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    pg.goto(url, wait_until='networkidle')
    pg.wait_for_function('window.pronto === true', timeout=30000)
    pg.evaluate('document.fonts.ready')
    if folha:
        from PIL import Image
        import io
        ts = [float(x) for x in args[0].split(',')]
        ims = []
        for t in ts:
            pg.evaluate(SEEK, t * 1000)
            pg.wait_for_timeout(60)
            ims.append(Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((640, 360)))
        cols = 3
        linhas = (len(ims) + cols - 1) // cols
        out = Image.new('RGB', (cols * 650, linhas * 370), (40, 40, 40))
        for i, im in enumerate(ims):
            out.paste(im, ((i % cols) * 650, (i // cols) * 370))
        out.save(saida)
        print('folha', saida, ts)
    else:
        n = round(SEG * FPS)
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                               '-movflags', '+faststart', saida], stdin=subprocess.PIPE)
        for f in range(n):
            pg.evaluate(SEEK, f * 1000 / FPS)
            ff.stdin.write(pg.screenshot(type='png'))
            if f % 90 == 0:
                print(f'{f}/{n}', flush=True)
        ff.stdin.close()
        ff.wait()
        print('ok', saida, n, 'quadros')
    nav.close()
