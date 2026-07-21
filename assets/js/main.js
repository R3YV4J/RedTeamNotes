/**
 * REDTEAMNOTES - Main JavaScript
 * Search · Log excerpt animation · TOC · Reading progress · Cookies
 */

'use strict';

/* ============================================
   POSTS INDEX (populated by build script)
   ============================================ */
window.POSTS_INDEX = window.POSTS_INDEX || [];

/* ============================================
   LOG EXCERPT ANIMATION (hero)
   ============================================ */
function initTerminal() {
  const terminal = document.getElementById('hero-terminal');
  if (!terminal) return;

  const lines = [
    { type: 'cmd', prompt: '$', cmd: 'nmap -sV -sC -p- -T4 192.168.1.1' },
    { type: 'out', text: 'PORT     STATE SERVICE   VERSION' },
    { type: 'out', text: '22/tcp   open  ssh       OpenSSH 8.9p1' },
    { type: 'out', text: '8443/tcp open  https     nginx 1.24.0' },
    { type: 'warn', text: 'nota: faltaba este puerto en el primer escaneo sin -p-' },
    { type: 'cmd', prompt: '$', cmd: 'searchsploit nginx 1.24' },
    { type: 'success', text: 'CVE-2024-7811 — path traversal, ver advisory antes de nada' },
  ];

  let lineIndex = 0;
  let charIndex = 0;
  let currentEl = null;

  function nextLine() {
    if (lineIndex >= lines.length) return;
    const line = lines[lineIndex];

    const row = document.createElement('div');
    row.className = 'terminal-line';

    if (line.type === 'cmd') {
      if (line.prompt) {
        const promptEl = document.createElement('span');
        promptEl.className = 't-prompt';
        promptEl.textContent = line.prompt + ' ';
        row.appendChild(promptEl);
      }
      currentEl = document.createElement('span');
      currentEl.className = 't-cmd';
      row.appendChild(currentEl);
      terminal.appendChild(row);
      typeChar(line.cmd);
    } else {
      const textEl = document.createElement('span');
      textEl.className = line.type === 'success' ? 't-success' :
                         line.type === 'warn' ? 't-warn' :
                         line.type === 'error' ? 't-error' : 't-output';
      textEl.textContent = line.text;
      row.appendChild(textEl);
      terminal.appendChild(row);
      lineIndex++;
      setTimeout(nextLine, 180);
    }
    terminal.scrollTop = terminal.scrollHeight;
  }

  function typeChar(text) {
    if (charIndex < text.length) {
      currentEl.textContent += text[charIndex];
      charIndex++;
      setTimeout(() => typeChar(text), 40 + Math.random() * 30);
    } else {
      charIndex = 0;
      lineIndex++;
      setTimeout(nextLine, 220);
    }
  }

  setTimeout(nextLine, 600);
}

/* ============================================
   SEARCH
   ============================================ */
function initSearch() {
  const overlay = document.getElementById('search-overlay');
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const openBtns = document.querySelectorAll('[data-search-open]');
  const closeBtn = document.getElementById('search-close');

  if (!overlay) return;

  function openSearch() {
    overlay.classList.add('active');
    input.focus();
    document.body.style.overflow = 'hidden';
  }

  function closeSearch() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    input.value = '';
    results.innerHTML = '';
  }

  openBtns.forEach(btn => btn.addEventListener('click', openSearch));
  closeBtn?.addEventListener('click', closeSearch);

  overlay.addEventListener('click', e => {
    if (e.target === overlay) closeSearch();
  });

  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }
    if (e.key === 'Escape') closeSearch();
  });

  input?.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q || q.length < 2) { results.innerHTML = ''; return; }

    const posts = window.POSTS_INDEX;
    const filtered = posts.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.excerpt?.toLowerCase().includes(q) ||
      p.tags?.some(t => t.toLowerCase().includes(q)) ||
      p.category?.toLowerCase().includes(q)
    ).slice(0, 8);

    if (!filtered.length) {
      results.innerHTML = `<li style="text-align:center;padding:1.5rem;color:var(--text-muted);font-family:var(--font-mono);font-size:0.85rem;">
        Sin resultados para "<strong style="color:var(--text-primary)">${q}</strong>"</li>`;
      return;
    }

    results.innerHTML = filtered.map(p => `
      <li class="search-result-item" onclick="location.href='${p.url}'">
        <div class="search-result-title">${highlight(p.title, q)}</div>
        <div class="search-result-meta">
          <span class="card-category cat-${p.category?.toLowerCase().replace(/\s/g,'-')}">${p.category || ''}</span>
          &nbsp;·&nbsp; ${p.date || ''} &nbsp;·&nbsp; ${p.readTime || ''}
        </div>
      </li>
    `).join('');
  });

  function highlight(text, q) {
    const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
    return text.replace(re, '<mark style="background:var(--accent-glow);color:var(--accent);border-radius:2px">$1</mark>');
  }
}

/* ============================================
   READING PROGRESS BAR
   ============================================ */
function initReadingProgress() {
  const bar = document.getElementById('reading-progress');
  if (!bar) return;

  const article = document.querySelector('.article-content');
  if (!article) return;

  function update() {
    const rect = article.getBoundingClientRect();
    const top = window.scrollY + rect.top;
    const h = rect.height - window.innerHeight;
    const progress = Math.min(Math.max((window.scrollY - top) / h, 0), 1);
    bar.style.width = (progress * 100) + '%';
  }

  window.addEventListener('scroll', update, { passive: true });
  update();
}

/* ============================================
   TABLE OF CONTENTS
   ============================================ */
function initTOC() {
  // El HTML del índice (toc-list y toc-sidebar) ya viene generado por
  // scripts/build.py a partir de los H2/H3 del artículo. Esta función
  // SOLO añade el resaltado de la sección activa al hacer scroll —
  // nunca debe crear elementos <li> nuevos, o se duplica el índice.
  const content = document.querySelector('.article-content');
  if (!content) return;

  const headings = content.querySelectorAll('h2, h3');
  if (!headings.length) return;

  // Vincula cada heading con su(s) enlace(s) ya existentes en el TOC
  // (puede haber dos: el bloque superior y el de la sidebar)
  const items = [];
  headings.forEach(h => {
    if (!h.id) return;
    const links = document.querySelectorAll(`.toc-list a[href="#${h.id}"]`);
    if (links.length) items.push({ el: h, links });
  });

  if (!items.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        items.forEach(it => it.links.forEach(link => link.classList.remove('active')));
        const item = items.find(it => it.el === entry.target);
        if (item) item.links.forEach(link => link.classList.add('active'));
      }
    });
  }, { rootMargin: '-80px 0px -60% 0px' });

  items.forEach(it => observer.observe(it.el));
}

/* ============================================
   SCROLL TO TOP
   ============================================ */
function initScrollTop() {
  const btn = document.getElementById('scroll-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ============================================
   MOBILE MENU
   ============================================ */
function initMobileMenu() {
  const btn = document.getElementById('mobile-menu-btn');
  const nav = document.getElementById('nav-links');
  if (!btn || !nav) return;

  btn.addEventListener('click', () => {
    nav.classList.toggle('mobile-open');
    btn.textContent = nav.classList.contains('mobile-open') ? '✕' : '☰';
  });
}

/* ============================================
   COOKIE BANNER
   ============================================ */
function initCookieBanner() {
  const banner = document.getElementById('cookie-banner');
  if (!banner) return;

  const accepted = localStorage.getItem('cookies-accepted');
  if (!accepted) {
    banner.classList.add('visible');
  }

  document.getElementById('cookie-accept')?.addEventListener('click', () => {
    localStorage.setItem('cookies-accepted', '1');
    banner.classList.remove('visible');
  });

  document.getElementById('cookie-reject')?.addEventListener('click', () => {
    localStorage.setItem('cookies-accepted', '0');
    banner.classList.remove('visible');
  });
}

/* ============================================
   ESTIMATED READ TIME (for article pages)
   ============================================ */
function calcReadTime() {
  const content = document.querySelector('.article-content');
  const el = document.getElementById('read-time');
  if (!content || !el) return;

  const words = content.textContent.trim().split(/\s+/).length;
  const mins = Math.max(1, Math.ceil(words / 200));
  el.textContent = `${mins} min de lectura`;
}

/* ============================================
   SMOOTH ANCHOR LINKS
   ============================================ */
function initAnchorLinks() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/* ============================================
   COPY CODE BLOCKS
   ============================================ */
function initCodeCopy() {
  document.querySelectorAll('pre').forEach(pre => {
    const btn = document.createElement('button');
    btn.textContent = 'copiar';
    btn.style.cssText = `
      position:absolute;top:0.6rem;right:0.6rem;
      background:var(--bg-surface);border:1px solid var(--border);
      color:var(--text-muted);font-family:var(--font-mono);
      font-size:0.68rem;padding:0.2rem 0.5rem;border-radius:4px;
      cursor:pointer;transition:all 0.2s;
    `;
    pre.style.position = 'relative';
    pre.appendChild(btn);

    btn.addEventListener('click', () => {
      navigator.clipboard.writeText(pre.querySelector('code')?.textContent || pre.textContent);
      btn.textContent = '✓ copiado';
      btn.style.color = 'var(--accent)';
      setTimeout(() => {
        btn.textContent = 'copiar';
        btn.style.color = 'var(--text-muted)';
      }, 2000);
    });
  });
}

/* ============================================
   INIT ALL
   ============================================ */
document.addEventListener('DOMContentLoaded', () => {
  initTerminal();
  initSearch();
  initReadingProgress();
  initTOC();
  initScrollTop();
  initMobileMenu();
  initCookieBanner();
  calcReadTime();
  initAnchorLinks();
  initCodeCopy();

  // Mark active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') && path.includes(a.getAttribute('href').replace(/^\//, ''))) {
      a.classList.add('active');
    }
  });
});
