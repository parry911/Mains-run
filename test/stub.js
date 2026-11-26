/* A stand-in for the artifact runtime's window.claude, for local tests only.
   Seeded from window.__SEED = {"plan/state": {...}, "logs/2026-11-25": {...}, ...}.
   Every write is recorded in window.__T.writes; window.__T.ext(path, data) plays an outside
   writer (the nightly coach) changing a record while the page is open. */
(() => {
  const clone = v => v === undefined ? undefined : JSON.parse(JSON.stringify(v));
  const store = new Map(Object.entries(window.__SEED || {}).map(([k, v]) => [k, clone(v)]));
  const T = window.__T = { writes: [], mcp: [], prompts: [], store, sampleReplies: [], failNext: null };
  const docSubs = new Map(), colSubs = new Map();
  const later = f => setTimeout(f, 5);
  const snapDoc = path => { const v = store.get(path); return { id: path.split("/").pop(), exists: v !== undefined, data: () => clone(v), metadata: { fromCache: false } }; };
  const snapCol = name => ({ docs: [...store.keys()].filter(k => k.split("/").length === 2 && k.startsWith(name + "/")).sort()
      .map(k => ({ id: k.split("/")[1], data: () => clone(store.get(k)) })), metadata: { fromCache: false } });
  const notify = path => {
    (docSubs.get(path) || []).forEach(cb => later(() => cb(snapDoc(path))));
    const col = path.split("/")[0]; (colSubs.get(col) || []).forEach(cb => later(() => cb(snapCol(col))));
  };
  const write = (kind, path, data) => {
    if (T.failNext) { const e = T.failNext; T.failNext = null; return Promise.reject(e); }
    T.writes.push({ kind, path, data: clone(data), at: Date.now() });
    if (kind === "set") store.set(path, clone(data));
    else if (kind === "update") {
      if (!store.has(path)) return Promise.reject({ code: "not_found" });
      const o = Object.assign({}, store.get(path), clone(data)); store.set(path, o);
    } else if (kind === "delete") store.delete(path);
    notify(path); return Promise.resolve();
  };
  T.ext = (path, data, merge) => { store.set(path, merge ? Object.assign({}, store.get(path), clone(data)) : clone(data)); notify(path); };
  /* the same, but this page never hears about it: a phone that missed the update */
  T.extSilent = (path, data, merge) => { store.set(path, merge ? Object.assign({}, store.get(path), clone(data)) : clone(data)); };
  const doc = path => ({
    id: path.split("/").pop(), path,
    get: () => Promise.resolve(snapDoc(path)),
    set: d => write("set", path, d),
    update: d => write("update", path, d),
    delete: () => write("delete", path),
    onSnapshot: (cb, err) => { const a = docSubs.get(path) || []; a.push(cb); docSubs.set(path, a); later(() => cb(snapDoc(path)));
      return () => docSubs.set(path, (docSubs.get(path) || []).filter(x => x !== cb)); }
  });
  const collection = name => ({
    doc: id => doc(name + "/" + id),
    get: () => Promise.resolve(snapCol(name)),
    onSnapshot: (cb, err) => { const a = colSubs.get(name) || []; a.push(cb); colSubs.set(name, a); later(() => cb(snapCol(name)));
      return () => colSubs.set(name, (colSubs.get(name) || []).filter(x => x !== cb)); }
  });
  const db = Object.freeze({ doc, collection });
  const user = Object.freeze({ isOwner: async () => window.__OWNER !== false, id: async () => "perry", name: async () => "Perry" });
  /* chats: sample(messages, {tools, onText}) plays T.chatReplies in order; a reply may carry tool calls,
     which run through the page's own tool code before the text comes back */
  T.chatReplies = []; T.chats = []; T.toolResults = [];
  const sampleFn = async (msgs, opts) => { T.chats.push({ msgs: clone(msgs), tools: (opts && opts.tools || []).map(t => t.name) });
      const r = T.chatReplies.shift(); if (r === undefined) throw { code: "no_reply_queued" };
      for (const c of (r.tools || [])) { const t = (opts.tools || []).find(x => x.name === c.name);
        if (!t) { T.toolResults.push({ name: c.name, error: "not offered" }); continue; }
        try { T.toolResults.push({ name: c.name, result: clone(await t.execute(c.input)) }) } catch (e) { T.toolResults.push({ name: c.name, error: String(e && (e.message || e.code) || e) }) } }
      if (opts && opts.onText) opts.onText({ text: r.text || "" });
      return { text: r.text || "" }; };
  sampleFn.json = async (prompt, opts) => { T.prompts.push(prompt);
      const r = T.sampleReplies.shift(); if (r === undefined) throw { code: "no_reply_queued" };
      return typeof r === "function" ? r(prompt) : clone(r); };
  const sample = Object.freeze(sampleFn);
  let evN = 0;
  const mcp = Object.freeze({ callTool: async (server, tool, args) => { T.mcp.push({ server, tool, args: clone(args) });
      return { payload: { id: tool === "create_event" ? "ev" + (++evN) : args.eventId } }; } });
  const caps = { db, user, sample, mcp, dictation: null };
  window.claude = Object.freeze({ use: name => new Promise(res => setTimeout(() => res(caps[name] === undefined ? null : caps[name]), 20)) });
})();
