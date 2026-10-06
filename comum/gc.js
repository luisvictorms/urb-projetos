// GC = gráficos ao vivo. Liga overlay (vMix), telas e controle remoto de um projeto.
// O estado (o que está no ar) e a lista de tarjas ficam no Supabase, separados por "sala":
// o código da sala funciona como senha. Mudanças chegam na hora via Realtime Broadcast,
// e a cada 15 s todo mundo relê o banco (se o broadcast falhar, no máximo 15 s de atraso).
window.GC = (function () {
  const q = new URLSearchParams(location.search);
  const SALA = (q.get('sala') || '').trim();
  const temSupa = !!window.supabase;
  const sb = temSupa ? window.supabase.createClient(
    'https://oemcxsuqbxhxxzubahzr.supabase.co',
    'sb_publishable_ZMNIN9uK_U4nc7hWkw8_wg_iPTqnksV'
  ) : null;

  const h = { estado: [], tarjas: [], status: [], disparo: [] };
  const emite = (ev, ...a) => h[ev].forEach(fn => { try { fn(...a); } catch (e) { console.error(e); } });

  let estado = {}, tarjas = [], ch = null;

  async function rpc(nome, args) {
    const { data, error } = await sb.rpc(nome, args);
    if (error) throw new Error(error.message);
    return data;
  }

  async function ler() {
    const d = await rpc('gc_ler', { p_sala: SALA });
    if (!d) return;
    const mudouEstado = JSON.stringify(d.estado) !== JSON.stringify(estado);
    const mudouLista = JSON.stringify(d.tarjas) !== JSON.stringify(tarjas);
    estado = d.estado || {};
    tarjas = d.tarjas || [];
    if (mudouEstado) emite('estado', estado, 'banco');
    if (mudouLista) emite('tarjas', tarjas);
  }

  function liga() {
    if (!sb || SALA.length < 6) { setTimeout(() => emite('status', 'SEM_SALA'), 0); return; }
    ch = sb.channel('gc-' + SALA, { config: { broadcast: { self: false } } });
    ch.on('broadcast', { event: 'estado' }, ({ payload }) => {
      estado = payload.estado || estado;
      emite('estado', estado, 'ao-vivo');
    })
      .on('broadcast', { event: 'tarjas' }, () => ler().catch(() => {}))
      .on('broadcast', { event: 'disparo' }, ({ payload }) => emite('disparo', payload))
      .subscribe(st => emite('status', st));
    ler().catch(e => emite('status', 'ERRO: ' + e.message));
    setInterval(() => ler().catch(() => {}), 15000);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) ler().catch(() => {}); });
  }

  const avisa = (event, payload) => ch && ch.send({ type: 'broadcast', event, payload: payload || {} });

  return {
    sala: SALA,
    ativo: () => !!sb && SALA.length >= 6,
    get estado() { return estado; },
    get tarjas() { return tarjas; },
    on(ev, fn) { h[ev].push(fn); },
    iniciar: liga,
    ler,
    // muda só as chaves passadas (merge no banco) e avisa todo mundo
    async mudar(patch) {
      estado = await rpc('gc_estado_set', { p_sala: SALA, p_patch: patch });
      avisa('estado', { estado });
      emite('estado', estado, 'local');
      return estado;
    },
    // gatilho de uma vez só (ex.: inscreva-se) — também grava no estado pra quem perder o broadcast
    async disparar(nome) {
      const t = Date.now();
      const patch = {}; patch[nome] = { t };
      await this.mudar(patch);
      avisa('disparo', { nome, t });
    },
    async salvarTarja(t) {
      const r = await rpc('gc_tarja_salvar', { p_sala: SALA, p_id: t.id || null, p_tipo: t.tipo, p_titulo: t.titulo, p_sub: t.subtitulo });
      await ler(); avisa('tarjas');
      return r;
    },
    async apagarTarja(id) {
      await rpc('gc_tarja_apagar', { p_sala: SALA, p_id: id });
      await ler(); avisa('tarjas');
    },
    async ordenar(ids) {
      await rpc('gc_tarja_ordem', { p_sala: SALA, p_ids: ids });
      await ler(); avisa('tarjas');
    },
  };
})();
