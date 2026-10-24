(() => {
  const STORE = "ai-engineer-progress-v1";
  const THEME = "ai-engineer-theme";
  const REPO = "https://github.com/Hemanth9336/AI-Engineer";
  const TYPE = {
    lesson: { icon: "📘", label: "Lesson" },
    task: { icon: "🛠️", label: "Task" },
    quiz: { icon: "❓", label: "Quiz" },
    scenario: { icon: "🎭", label: "Scenario" },
    challenge: { icon: "🏆", label: "Challenge" },
  };
  const app = document.getElementById("app");
  const cache = new Map();
  let data = null;
  let done = load();

  function load() { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch { return {}; } }
  function save() { localStorage.setItem(STORE, JSON.stringify(done)); renderTopProgress(); }
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pad = (n) => String(n).padStart(2, "0");
  const skillById = (id) => data.skills.find((s) => s.id === id);
  const itemsOf = (sk) => sk.steps.flatMap((st) => st.items.map((it, i) => ({ ...it, step: st, idx: i + 1, skill: sk })));
  const allItems = () => data.skills.flatMap(itemsOf);
  const stepDone = (st) => st.items.filter((it) => done[it.path]).length;
  const isStepDone = (st) => stepDone(st) === st.items.length;
  const currentStep = (sk) => sk.steps.find((st) => !isStepDone(st)) || sk.steps[sk.steps.length - 1];
  const isLocked = (sk, st) => {
    const i = sk.steps.indexOf(st);
    return i > 0 && !isStepDone(sk.steps[i - 1]) && stepDone(st) === 0;
  };

  function toast(msg) {
    let t = document.querySelector(".toast");
    if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2400);
  }

  /* ---------- theme ---------- */
  const setTheme = (t) => {
    document.documentElement.dataset.theme = t; localStorage.setItem(THEME, t);
    if (window.mermaid) mermaid.initialize({ startOnLoad: false, theme: "default", securityLevel: "loose" });
  };
  setTheme(localStorage.getItem(THEME) || "dark");
  document.getElementById("theme").onclick = () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");

  /* ---------- markdown ---------- */
  let mermaidSources = [];
  marked.use({
    gfm: true,
    renderer: {
      code(code, lang) {
        if ((lang || "").trim() === "mermaid") {
          mermaidSources.push(code);
          return `<div class="mermaid" data-m="${mermaidSources.length - 1}"></div>`;
        }
        return false;
      },
    },
  });
  const md = (text) => marked.parse(text);

  async function enhance(root) {
    root.querySelectorAll("pre code").forEach((el) => {
      if (window.hljs) hljs.highlightElement(el);
      const pre = el.parentElement;
      if (pre.querySelector(".copy")) return;
      const b = document.createElement("button");
      b.className = "copy"; b.textContent = "Copy";
      b.onclick = () => { navigator.clipboard.writeText(el.innerText); b.textContent = "Copied ✓"; setTimeout(() => (b.textContent = "Copy"), 1400); };
      pre.appendChild(b);
    });
    const nodes = [...root.querySelectorAll(".mermaid[data-m]")];
    nodes.forEach((n) => { n.textContent = mermaidSources[+n.dataset.m]; n.removeAttribute("data-m"); });
    if (nodes.length && window.mermaid) { try { await mermaid.run({ nodes }); } catch (e) { console.warn("mermaid", e); } }
    root.querySelectorAll(".md a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (/^https?:/.test(href)) { a.target = "_blank"; a.rel = "noopener"; return; }
      if (href.startsWith("#")) return;
      a.href = `${REPO}/blob/main/${href.replace(/^(\.\.\/)+/, "")}`;
      a.target = "_blank"; a.rel = "noopener";
    });
  }

  async function fetchItem(path) {
    if (cache.has(path)) return cache.get(path);
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Could not load ${path}`);
    const text = (await res.text()).replace(/^---\n[\s\S]*?\n---\n/, "");
    cache.set(path, text);
    return text;
  }

  /* ---------- quizzes ---------- */
  function parseQuiz(body) {
    const parts = body.split(/^### Q\d+\.\s*/m);
    const intro = parts.shift();
    const questions = parts.map((block) => {
      const nl = block.indexOf("\n");
      const title = block.slice(0, nl).trim();
      let rest = block.slice(nl + 1);
      const det = rest.match(/<details>\s*<summary>[^<]*<\/summary>([\s\S]*?)<\/details>/);
      const explanation = det ? det[1].trim() : "";
      const after = det ? rest.slice(det.index + det[0].length) : "";
      if (det) rest = rest.slice(0, det.index);
      const opts = [], pre = [];
      for (const line of rest.split("\n")) {
        const m = line.match(/^- ([A-D])\. (.*)$/);
        if (m) opts.push({ letter: m[1], text: m[2] });
        else if (!opts.length) pre.push(line);
      }
      const ans = (explanation.match(/\*\*Answer: ([A-D])\*\*/) || [])[1];
      return { title, pre: pre.join("\n"), opts, ans, explanation: explanation.replace(/^\*\*Answer: [A-D]\*\*\s*[-—–:]?\s*/, ""), after };
    });
    return { intro, questions };
  }

  function renderQuiz(container, body, item) {
    const { intro, questions } = parseQuiz(body);
    let answered = 0, correct = 0;
    let html = md(intro);
    questions.forEach((q, qi) => {
      html += `<div class="q" data-q="${qi}"><div class="qn">Question ${qi + 1} of ${questions.length}</div>
        <h3>${marked.parseInline(q.title)}</h3>${q.pre.trim() ? md(q.pre) : ""}
        <div class="opts">${q.opts.map((o) => `<button class="opt" data-l="${o.letter}"><span class="l">${o.letter}</span><span>${marked.parseInline(o.text)}</span></button>`).join("")}</div>
        <div class="slot"></div></div>${q.after.trim() ? md(q.after) : ""}`;
    });
    html += `<div class="score" hidden><span class="big"></span><span class="txt"></span></div>`;
    container.innerHTML = html;
    container.querySelectorAll(".q").forEach((qel) => {
      const q = questions[+qel.dataset.q];
      qel.querySelectorAll(".opt").forEach((btn) => {
        btn.onclick = () => {
          const ok = btn.dataset.l === q.ans;
          qel.querySelectorAll(".opt").forEach((b) => { b.disabled = true; if (b.dataset.l === q.ans) b.classList.add("right"); });
          if (!ok) btn.classList.add("wrong");
          answered++; if (ok) correct++;
          const slot = qel.querySelector(".slot");
          slot.innerHTML = `<div class="explain ${ok ? "" : "bad"}"><b>${ok ? "✅ Correct" : `❌ Not quite - the answer is ${q.ans}`}</b>${md(q.explanation)}</div>`;
          enhance(slot);
          if (answered === questions.length) {
            const sc = container.querySelector(".score");
            const pass = correct / questions.length >= 0.6;
            sc.hidden = false;
            sc.querySelector(".big").textContent = `${correct}/${questions.length}`;
            sc.querySelector(".txt").textContent = correct === questions.length ? "Perfect score - marked complete!" :
              pass ? "Passed - marked complete. Review the explanations above." : "Not yet - re-read the lessons and reload to try again.";
            if (pass) { setDone(item.path, true); refreshItemChrome(); }
          }
        };
      });
    });
  }

  /* ---------- progress ---------- */
  function setDone(path, v) { if (v) done[path] = Date.now(); else delete done[path]; save(); }
  function renderTopProgress() {
    if (!data) return;
    const items = allItems();
    const n = items.filter((i) => done[i.path]).length;
    document.getElementById("top-progress").innerHTML = `<b>${Math.round((n / items.length) * 100)}%</b> complete`;
  }
  function ring(pct) {
    const r = 22, c = 2 * Math.PI * r;
    return `<svg class="ring" viewBox="0 0 54 54"><circle class="bg" cx="27" cy="27" r="${r}"/>
      <circle class="fg" cx="27" cy="27" r="${r}" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct)}"/>
      <text x="27" y="27">${Math.round(pct * 100)}%</text></svg>`;
  }
  const resumeLink = (sk) => {
    const cur = currentStep(sk);
    const i = cur.items.findIndex((it) => !done[it.path]) + 1 || 1;
    return `#/${sk.id}/${cur.n}/${i}`;
  };

  /* ---------- views ---------- */
  function home() {
    const tot = { topics: 0, tasks: 0, quizzes: 0, challenges: 0, minutes: 0 };
    data.skills.forEach((sk) => Object.keys(tot).forEach((k) => (tot[k] += sk.stats[k] || 0)));
    const first = data.skills[0];
    const started = allItems().some((i) => done[i.path]);
    let html = `<section class="hero">
      <span class="eyebrow">🤖 AI engineering · zero to hero</span>
      <h1>AI <span class="grad">Engineer</span></h1>
      <p class="lead">Work with real LLM APIs from a live machine — raw HTTP, official SDKs, embeddings, vector databases
      and RAG pipelines, graded when you press Submit.</p>
      <div class="stats">
        <div class="stat"><div class="num">${tot.topics}</div><div class="lbl">topics</div></div>
        <div class="stat"><div class="num">${tot.tasks}</div><div class="lbl">hands-on tasks</div></div>
        <div class="stat"><div class="num">${tot.quizzes}</div><div class="lbl">quizzes</div></div>
        ${tot.challenges ? `<div class="stat"><div class="num">${tot.challenges}</div><div class="lbl">challenges</div></div>` : ""}
        <div class="stat"><div class="num">~${Math.round(tot.minutes / 60)}h</div><div class="lbl">guided practice</div></div>
      </div>
      <div class="hero-cta">
        <a class="btn primary" href="${started ? resumeLink(first) : `#/${first.id}`}">${started ? "▶ Continue learning" : `🚀 Start with ${esc(first.name)}`}</a>
        <a class="btn" href="${REPO}/blob/main/setup/README.md" target="_blank" rel="noopener">🧪 Set up a practice machine</a>
      </div>
    </section>
    <div class="wrap">
      <h2 class="section-title">Skills</h2>
      <p class="section-sub">Follow them in order. Each skill is a path of short lessons, real tasks, quizzes, and projects.</p>
      <div class="skills">`;
    data.skills.forEach((sk) => {
      const items = itemsOf(sk), n = items.filter((i) => done[i.path]).length, s = sk.stats;
      html += `<a class="skill" href="#/${sk.id}"><span class="sk-status">Live</span><div class="sk-icon">${sk.icon}</div>
        <h3>${esc(sk.name)}</h3><p>${esc(sk.tagline)}</p>
        <div class="chips"><span class="chip">${s.topics} topics</span><span class="chip">🛠️ ${s.tasks} tasks</span><span class="chip">❓ ${s.quizzes} quizzes</span>${s.challenges ? `<span class="chip">🏆 ${s.challenges}</span>` : ""}<span class="chip">~${s.minutes} min</span></div>
        <div class="bar"><span style="width:${(n / items.length) * 100}%"></span></div></a>`;
    });
    data.coming_soon.forEach((cs) => {
      html += `<div class="skill soon"><span class="sk-status">Coming next</span><div class="sk-icon">${cs.icon}</div>
        <h3>${esc(cs.name)}</h3><p>${esc(cs.tagline)}</p></div>`;
    });
    html += `</div></div>`;
    app.innerHTML = html;
    window.scrollTo(0, 0);
  }

  function skillView(sk) {
    const s = sk.stats, items = itemsOf(sk), n = items.filter((i) => done[i.path]).length;
    const cur = currentStep(sk);
    let html = `<section class="skill-hero"><div class="sk-icon">${sk.icon}</div><h1>${esc(sk.name)}</h1><p class="lead">${esc(sk.tagline)}</p>
      <div class="stats">
        <div class="stat"><div class="num">${s.topics}</div><div class="lbl">topics</div></div>
        <div class="stat"><div class="num">${s.tasks}</div><div class="lbl">hands-on tasks</div></div>
        <div class="stat"><div class="num">${s.quizzes}</div><div class="lbl">quizzes</div></div>
        ${s.challenges ? `<div class="stat"><div class="num">${s.challenges}</div><div class="lbl">challenges</div></div>` : ""}
        <div class="stat"><div class="num">~${s.minutes}</div><div class="lbl">minutes</div></div>
      </div>
      <div class="hero-cta"><a class="btn primary" href="${resumeLink(sk)}">${n ? `▶ Continue: ${pad(cur.n)} ${esc(cur.title)}` : `🚀 Start ${pad(sk.steps[0].n)} ${esc(sk.steps[0].title)}`}</a>
      <a class="btn" href="#/">← All skills</a></div>
      <div class="overall"><div class="bar"><span style="width:${(n / items.length) * 100}%"></span></div>
        <div class="meta"><span>${n} of ${items.length} items complete</span><span>${s.questions} quiz questions</span></div></div>
    </section><div class="wrap">
      <h2 class="section-title">The path</h2>
      <p class="section-sub">Steps unlock as you finish the one before - you can still peek ahead any time.</p>
      <div class="legend">${Object.values(TYPE).map((t) => `<span>${t.icon} ${t.label}</span>`).join("")}<span>✅ done</span><span>▶ you are here</span><span>🔒 up next</span></div>`;
    sk.phases.forEach((p, pi) => {
      const steps = sk.steps.filter((st) => st.phase === p.id);
      const pDone = steps.every(isStepDone);
      html += `<section class="phase ${pDone ? "done" : ""}"><div class="phase-num">${pDone ? "✓" : pi + 1}</div>
        <div class="phase-head"><div><h3>${esc(p.name)}</h3><p>${esc(p.blurb)}</p></div></div><div class="cards">`;
      steps.forEach((st) => {
        const pct = stepDone(st) / st.items.length, here = st === cur && pct < 1, locked = !here && isLocked(sk, st);
        const c = st.counts;
        html += `<a class="card ${pct === 1 ? "done" : ""} ${here ? "current" : ""} ${locked ? "locked" : ""}" href="#/${sk.id}/${st.n}">
          ${here ? '<span class="badge-now">▶ YOU ARE HERE</span>' : locked ? '<span class="lock">🔒</span>' : ""}
          ${ring(pct)}<div class="body"><div class="step-no">${pad(st.n)} · ~${st.minutes} min</div>
          <h4>${esc(st.title)}</h4><p>${esc(st.summary)}</p>
          <div class="chips">${c.lessons ? `<span class="chip">📘 ${c.lessons}</span>` : `<span class="chip">🎓 project</span>`}
          ${c.tasks ? `<span class="chip">🛠️ ${c.tasks}</span>` : ""}${c.quizzes ? `<span class="chip">❓ ${c.quizzes}</span>` : ""}${c.challenges ? `<span class="chip">🏆 ${c.challenges}</span>` : ""}</div></div></a>`;
      });
      html += `</div></section>`;
    });
    app.innerHTML = html + `</div>`;
    window.scrollTo(0, 0);
  }

  function sidebar(sk, st, activeIdx) {
    const d = stepDone(st);
    return `<aside class="sidebar"><a class="back" href="#/${sk.id}">← ${esc(sk.name)} path</a>
      <h3><a href="#/${sk.id}/${st.n}" style="color:inherit">${pad(st.n)} · ${esc(st.title)}</a></h3>
      <div class="meta">~${st.minutes} min · ${d}/${st.items.length} complete</div>
      <div class="bar"><span style="width:${(d / st.items.length) * 100}%"></span></div>
      <ul class="items">${st.items.map((it, i) => `<li><a href="#/${sk.id}/${st.n}/${i + 1}" class="${i + 1 === activeIdx ? "active" : ""} ${done[it.path] ? "done" : ""}">
        <span class="st">${done[it.path] ? "✓" : i + 1}</span><span class="t">${esc(it.title)}<small>${TYPE[it.type].icon} ${TYPE[it.type].label} · ${it.minutes}m</small></span></a></li>`).join("")}</ul></aside>`;
  }

  function stepView(sk, n) {
    const st = sk.steps.find((s) => s.n === n);
    if (!st) return skillView(sk);
    const phase = sk.phases.find((p) => p.id === st.phase);
    const first = st.items.findIndex((it) => !done[it.path]) + 1 || 1;
    const c = st.counts;
    app.innerHTML = `<div class="layout">${sidebar(sk, st, 0)}<div>
      <div class="step-hero"><div class="step-no">${sk.icon} ${esc(sk.name)} · ${pad(st.n)} of ${sk.steps.length} · ${esc(phase.name)}</div>
        <h1>${esc(st.title)}</h1><p>${esc(st.summary)}</p>
        <div class="chips" style="margin-bottom:18px"><span class="chip">⏱ ~${st.minutes} min</span>${c.lessons ? `<span class="chip">📘 ${c.lessons} lessons</span>` : ""}
        ${c.tasks ? `<span class="chip">🛠️ ${c.tasks} tasks</span>` : ""}${c.quizzes ? `<span class="chip">❓ ${c.quizzes} quizzes</span>` : ""}${c.challenges ? `<span class="chip">🏆 ${c.challenges} challenge${c.challenges > 1 ? "s" : ""}</span>` : ""}</div>
        ${isLocked(sk, st) ? `<p style="font-size:14px">🔒 Recommended: finish <a href="#/${sk.id}/${st.n - 1}">step ${pad(st.n - 1)}</a> first. You can still open this step.</p>` : ""}
        <a class="btn primary" href="#/${sk.id}/${st.n}/${first}">${stepDone(st) ? "▶ Continue" : "🚀 Start this step"}</a>
        <a class="btn" href="${REPO}/tree/main/${st.dir}" target="_blank" rel="noopener">📁 Folder on GitHub</a></div>
      <div class="item-list">${st.items.map((it, i) => `<a class="item-row ${done[it.path] ? "done" : ""}" href="#/${sk.id}/${st.n}/${i + 1}">
        <span class="n">${pad(i + 1)}</span><span class="type ${it.type}">${TYPE[it.type].icon} ${TYPE[it.type].label}</span>
        <span class="t">${esc(it.title)}</span><span class="m">${it.minutes}m</span></a>`).join("")}</div></div></div>`;
    window.scrollTo(0, 0);
  }

  let ctx = null;
  function refreshItemChrome() {
    if (!ctx) return;
    const { sk, st, idx } = ctx;
    const it = st.items[idx - 1];
    const el = document.getElementById("complete");
    if (el) {
      const isDone = !!done[it.path];
      el.className = "btn " + (isDone ? "success" : "primary");
      el.textContent = isDone ? "✓ Completed" : it.type === "task" || it.type === "challenge" ? "✅ Submit" : "Mark as complete";
    }
    const side = document.querySelector(".sidebar");
    if (side) side.outerHTML = sidebar(sk, st, idx);
  }

  async function itemView(sk, n, idx) {
    const st = sk.steps.find((s) => s.n === n);
    const it = st && st.items[idx - 1];
    if (!it) return stepView(sk, n);
    ctx = { sk, st, idx };
    const flat = itemsOf(sk);
    const pos = flat.findIndex((f) => f.path === it.path);
    const prev = flat[pos - 1], next = flat[pos + 1];
    const link = (f, label) => (f ? `<a class="btn" href="#/${sk.id}/${f.step.n}/${f.idx}">${label}</a>` : "");
    app.innerHTML = `<div class="layout">${sidebar(sk, st, idx)}<article class="article">
      <div class="article-head"><div class="crumb"><a href="#/">AI Engineer</a> / <a href="#/${sk.id}">${esc(sk.name)}</a> / <a href="#/${sk.id}/${st.n}">${pad(st.n)} · ${esc(st.title)}</a></div>
        <h1>${esc(it.title)}</h1><span class="type ${it.type}">${TYPE[it.type].icon} ${TYPE[it.type].label}</span>
        <span class="chip" style="margin-left:6px">⏱ ${it.minutes} min</span></div>
      <div class="md" id="content"><p class="loading">Loading…</p></div>
      ${it.type === "task" || it.type === "challenge" ? `<div class="checker-note">🧪 Run the <b>Check your work</b> script on your practice machine. When every line shows ✅, press <b>Submit</b>.
        No lab yet? <a href="${REPO}/blob/main/setup/README.md" target="_blank" rel="noopener">Set up the machine and AI gateway</a>.</div>` : ""}
      <div class="article-foot"><button id="complete" class="btn"></button>
        <div class="nav-links">${link(prev, "← Previous")}${link(next, next && next.step.n !== st.n ? `Next: ${pad(next.step.n)} ${esc(next.step.title)} →` : "Next →")}</div></div>
    </article></div>`;
    window.scrollTo(0, 0);
    refreshItemChrome();
    document.getElementById("complete").onclick = () => {
      const v = !done[it.path];
      setDone(it.path, v); refreshItemChrome();
      if (v) toast(isStepDone(st) ? `🎉 ${pad(st.n)} ${st.title} complete!` : `✓ "${it.title}" complete`);
    };
    const content = document.getElementById("content");
    try {
      const body = await fetchItem(it.path);
      mermaidSources = [];
      if (it.type === "quiz" || it.type === "scenario") renderQuiz(content, body, it);
      else content.innerHTML = md(body);
      await enhance(content);
    } catch (e) {
      content.innerHTML = `<p>Could not load this item. <a href="${it.path}">Open the Markdown file</a>.</p>`;
    }
  }

  /* ---------- search ---------- */
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (!q || !data) { results.hidden = true; return; }
    const stepHits = data.skills.flatMap((sk) => sk.steps.filter((s) => (s.title + " " + s.summary).toLowerCase().includes(q))
      .map((s) => `<a href="#/${sk.id}/${s.n}">🗺️ ${pad(s.n)} · ${esc(s.title)}<small>${esc(sk.name)}</small></a>`));
    const itemHits = allItems().filter((i) => i.title.toLowerCase().includes(q)).slice(0, 25)
      .map((i) => `<a href="#/${i.skill.id}/${i.step.n}/${i.idx}">${TYPE[i.type].icon} ${esc(i.title)}<small>${esc(i.skill.name)} ${pad(i.step.n)}</small></a>`);
    const all = [...stepHits, ...itemHits];
    results.innerHTML = all.length ? all.join("") : `<div style="padding:10px;color:var(--muted)">No matches</div>`;
    results.hidden = false;
  });
  results.addEventListener("click", () => { results.hidden = true; input.value = ""; });
  document.addEventListener("click", (e) => { if (!e.target.closest(".search")) results.hidden = true; });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    if (e.key === "Escape") { results.hidden = true; input.blur(); }
  });

  /* ---------- router ---------- */
  function route() {
    ctx = null;
    const m = location.hash.match(/^#\/([a-z0-9-]+)(?:\/(\d+))?(?:\/(\d+))?/);
    const sk = m && skillById(m[1]);
    if (!sk) return home();
    if (m[3]) itemView(sk, +m[2], +m[3]);
    else if (m[2]) stepView(sk, +m[2]);
    else skillView(sk);
  }

  fetch("data/ai-engineer.json").then((r) => r.json()).then((d) => {
    data = d;
    renderTopProgress();
    window.addEventListener("hashchange", route);
    route();
  }).catch(() => { app.innerHTML = `<div class="loading">Could not load data/ai-engineer.json - serve this folder over HTTP (python3 -m http.server).</div>`; });
})();
