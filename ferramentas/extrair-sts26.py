"""Extrai do PSD do Siará Tech Summit as peças usadas no site (telas por dia com janelas
transparentes + peças das tarjas e do mosquito/inscreva-se)."""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from psd_tools import PSDImage
from PIL import Image, ImageChops

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'saida')
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080


def cola(base, layer, ox=0, oy=0):
    """Cola o pixel salvo da camada (inclui texto/forma rasterizados) na posição dela."""
    try:
        im = layer.topil()
    except Exception as e:
        print('  ! sem pixel', layer.name, e)
        return
    if im is None:
        return
    im = im.convert('RGBA')
    if layer.opacity < 255:
        a = im.getchannel('A').point(lambda v: v * layer.opacity // 255)
        im.putalpha(a)
    x, y = layer.left - ox, layer.top - oy
    tmp = Image.new('RGBA', base.size, (0, 0, 0, 0))
    tmp.paste(im, (x, y))
    base.alpha_composite(tmp)


def compoe(grupo, base, pular=(), ox=0, oy=0, so_visiveis=True):
    for l in grupo:  # de baixo pra cima
        if l.name in pular:
            continue
        if so_visiveis and not l.visible:
            continue
        if l.is_group():
            compoe(l, base, pular, ox, oy)
        else:
            if l.blend_mode and str(l.blend_mode) not in ('BlendMode.NORMAL', 'BlendMode.PASS_THROUGH'):
                print('  ! blend', l.name, l.blend_mode)
            if getattr(l, 'has_effects', lambda: False)() if callable(getattr(l, 'has_effects', None)) else False:
                print('  ! efeitos', l.name)
            cola(base, l, ox, oy)


def furos(base, rects):
    """Zera o alfa onde o retângulo da janela de câmera tem o preenchimento azul (mantém o contorno branco)."""
    m = Image.new('L', base.size, 0)
    for r in rects:
        im = r.topil().convert('RGBA')
        px = im.load()
        mk = Image.new('L', im.size, 0)
        mp = mk.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                cr, cg, cb, ca = px[x, y]
                if ca > 0 and cr < 150:  # azul do preenchimento (o contorno é #f0f0f0)
                    # antialias contra o branco: quanto mais azul, mais furo
                    mp[x, y] = max(0, min(255, int((150 - cr) / (150 - 49) * 255))) * ca // 255
        m.paste(mk, (r.left, r.top), mk)
    a = base.getchannel('A')
    a = ImageChops.subtract(a, m)
    base.putalpha(a)


def acha(grupo, nome):
    for l in grupo:
        if l.name == nome:
            return l
    raise KeyError(nome)


def salva(im, nome):
    p = os.path.join(OUT, nome)
    im.save(p, optimize=True)
    print('  ->', nome, im.size, os.path.getsize(p) // 1024, 'KB')


janelas = {}

# ---------- TELAS ----------
psd = PSDImage.open(os.path.join(AQUI, 'TELA-COMEÇAREMOS-EM-BREVE.psd'))
art = psd[0]
for i, d in enumerate(['DIA 1', 'DIA 2', 'DIA 3'], 1):
    g = acha(art, d)
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    compoe(g, base, so_visiveis=False) if False else None
    # filhos de grupos escondidos continuam com visible=True, então compõe só pelo flag dos filhos
    for l in g:
        if not l.visible:
            continue
        if l.is_group():
            for c in l:
                if c.visible:
                    cola(base, c)
        else:
            cola(base, l)
    salva(base.convert('RGB'), f'tela-comecaremos-dia{i}.png')

psd = PSDImage.open(os.path.join(AQUI, 'TELA-INTERVALO-CAMERAFIXA.psd'))
art = psd[0]
for i in (1, 2, 3):
    g = acha(art, f'INTERVALO-DIA {i}')
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    compoe(g, base)
    r = acha(g, 'Retângulo 2')
    furos(base, [r])
    janelas['intervalo'] = [list(r.bbox)]
    salva(base, f'tela-intervalo-dia{i}.png')

psd = PSDImage.open(os.path.join(AQUI, 'TELA-DIVIDIDA e TARJA TEMA.psd'))
art = psd[0]
for i in (1, 2, 3):
    g = acha(art, f'DIVIDIDA-DIA {i}')
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # tarja tema vira peça dinâmica (overlay); logo-cobertura fica escondido como no DIA 3 do designer
    compoe(g, base, pular=('TARJA-TEMA', 'LOGO-COBERTURA'))
    telas = acha(g, 'TELAS')
    rs = [acha(telas, n) for n in ('Retângulo 2', 'Retângulo 2 copiar', 'Retângulo 2 copiar 2')]
    furos(base, rs)
    janelas['dividida'] = [list(r.bbox) for r in rs]
    salva(base, f'tela-dividida-dia{i}.png')

    if i == 3:
        # peças da tarja tema (sem texto)
        tt = acha(g, 'TARJA-TEMA')
        kids = list(tt)
        fundo, box, seta = kids[0], kids[1], kids[2]
        x0, y0 = fundo.left, fundo.top
        im = Image.new('RGBA', fundo.size, (0, 0, 0, 0)); cola(im, fundo, x0, y0); salva(im, 'tema-fundo.png')
        bx, by = box.left, box.top
        im = Image.new('RGBA', box.size, (0, 0, 0, 0))
        for k in kids[1:]:
            if k is seta or k.kind == 'type':
                continue
            if k.is_group():
                for c in k:
                    cola(im, c, bx, by)
            else:
                cola(im, k, bx, by)
        salva(im, 'tema-box.png')
        im = Image.new('RGBA', seta.size, (0, 0, 0, 0)); cola(im, seta, seta.left, seta.top); salva(im, 'tema-seta.png')
        janelas['tema'] = {'fundo': list(fundo.bbox), 'box': list(box.bbox), 'seta': list(seta.bbox),
                           'titulo': list(kids[-2].bbox), 'sub': list(kids[-1].bbox)}
        # mosquito AO VIVO do layout dividido (tamanho de referência)
        av = acha(g, 'AO VIVO')
        janelas['aovivo'] = {c.name: list(c.bbox) for c in av}

# ---------- TARJA NOME ----------
psd = PSDImage.open(os.path.join(AQUI, 'TARJA NOME.psd'))
nomes = {'bg azul': 'nome-fundo.png', 'box': 'nome-box.png', 'logo': 'nome-logo.png', 'Layer 1': 'nome-seta.png'}
geo = {}
for l in psd:
    geo[l.name] = list(l.bbox)
    if l.name in nomes:
        salva(l.topil().convert('RGBA'), nomes[l.name])
janelas['nome'] = geo

# ---------- MOSQUITO / INSCREVA-SE ----------
psd = PSDImage.open(os.path.join(AQUI, 'MOSQUITO-INSCREVA-SE.psd'))
g1 = acha(psd[0], '01')
k = list(g1)
selo = Image.new('RGBA', k[0].size, (0, 0, 0, 0))
cola(selo, k[0], k[0].left, k[0].top); cola(selo, k[1], k[0].left, k[0].top)
salva(selo, 'selo.png')
for l in g1:
    if l.name in ('gostar', 'clique'):
        salva(l.topil().convert('RGBA'), f'ico-{l.name}.png')
g2 = acha(psd[0], '02')
for l in g2:
    if l.name == 'sinos':
        salva(l.topil().convert('RGBA'), 'ico-sino.png')
janelas['mosquito'] = {f'{g.name}/{l.name}': list(l.bbox) for g in psd[0] for l in g}

with open(os.path.join(OUT, 'geometria.json'), 'w', encoding='utf-8') as f:
    json.dump(janelas, f, ensure_ascii=False, indent=1)
print(json.dumps(janelas, ensure_ascii=False))
