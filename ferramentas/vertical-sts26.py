"""Moldura vertical 1080×1920 (Instagram) do Siará Tech Summit, uma por dia, com janela 16:9 vazada
para a live do YouTube. Monta com as camadas soltas do PSD (sts26/img/anim, geradas por extrair-sts26.py).

uso: python ferramentas/vertical-sts26.py      → sts26/img/tela-vertical-dia{1,2,3}.png
"""
import os
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, 'sts26', 'img')
A = os.path.join(IMG, 'anim')
W, H = 1080, 1920
# janela da live (16:9) — cantos arredondados só em cima-esquerda e embaixo-direita, como nas telas da arte
JX, JY, JW, JH, RAIO, TRACO = 40, 660, 1000, 563, 44, 4

camada = lambda n: Image.open(os.path.join(A, n + '.png')).convert('RGBA')


def fundo(d):
    # fundo do PSD no quadro 1920×1080 e transposto (x↔y): mantém as cores nos mesmos cantos
    bg = camada(f'bg-dia{d}')
    q = Image.new('RGBA', (1920, 1080))
    q.paste(bg, (-168, -95) if d == 3 else (0, 0))
    return q.transpose(Image.Transpose.TRANSPOSE)


def cola(base, im, x, y):
    t = Image.new('RGBA', base.size)
    t.paste(im, (x, y))
    base.alpha_composite(t)


for d in (1, 2, 3):
    b = fundo(d)
    cola(b, camada('setas-topo'), W - 220, -300)
    cola(b, camada('seta-menor'), 50, 80)
    logo = camada('logo')                                   # 793×310
    cola(b, logo, (W - logo.width) // 2 - 20, 250)
    # janela: contorno branco + miolo transparente
    dr = ImageDraw.Draw(b)
    cantos = (True, False, True, False)                     # tl, tr, br, bl
    dr.rounded_rectangle((JX - TRACO, JY - TRACO, JX + JW + TRACO - 1, JY + JH + TRACO - 1), RAIO + TRACO, fill=(240, 240, 240, 255), corners=cantos)
    furo = Image.new('L', (W, H), 0)
    ImageDraw.Draw(furo).rounded_rectangle((JX, JY, JX + JW - 1, JY + JH - 1), RAIO, fill=255, corners=cantos)
    a = b.getchannel('A')
    a.paste(0, mask=furo)
    b.putalpha(a)
    # coluna de texto embaixo, alinhada à direita como na tela horizontal
    dir_ = W - 60
    caixa, dia, txt = camada(f'caixa-dia{d}'), camada(f'dia{d}'), camada('txt-cobertura')
    yc = JY + JH + 70
    cola(b, caixa, dir_ - caixa.width, yc)
    cola(b, dia, dir_ - caixa.width + 40, yc + 22)
    cola(b, txt, dir_ - txt.width, yc + 103)
    cola(b, camada('seta-maior'), 70, yc + 20)
    cola(b, camada('setas-base'), 40, H - 330)
    b.save(os.path.join(IMG, f'tela-vertical-dia{d}.png'), optimize=True)
    print('ok', d)
print('janela da live:', JX, JY, JW, JH)
