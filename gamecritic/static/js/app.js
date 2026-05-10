/* ═══════════════════════════════════════════════
   GameCritic — SPA Frontend
   ═══════════════════════════════════════════════ */

const API = '';

// ── Estado global ────────────────────────────────
let token       = localStorage.getItem('gc_token') || null;
let usuario     = JSON.parse(localStorage.getItem('gc_usuario') || 'null');
let vistaActual = 'juegos';

// ── Al arrancar: verificar que el token sigue vivo ──
async function verificarSesion() {
  if (!token) return;
  // Intentamos un endpoint protegido liviano
  const res = await fetch('/auth/logout', {
    method: 'OPTIONS',   // preflight no consume el token
  });
  // Mejor: intentamos obtener el perfil del usuario guardado
  const check = await fetch(`/usuarios/${usuario?.id_usuario}/perfil`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (check.status === 401) {
    // Token expirado o revocado → limpiar sesión silenciosamente
    token   = null;
    usuario = null;
    localStorage.removeItem('gc_token');
    localStorage.removeItem('gc_usuario');
  }
}

// ── Helpers HTTP ─────────────────────────────────
async function api(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

// ── Toast ─────────────────────────────────────────
function toast(msg, error = false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (error ? ' error' : '');
  clearTimeout(t._to);
  t._to = setTimeout(() => t.classList.remove('show'), 3500);
}

// ── Modales ───────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// ── Sidebar / navegación ──────────────────────────
function activarVista(nombre) {
  vistaActual = nombre;
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(`view-${nombre}`).classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === nombre);
  });
  const titulos = {
    juegos: 'Videojuegos', resenas: 'Reseñas',
    calificaciones: 'Calificaciones', usuarios: 'Usuarios', logs: 'Logs',
  };
  document.getElementById('page-title').textContent = titulos[nombre] || nombre;

  // Botón "Nuevo" solo cuando corresponde
  const btnAdd = document.getElementById('btn-add');
  const showAdd = (nombre === 'juegos' && usuario?.rol === 'admin')
               || (nombre === 'resenas' && usuario);
  btnAdd.style.display = showAdd ? '' : 'none';

  cargarVista(nombre);
}

// ── Auth UI ───────────────────────────────────────
function actualizarAuthUI() {
  const loggedIn = !!usuario;
  document.getElementById('user-info').style.display     = loggedIn ? '' : 'none';
  document.getElementById('btn-show-auth').style.display = loggedIn ? 'none' : '';
  document.getElementById('admin-section').style.display = (usuario?.rol === 'admin') ? '' : 'none';

  if (loggedIn) {
    document.getElementById('user-avatar').textContent = usuario.nombre[0].toUpperCase();
    document.getElementById('user-name-display').textContent = usuario.nombre;
    document.getElementById('user-role-display').textContent = usuario.rol;
  }
}

// ── Carga de vistas ───────────────────────────────
async function cargarVista(nombre) {
  switch (nombre) {
    case 'juegos':        await cargarJuegos(); break;
    case 'resenas':       await cargarResenas(); break;
    case 'calificaciones': await cargarCalificaciones(); break;
    case 'usuarios':      await cargarUsuarios(); break;
    case 'logs':          await cargarLogs(); break;
  }
}

// ── VIDEOJUEGOS ───────────────────────────────────
async function cargarJuegos() {
  const { ok, data } = await api('GET', '/videojuegos');
  const grid = document.getElementById('juegos-grid');
  if (!ok || !data.length) {
    grid.innerHTML = '<div class="empty"><span class="empty-icon">⬡</span>Sin videojuegos todavía.</div>';
    return;
  }
  grid.innerHTML = data.map(j => {
    const imgUrl = j.imagen_url || '';
    return `
    <div class="game-card" onclick="verDetalleJuego(${j.id_juego})">
      ${imgUrl
        ? `<div class="card-cover">
             <img src="${imgUrl}" alt="${esc(j.titulo)}"
                  onerror="this.parentElement.classList.add('card-cover--empty'); this.remove()"/>
           </div>`
        : `<div class="card-cover card-cover--empty"><span>⬡</span></div>`}
      <div class="card-body">
        <span class="card-genre">${esc(j.genero || 'Sin género')}</span>
        <h3 class="card-title">${esc(j.titulo)}</h3>
        <p class="card-desc">${esc(j.descripcion || '–')}</p>
        <div class="card-footer">
          <span class="card-date">${j.fecha_de_lanzamiento || '–'}</span>
        </div>
        ${usuario?.rol === 'admin' ? `
        <div class="card-actions" onclick="event.stopPropagation()">
          <button class="btn-sm" onclick="editarJuego(${j.id_juego})">Editar</button>
          <button class="btn-sm danger" onclick="eliminarJuego(${j.id_juego})">Eliminar</button>
        </div>` : ''}
      </div>
    </div>`;
  }).join('');
}

async function verDetalleJuego(id) {
  const [{ data: juego }, { data: resenas }, { data: cals }] = await Promise.all([
    api('GET', `/videojuegos/${id}`),
    api('GET', `/resenas?id_juego=${id}`),
    api('GET', `/calificaciones?id_juego=${id}`),
  ]);

  document.getElementById('detalle-titulo').textContent = juego.titulo;
  document.getElementById('detalle-genero').textContent = juego.genero || '–';
  document.getElementById('detalle-desc').textContent   = juego.descripcion || '–';
  document.getElementById('detalle-fecha').textContent  = juego.fecha_de_lanzamiento || '–';
  document.getElementById('detalle-juego-id').value    = id;

  // Imagen de portada
  const imgWrap = document.getElementById('detalle-imagen-wrap');
  const imgEl   = document.getElementById('detalle-imagen');
  if (juego.imagen_url) {
    imgEl.src = juego.imagen_url;          // URL directa, sin escapar
    imgWrap.style.display = '';
  } else {
    imgWrap.style.display = 'none';
    imgEl.src = '';
  }

  const avg = cals.length
    ? (cals.reduce((s, c) => s + c.puntuacion, 0) / cals.length).toFixed(1)
    : '–';
  document.getElementById('detalle-score').textContent = `${avg} / 10`;

  const cont = document.getElementById('detalle-resenas');
  cont.innerHTML = resenas.length
    ? resenas.map(r => `
        <div class="resena-item">
          ${esc(r.contenido)}
          <div class="resena-meta">Usuario #${r.id_usuario} · ${r.fecha}
          ${usuario && (usuario.id_usuario === r.id_usuario || usuario.rol === 'admin')
            ? `<button class="btn-sm danger" style="margin-left:8px" onclick="eliminarResena(${r.id_resena})">Eliminar</button>`
            : ''}
          </div>
        </div>`).join('')
    : '<p style="color:var(--muted);font-size:.85rem">Sin reseñas aún.</p>';

  document.getElementById('detalle-form-resena').style.display = usuario ? '' : 'none';
  openModal('modal-detalle');
}

async function eliminarJuego(id) {
  if (!confirm('¿Eliminar este videojuego?')) return;
  const { ok, data } = await api('DELETE', `/videojuegos/${id}`);
  toast(ok ? data.message : data.error, !ok);
  if (ok) cargarJuegos();
}

function editarJuego(id) {
  api('GET', `/videojuegos/${id}`).then(({ data: j }) => {
    document.getElementById('juego-titulo').value      = j.titulo || '';
    document.getElementById('juego-descripcion').value = j.descripcion || '';
    document.getElementById('juego-genero').value      = j.genero || '';
    document.getElementById('juego-fecha').value       = j.fecha_de_lanzamiento || '';
    document.getElementById('juego-imagen').value      = j.imagen_url || '';
    document.getElementById('juego-edit-id').value     = id;
    document.getElementById('juego-modal-title').textContent = 'Editar videojuego';
    // mostrar preview si ya tiene imagen
    mostrarPreviewImagen(j.imagen_url || '');
    openModal('modal-juego');
  });
}

function mostrarPreviewImagen(url) {
  const wrap  = document.getElementById('juego-imagen-preview');
  const thumb = document.getElementById('juego-img-thumb');
  if (url) {
    thumb.src = url;
    wrap.style.display = '';
  } else {
    wrap.style.display = 'none';
    thumb.src = '';
  }
}

// ── RESEÑAS ───────────────────────────────────────
async function cargarResenas() {
  const { ok, data } = await api('GET', '/resenas');
  const tbody = document.querySelector('#resenas-table tbody');
  if (!ok || !data.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Sin reseñas.</td></tr>';
    return;
  }
  tbody.innerHTML = data.map(r => `
    <tr>
      <td class="mono">${r.id_resena}</td>
      <td>${esc(r.contenido.slice(0, 60))}${r.contenido.length > 60 ? '…' : ''}</td>
      <td class="mono">${r.fecha}</td>
      <td class="mono">${r.id_usuario}</td>
      <td class="mono">${r.id_juego}</td>
      <td>
        ${usuario && (usuario.id_usuario === r.id_usuario || usuario.rol === 'admin')
          ? `<button class="btn-sm danger" onclick="eliminarResena(${r.id_resena})">Eliminar</button>`
          : ''}
      </td>
    </tr>
  `).join('');
}

async function eliminarResena(id) {
  if (!confirm('¿Eliminar esta reseña?')) return;
  const { ok, data } = await api('DELETE', `/resenas/${id}`);
  toast(ok ? data.message : data.error, !ok);
  if (ok) { cargarResenas(); }
}

// ── CALIFICACIONES ────────────────────────────────
async function cargarCalificaciones() {
  const { ok, data } = await api('GET', '/calificaciones');
  const tbody = document.querySelector('#cal-table tbody');
  if (!ok || !data.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">Sin calificaciones.</td></tr>';
    return;
  }
  tbody.innerHTML = data.map(c => `
    <tr>
      <td class="mono">${c.id_calificacion}</td>
      <td><span class="score-pill">${c.puntuacion}</span></td>
      <td class="mono">${c.id_usuario}</td>
      <td class="mono">${c.id_juego}</td>
      <td>
        ${usuario && (usuario.id_usuario === c.id_usuario || usuario.rol === 'admin')
          ? `<button class="btn-sm danger" onclick="eliminarCalificacion(${c.id_calificacion})">Eliminar</button>`
          : ''}
      </td>
    </tr>
  `).join('');
}

async function eliminarCalificacion(id) {
  if (!confirm('¿Eliminar esta calificación?')) return;
  const { ok, data } = await api('DELETE', `/calificaciones/${id}`);
  toast(ok ? data.message : data.error, !ok);
  if (ok) cargarCalificaciones();
}

// ── USUARIOS (admin) ──────────────────────────────
async function cargarUsuarios() {
  const { ok, data } = await api('GET', '/usuarios');
  const tbody = document.querySelector('#users-table tbody');
  if (!ok) { tbody.innerHTML = '<tr><td colspan="4" class="empty">Sin acceso.</td></tr>'; return; }
  tbody.innerHTML = data.map(u => `
    <tr>
      <td class="mono">${u.id_usuario}</td>
      <td>${esc(u.nombre)}</td>
      <td class="mono">${esc(u.email)}</td>
      <td>
        <button class="btn-sm danger" onclick="eliminarUsuario(${u.id_usuario})">Eliminar</button>
      </td>
    </tr>
  `).join('');
}

async function eliminarUsuario(id) {
  if (!confirm('¿Eliminar este usuario?')) return;
  const { ok, data } = await api('DELETE', `/usuarios/${id}`);
  toast(ok ? data.message : data.error, !ok);
  if (ok) cargarUsuarios();
}

// ── LOGS (admin) ──────────────────────────────────
async function cargarLogs() {
  const { ok, data } = await api('GET', '/logs?limit=100');
  const tbody = document.querySelector('#logs-table tbody');
  if (!ok) { tbody.innerHTML = '<tr><td colspan="4" class="empty">Sin acceso.</td></tr>'; return; }
  tbody.innerHTML = data.map(l => `
    <tr>
      <td class="mono">${new Date(l.timestamp).toLocaleString('es-CO')}</td>
      <td class="mono">${l.id_usuario}</td>
      <td>${esc(l.accion)}</td>
      <td class="mono">${l.ip || '–'}</td>
    </tr>
  `).join('');
}

// ── Utilidad de escape XSS ────────────────────────
function esc(str) {
  return String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ═══════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {

  // Sidebar nav
  document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
    btn.addEventListener('click', () => {
      activarVista(btn.dataset.view);
      document.getElementById('sidebar').classList.remove('open');
    });
  });

  // Hamburger
  document.getElementById('hamburger').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  // Cerrar modales
  ['auth','juego','detalle','resena'].forEach(id => {
    document.getElementById(`close-${id}`)?.addEventListener('click', () => closeModal(`modal-${id}`));
    document.getElementById(`modal-${id}`)?.addEventListener('click', e => {
      if (e.target.id === `modal-${id}`) closeModal(`modal-${id}`);
    });
  });

  // Auth tabs
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.auth-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');
    });
  });

  // Mostrar modal auth
  document.getElementById('btn-show-auth').addEventListener('click', () => openModal('modal-auth'));

  // ── Login ──────────────────────────────────────
  document.getElementById('btn-login').addEventListener('click', async () => {
    const email    = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    if (!email || !password) return toast('Completa todos los campos', true);

    const { ok, data } = await api('POST', '/auth/login', { email, contrasena: password });
    if (!ok) return toast(data.error || 'Error al iniciar sesión', true);

    token   = data.token;
    usuario = data.usuario;
    localStorage.setItem('gc_token', token);
    localStorage.setItem('gc_usuario', JSON.stringify(usuario));
    closeModal('modal-auth');
    actualizarAuthUI();
    toast(`Bienvenido, ${usuario.nombre} ◈`);
    activarVista('juegos');
  });

  // ── Registro ───────────────────────────────────
  document.getElementById('btn-registro').addEventListener('click', async () => {
    const nombre   = document.getElementById('reg-nombre').value.trim();
    const email    = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const edad     = document.getElementById('reg-edad').value || null;
    if (!nombre || !email || !password) return toast('Completa los campos obligatorios', true);

    const { ok, data } = await api('POST', '/auth/registro', {
      nombre, email, contrasena: password, edad: edad ? Number(edad) : null
    });
    if (!ok) return toast(data.error || 'Error al registrarse', true);
    toast('Cuenta creada. Ahora inicia sesión.');
    document.querySelector('[data-tab="login"]').click();
  });

  // ── Logout ─────────────────────────────────────
  document.getElementById('btn-logout').addEventListener('click', async () => {
    await api('POST', '/auth/logout');
    token   = null;
    usuario = null;
    localStorage.removeItem('gc_token');
    localStorage.removeItem('gc_usuario');
    actualizarAuthUI();
    toast('Sesión cerrada.');
    activarVista('juegos');
  });

  // ── Btn Nuevo (juego o reseña) ─────────────────
  document.getElementById('btn-add').addEventListener('click', () => {
    if (vistaActual === 'juegos') {
      document.getElementById('juego-titulo').value      = '';
      document.getElementById('juego-descripcion').value = '';
      document.getElementById('juego-genero').value      = '';
      document.getElementById('juego-fecha').value       = '';
      document.getElementById('juego-imagen').value      = '';
      document.getElementById('juego-edit-id').value     = '';
      document.getElementById('juego-modal-title').textContent = 'Nuevo videojuego';
      mostrarPreviewImagen('');
      openModal('modal-juego');
    } else if (vistaActual === 'resenas') {
      openModal('modal-resena');
    }
  });

  // ── Preview imagen en tiempo real ──────────────
  document.getElementById('juego-imagen').addEventListener('input', e => {
    mostrarPreviewImagen(e.target.value.trim());
  });

  // ── Guardar juego (crear o editar) ────────────
  document.getElementById('btn-save-juego').addEventListener('click', async () => {
    const titulo      = document.getElementById('juego-titulo').value.trim();
    const descripcion = document.getElementById('juego-descripcion').value.trim();
    const genero      = document.getElementById('juego-genero').value.trim();
    const fecha       = document.getElementById('juego-fecha').value;
    const imagen_url  = document.getElementById('juego-imagen').value.trim() || null;
    const editId      = document.getElementById('juego-edit-id').value;

    if (!titulo) return toast('El título es obligatorio', true);

    let res;
    if (editId) {
      res = await api('PUT', `/videojuegos/${editId}`, {
        titulo, descripcion, genero, fecha_de_lanzamiento: fecha, imagen_url
      });
    } else {
      res = await api('POST', '/videojuegos', {
        titulo, descripcion, genero, fecha_de_lanzamiento: fecha, creado_por: 1, imagen_url
      });
    }

    toast(res.ok ? (editId ? 'Juego actualizado' : 'Juego creado') : res.data.error, !res.ok);
    if (res.ok) { closeModal('modal-juego'); cargarJuegos(); }
  });

  // ── Guardar reseña desde modal reseñas ────────
  document.getElementById('btn-save-resena').addEventListener('click', async () => {
    const contenido = document.getElementById('resena-contenido').value.trim();
    const id_juego  = document.getElementById('resena-id-juego').value;
    if (!contenido || !id_juego) return toast('Completa todos los campos', true);

    const { ok, data } = await api('POST', '/resenas', { contenido, id_juego: Number(id_juego) });
    toast(ok ? 'Reseña publicada' : data.error, !ok);
    if (ok) { closeModal('modal-resena'); cargarResenas(); }
  });

  // ── Publicar reseña desde detalle juego ───────
  document.getElementById('btn-enviar-resena').addEventListener('click', async () => {
    const contenido  = document.getElementById('nueva-resena-texto').value.trim();
    const puntuacion = Number(document.getElementById('nueva-puntuacion').value);
    const id_juego   = Number(document.getElementById('detalle-juego-id').value);

    if (!contenido) return toast('Escribe algo en tu reseña', true);

    const [r1, r2] = await Promise.all([
      api('POST', '/resenas',       { contenido, id_juego }),
      api('POST', '/calificaciones', { puntuacion, id_juego }),
    ]);

    if (!r1.ok) return toast(r1.data.error, true);
    toast('Reseña y calificación publicadas ◈');
    document.getElementById('nueva-resena-texto').value = '';
    verDetalleJuego(id_juego);  // refrescar detalle
  });

  // ── Init ───────────────────────────────────────
  await verificarSesion();   // limpia sesión expirada antes de pintar
  actualizarAuthUI();
  activarVista('juegos');
});
