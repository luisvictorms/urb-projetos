# urb/projetos

Catálogo de programas e eventos da **urb.NEWS** e do **FUTEBORA**, com os formatos base e as peças de vMix de cada projeto.

Site: https://luisvictorms.github.io/urb-projetos/

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html` + `projetos.js` | Catálogo. Para cadastrar um projeto novo, adicione um bloco em `projetos.js`. |
| `comum/gc.js` | "Gráficos ao vivo": liga overlay, telas e controle remoto via Supabase (estado + lista de tarjas por sala). |
| `comum/site.css` | Estilo das páginas do catálogo. |
| `sts26/` | Siará Tech Summit ‘26 (urb.NEWS). |
| `ferramentas/` | Scripts que geram as peças a partir dos PSDs. |

## Siará Tech Summit ‘26 (`sts26/`)

- `index.html`: página do projeto (links do vMix, telas, peças, identidade).
- `controle.html?sala=…`: controle remoto do operador. Com `&modo=redacao`, fica só a lista de tarjas, para o jornalista.
- `overlay.html?sala=…`: overlay transparente 1920×1080 para o Web Browser input do vMix. `&so=mosquito,inscreva,nome,tema` filtra as peças, `&demo=1` roda uma demonstração e `&fundo=1` mostra o xadrez de prévia.
- `tela.html?t=comecaremos|intervalo|dividida&sala=…`: telas cheias que seguem o dia escolhido no controle (`&dia=N` fixa o dia).

O código da sala funciona como senha e **não fica no repositório** (`.sala-local`). A sala de ensaio é `sts26-ensaio`.

### Banco (Supabase `urbnews-apuracao`)

As tabelas `gc_estado` e `gc_tarja` têm RLS sem policies, então o acesso é só pelas funções `gc_ler`, `gc_estado_set`, `gc_tarja_salvar`, `gc_tarja_apagar` e `gc_tarja_ordem`. A sincronização em tempo real usa o Realtime Broadcast no canal `gc-<sala>`, e cada tela relê o banco a cada 15 s.

O projeto do Supabase é gratuito e **pausa quando fica parado**. Confira se ele está ativo antes do evento.

### Regerar as peças a partir dos PSDs

```
python ferramentas/extrair-sts26.py sts26/img
```

O script lê os PSDs da pasta onde está (copie os PSDs de `LAYSA/2026/PEÇAS LIVE - SIARÁ TECH SUMMIT` no Drive para junto dele).
