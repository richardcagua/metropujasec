from datetime import datetime
import io
import json
import os
from urllib.parse import quote
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nobartys_clave_secreta_super_segura_2026'

# Clave de acceso para tu Panel de Administración
ADMIN_PASSWORD = 'pando10A@'

# Configuración de carpeta para archivos subidos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite 16MB


# --------------------------------------------------------------------------
# FILTRO DE MODERACIÓN DE IMÁGENES INAPROPIADAS / SEXUALES (PIL)
# --------------------------------------------------------------------------


def es_imagen_apropiada(file_storage):
    """Escanea la imagen cargada para detectar patrones de desnudez explícita."""
    try:
        img_bytes = file_storage.read()
        file_storage.seek(0)

        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img.thumbnail((150, 150))

        width, height = img.size
        pixels = img.getdata()

        conteo_sospechoso = 0
        total_pixels = width * height

        for r, g, b in pixels:
            if (
                    r > 95
                    and g > 40
                    and b > 20
                    and (max(r, g, b) - min(r, g, b) > 15)
                    and abs(r - g) > 15
                    and r > g
                    and r > b
            ):
                conteo_sospechoso += 1

        porcentaje = (conteo_sospechoso / total_pixels) * 100

        if porcentaje > 35.0:
            return (
                False,
                'El archivo cargado fue rechazado automáticamente por el filtro de'
                ' seguridad (detectado contenido no apropiado o explícito).',
            )

        return True, 'Ok'
    except Exception as e:
        file_storage.seek(0)
        return True, 'Ok'


# --------------------------------------------------------------------------
# LOGOTIPOS EMBEBIDOS (DATA URIs VECTORIALES NÍTIDOS)
# --------------------------------------------------------------------------

LOGO_TEATRO = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'><rect width='300' height='300' fill='%237A1A22'/><text x='150' y='45' fill='%23E2B3B7' font-family='Georgia, serif' font-size='20' font-weight='bold' text-anchor='middle' letter-spacing='5'>TEATRO</text><g stroke='%23E2B3B7' stroke-width='2' fill='none'><rect x='50' y='60' width='200' height='120' rx='2'/><line x1='50' y1='80' x2='250' y2='80'/><line x1='50' y1='100' x2='250' y2='100'/><line x1='50' y1='140' x2='250' y2='140'/><line x1='75' y1='60' x2='75' y2='180'/><line x1='105' y1='60' x2='105' y2='180'/><line x1='135' y1='60' x2='135' y2='180'/><line x1='165' y1='60' x2='165' y2='180'/><line x1='195' y1='60' x2='195' y2='180'/><line x1='225' y1='60' x2='225' y2='180'/><path d='M 135 140 A 15 15 0 0 1 165 140 Z' fill='%23E2B3B7'/></g><text x='150' y='225' fill='%23E2B3B7' font-family='Georgia, serif' font-size='30' font-weight='bold' text-anchor='middle' letter-spacing='2'>SANCHEZ</text><text x='150' y='265' fill='%23E2B3B7' font-family='Georgia, serif' font-size='30' font-weight='bold' text-anchor='middle' letter-spacing='2'>AGUILAR</text></svg>"

LOGO_SWEET = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'><rect width='300' height='300' fill='%230E542C'/><text x='150' y='105' fill='%23FFFFFF' font-family='Georgia, serif' font-size='52' font-style='italic' font-weight='bold' text-anchor='middle'>Sweet</text><text x='150' y='175' fill='%23FFFFFF' font-family='Georgia, serif' font-size='58' font-style='italic' text-anchor='middle'>&amp;</text><text x='150' y='240' fill='%23FFFFFF' font-family='Georgia, serif' font-size='52' font-style='italic' font-weight='bold' text-anchor='middle'>Coffee</text></svg>"

LOGO_UG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 250'><rect width='300' height='250' fill='%23FFFFFF'/><g font-family='Arial, sans-serif' font-weight='900'><path d='M 35 40 L 80 40 L 80 140 C 80 175 110 175 110 140 L 110 40 L 155 40 L 155 140 C 155 210 35 210 35 140 Z' fill='%2300A3E0'/><path d='M 135 125 C 135 50 215 50 255 80 L 220 112 C 200 95 178 95 178 125 C 178 155 205 155 220 140 L 195 140 L 195 112 L 260 112 L 260 170 C 230 205 160 205 135 155 Z' fill='%23003366'/><path d='M 210 100 Q 235 80 250 65 Q 235 95 218 112 Z' fill='%2300A3E0'/></g></svg>"

# --------------------------------------------------------------------------
# BASE DE DATOS EN MEMORIA Y CONTROL DE REINICIO TRIMESTRAL
# --------------------------------------------------------------------------

mes_actual_nombre = 'Trimestre Q3 - 2026'
ultimo_trimestre_reset = '2026-Q3'

ranking_mensual = [
    {
        'id': 1,
        'nombre': 'Teatro Sánchez Aguilar',
        'monto': 5.00,
        'direccion': 'Km 1.5 Av. Samborondón, Samborondón',
        'web': 'https://www.teatrosanchezaguilar.org',
        'telefono': '',
        'redes_nombre': '',
        'redes_url': '',
        'logo_url': LOGO_TEATRO,
    },
    {
        'id': 2,
        'nombre': 'Sweet & Coffee',
        'monto': 3.00,
        'direccion': 'Puerto Santa Ana, Guayaquil',
        'web': 'https://www.sweetandcoffee.com.ec',
        'telefono': '',
        'redes_nombre': '',
        'redes_url': '',
        'logo_url': LOGO_SWEET,
    },
    {
        'id': 3,
        'nombre': 'Universidad de Guayaquil',
        'monto': 2.00,
        'direccion': 'Av. Delta y Av. Kennedy, Guayaquil',
        'web': 'https://www.ug.edu.ec',
        'telefono': '',
        'redes_nombre': '',
        'redes_url': '',
        'logo_url': LOGO_UG,
    },
]

top3_historico = [
    {
        'id': 101,
        'nombre': ranking_mensual[0]['nombre'],
        'monto': ranking_mensual[0]['monto'],
        'web': ranking_mensual[0]['web'],
        'telefono': ranking_mensual[0]['telefono'],
        'redes_nombre': ranking_mensual[0]['redes_nombre'],
        'redes_url': ranking_mensual[0]['redes_url'],
        'media_url': (
            'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80'
        ),
        'fecha': mes_actual_nombre,
    },
    {
        'id': 102,
        'nombre': ranking_mensual[1]['nombre'],
        'monto': ranking_mensual[1]['monto'],
        'web': ranking_mensual[1]['web'],
        'telefono': ranking_mensual[1]['telefono'],
        'redes_nombre': ranking_mensual[1]['redes_nombre'],
        'redes_url': ranking_mensual[1]['redes_url'],
        'media_url': (
            'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80'
        ),
        'fecha': mes_actual_nombre,
    },
    {
        'id': 103,
        'nombre': ranking_mensual[2]['nombre'],
        'monto': ranking_mensual[2]['monto'],
        'web': ranking_mensual[2]['web'],
        'telefono': ranking_mensual[2]['telefono'],
        'redes_nombre': ranking_mensual[2]['redes_nombre'],
        'redes_url': ranking_mensual[2]['redes_url'],
        'media_url': (
            'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80'
        ),
        'fecha': mes_actual_nombre,
    },
]


def verificar_reinicio_trimestral():
    """Verifica si ha comenzado un nuevo trimestre para restablecer montos a $0 conservando las posiciones."""
    global ranking_mensual, ultimo_trimestre_reset, mes_actual_nombre
    ahora = datetime.now()
    trimestre_actual = (ahora.month - 1) // 3 + 1
    clave_trimestre = f'{ahora.year}-Q{trimestre_actual}'

    # Si inicia un nuevo trimestre el 1° de mes, reinicia montos a $0 conservando las marcas
    if ultimo_trimestre_reset != clave_trimestre and ahora.day == 1:
        for item in ranking_mensual:
            item['monto'] = 0.00
        ultimo_trimestre_reset = clave_trimestre
        mes_actual_nombre = f'Trimestre Q{trimestre_actual} - {ahora.year}'


def formatear_telefono_wa(num):
    if not num:
        return ''
    num_clean = ''.join(filter(str.isdigit, str(num)))
    if not num_clean:
        return ''
    if num_clean.startswith('0'):
        num_clean = '593' + num_clean[1:]
    elif not num_clean.startswith('593'):
        num_clean = '593' + num_clean
    return num_clean


def formatear_redes_url(redes):
    if not redes:
        return '', ''
    redes = redes.strip()
    if not redes:
        return '', ''
    if redes.startswith('http'):
        username = '@' + redes.rstrip('/').split('/')[-1]
        return username, redes
    username = redes if redes.startswith('@') else '@' + redes
    clean_user = username.replace('@', '')
    return username, f'https://www.instagram.com/{clean_user}'


def guardar_archivo(file_obj):
    if file_obj and file_obj.filename != '':
        filename = secure_filename(
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_obj.filename}"
        )
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        return f'/static/uploads/{filename}'
    return ''


def actualizar_rankings(nuevo_registro):
    global ranking_mensual, top3_historico

    if not nuevo_registro.get('nombre'):
        ranking_mensual = sorted(
            ranking_mensual, key=lambda x: x['monto'], reverse=True
        )[:50]
        top3_historico = sorted(
            top3_historico, key=lambda x: x['monto'], reverse=True
        )[:3]
        return

    monto = nuevo_registro['monto']
    redes_nombre, redes_url = formatear_redes_url(nuevo_registro.get('redes', ''))
    tel_wa = (
        formatear_telefono_wa(nuevo_registro.get('telefono', ''))
        if nuevo_registro.get('telefono')
        else ''
    )

    # 1. Actualizar Ránking Trimestral (Top 50)
    existente = next(
        (
            item
            for item in ranking_mensual
            if item['nombre'].lower() == nuevo_registro['nombre'].lower()
        ),
        None,
    )

    if existente:
        existente['monto'] += monto
        if nuevo_registro.get('web'):
            existente['web'] = nuevo_registro['web']
        if nuevo_registro.get('direccion'):
            existente['direccion'] = nuevo_registro['direccion']
        if nuevo_registro.get('logo_url'):
            existente['logo_url'] = nuevo_registro['logo_url']
        if tel_wa:
            existente['telefono'] = tel_wa
        if redes_url:
            existente['redes_nombre'] = redes_nombre
            existente['redes_url'] = redes_url
    else:
        ranking_mensual.append({
            'id': len(ranking_mensual) + 1,
            'nombre': nuevo_registro['nombre'],
            'monto': monto,
            'direccion': nuevo_registro.get('direccion', ''),
            'logo_url': nuevo_registro.get('logo_url', ''),
            'web': nuevo_registro.get('web', ''),
            'telefono': tel_wa,
            'redes_nombre': redes_nombre,
            'redes_url': redes_url,
        })

    ranking_mensual = sorted(
        ranking_mensual, key=lambda x: x['monto'], reverse=True
    )[:50]

    # 2. Evaluar ingreso al Top 3 Inmortal
    media_inmortal = nuevo_registro.get('media_url') or (
            nuevo_registro.get('logo_url')
            or 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80'
    )

    top3_historico.append({
        'id': len(top3_historico) + 100,
        'nombre': nuevo_registro['nombre'],
        'monto': monto,
        'web': nuevo_registro.get('web', ''),
        'telefono': tel_wa,
        'redes_nombre': redes_nombre,
        'redes_url': redes_url,
        'media_url': media_inmortal,
        'fecha': mes_actual_nombre,
    })

    top3_historico = sorted(
        top3_historico, key=lambda x: x['monto'], reverse=True
    )[:3]


# --------------------------------------------------------------------------
# PLANTILLA HTML PRINCIPAL (CON TEXTOS Y LÓGICA TRIMESTRAL)
# --------------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetroPuja.ec | Ránking de Posicionamiento Comercial en Guayas</title>

    <!-- METADATOS SEO INVISIBLES PARA GOOGLE -->
    <meta name="description" content="MetroPuja.ec es la subasta interactiva de visibilidad comercial para marcas y empresas en Guayaquil, Samborondón, Daule y la provincia del Guayas.">
    <meta name="keywords" content="MetroPuja, MetroPuja.ec, posicionamiento comercial Guayaquil, publicidad digital Guayas, marcas Samborondón, empresas Daule, subasta web Ecuador, directorio de empresas Guayaquil, SEO Ecuador">
    <meta name="author" content="MetroPuja.ec - @nobartys">
    <meta name="robots" content="index, follow">

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">

    <style>
        body { font-family: 'Outfit', sans-serif; background-color: #030712; }

        @keyframes orbDrift1 { 0%, 100% { transform: translate(0px, 0px) scale(1); } 50% { transform: translate(60px, 40px) scale(1.15); } }
        @keyframes orbDrift2 { 0%, 100% { transform: translate(0px, 0px) scale(1); } 50% { transform: translate(-50px, -30px) scale(1.25); } }

        @keyframes goldGlow {
            0%, 100% { border-color: rgba(245, 158, 11, 0.4); box-shadow: 0 0 20px rgba(245, 158, 11, 0.25); }
            50% { border-color: rgba(251, 191, 36, 0.9); box-shadow: 0 0 35px rgba(245, 158, 11, 0.5); }
        }

        @keyframes emeraldGlow {
            0%, 100% { border-color: rgba(16, 185, 129, 0.3); box-shadow: 0 0 15px rgba(16, 185, 129, 0.15); }
            50% { border-color: rgba(16, 185, 129, 0.7); box-shadow: 0 0 30px rgba(16, 185, 129, 0.3); }
        }

        .animate-orb-1 { animation: orbDrift1 14s ease-in-out infinite; }
        .animate-orb-2 { animation: orbDrift2 16s ease-in-out infinite; }

        .gold-card-glow { animation: goldGlow 4s infinite ease-in-out; }
        .emerald-card-glow { animation: emeraldGlow 5s infinite ease-in-out; }

        .bg-grid-pattern { background-image: radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px); background-size: 24px 24px; }
    </style>
</head>
<body class="text-slate-100 min-h-screen relative overflow-x-hidden bg-grid-pattern selection:bg-amber-400 selection:text-slate-950">

    <div class="fixed top-[-100px] left-1/2 -translate-x-1/2 -z-10 w-[800px] h-[500px] bg-emerald-500/15 blur-[160px] rounded-full pointer-events-none animate-orb-1"></div>
    <div class="fixed bottom-[-100px] right-[-100px] -z-10 w-[700px] h-[500px] bg-amber-500/20 blur-[170px] rounded-full pointer-events-none animate-orb-2"></div>
    <div class="fixed top-[35%] left-[-150px] -z-10 w-[500px] h-[500px] bg-yellow-500/15 blur-[160px] rounded-full pointer-events-none"></div>

    <!-- NAVBAR -->
    <header class="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-50 shadow-2xl">
        <div class="max-w-5xl mx-auto px-4 py-3.5 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="relative group">
                    <div class="absolute -inset-0.5 bg-gradient-to-r from-amber-400 via-emerald-400 to-yellow-500 rounded-xl blur opacity-80 group-hover:opacity-100 transition duration-300"></div>
                    <div class="relative bg-slate-950 text-amber-400 font-black text-xl px-3.5 py-1 rounded-xl">MP</div>
                </div>
                <div>
                    <h1 class="font-black text-xl tracking-tight text-white flex items-center gap-1">MetroPuja<span class="text-amber-400">.ec</span></h1>
                    <p class="text-[11px] text-slate-400 font-medium">Exclusivo Guayas • Guayaquil • Samborondón • Daule</p>
                </div>
            </div>

            <div class="flex items-center gap-3">
                <a href="#participar" class="bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 hover:from-amber-300 hover:to-yellow-200 text-slate-950 font-black text-xs px-5 py-2.5 rounded-xl flex items-center gap-2 shadow-lg transition-all hover:scale-105">
                    <i class="fa-solid fa-bolt text-slate-950 animate-pulse"></i> Pujar Mi Marca
                </a>
            </div>
        </div>
    </header>

    <!-- NOTIFICACIONES -->
    {% if msg %}
    <div class="max-w-5xl mx-auto px-4 pt-6">
        <div class="bg-emerald-950/80 border border-emerald-500/60 text-emerald-200 px-5 py-3.5 rounded-2xl flex items-center gap-3 text-sm shadow-2xl backdrop-blur-md">
            <i class="fa-solid fa-circle-check text-emerald-400 text-xl"></i>
            <span class="font-semibold">{{ msg }}</span>
        </div>
    </div>
    {% endif %}

    {% if err %}
    <div class="max-w-5xl mx-auto px-4 pt-6">
        <div class="bg-rose-950/80 border border-rose-500/60 text-rose-200 px-5 py-3.5 rounded-2xl flex items-center gap-3 text-sm shadow-2xl backdrop-blur-md">
            <i class="fa-solid fa-shield-cat text-rose-400 text-xl animate-bounce"></i>
            <span class="font-semibold">{{ err }}</span>
        </div>
    </div>
    {% endif %}

    <main class="max-w-5xl mx-auto px-4 py-8 space-y-10">

        <!-- HERO BANNER -->
        <section>
            <div class="relative bg-slate-900/60 border border-slate-800 rounded-3xl p-7 md:p-10 backdrop-blur-2xl shadow-2xl overflow-hidden emerald-card-glow">
                <div class="max-w-2xl relative z-10 space-y-4">
                    <div class="inline-flex items-center gap-2 bg-emerald-950/80 border border-emerald-500/40 px-3.5 py-1 rounded-full text-[11px] font-bold text-emerald-300 tracking-wider uppercase">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> SUBASTA EN VIVO • GUAYAS
                    </div>

                    <h2 class="text-3xl md:text-5xl font-black text-white leading-tight">
                        Puja para posicionar tu Marca en el <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-300 to-emerald-400">Puesto #1</span>.
                    </h2>

                    <p class="text-slate-300 text-sm md:text-base leading-relaxed">
                        Las empresas y proyectos con mayor valor acumulado ocupan la cima del ranking comercial, captando la atención directa de clientes en la provincia del Guayas.
                    </p>
                </div>
            </div>
        </section>

        <!-- AVISO DE REINICIO TRIMESTRAL -->
        <div class="bg-amber-950/40 border border-amber-500/50 rounded-2xl p-4 flex items-start gap-4 backdrop-blur-md shadow-[0_0_20px_rgba(245,158,11,0.2)]">
            <div class="bg-amber-500/30 text-amber-300 p-2.5 rounded-xl text-lg shadow-inner">
                <i class="fa-solid fa-rotate-left"></i>
            </div>
            <div class="text-xs leading-relaxed space-y-0.5">
                <strong class="text-amber-300 text-sm font-bold block">Tablas Restablecidas Cada 3 Meses (Trimestral)</strong>
                <p class="text-slate-300">
                    El 1° día de cada trimestre, los contadores de pujas vuelven a $0.00 USD. **Las marcas conservan su posición en la lista**, listas para sumar sus nuevas pujas en el nuevo ciclo.
                </p>
            </div>
        </div>

        <!-- SECCIÓN 1: RÁNKING INMORTAL -->
        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <div>
                    <span class="bg-gradient-to-r from-amber-500/20 to-yellow-500/20 text-amber-300 font-extrabold text-[11px] uppercase tracking-widest px-3.5 py-1 rounded-xl border border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.3)] inline-flex items-center gap-1.5 mb-1">
                        <i class="fa-solid fa-crown text-amber-400 animate-bounce"></i> Ránking Inmortal
                    </span>
                    <h3 class="text-2xl md:text-3xl font-black text-white">Top 3 Histórico de Todos los Tiempos</h3>
                </div>
                <span class="text-xs text-amber-300/90 bg-amber-950/60 px-3.5 py-1.5 rounded-xl border border-amber-500/40 hidden md:inline-flex items-center gap-1.5 shadow-inner">
                    <i class="fa-solid fa-infinity text-amber-400"></i> Récords Permanentes
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {% for h in top3 %}
                <div class="group relative bg-slate-900/80 border border-amber-500/50 hover:border-amber-400 rounded-3xl overflow-hidden shadow-2xl flex flex-col justify-between transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_0_35px_rgba(245,158,11,0.35)] backdrop-blur-xl gold-card-glow">

                    <div class="absolute top-3 left-3 z-20">
                        {% if loop.index == 1 %}
                            <span class="bg-gradient-to-r from-amber-300 via-yellow-400 to-amber-500 text-slate-950 font-black text-[11px] px-3.5 py-1 rounded-full shadow-[0_0_15px_rgba(245,158,11,0.6)] flex items-center gap-1">
                                <i class="fa-solid fa-trophy"></i> #1 HISTÓRICO ORO
                            </span>
                        {% elif loop.index == 2 %}
                            <span class="bg-gradient-to-r from-slate-200 to-slate-400 text-slate-950 font-black text-[11px] px-3.5 py-1 rounded-full shadow-lg">
                                #2 HISTÓRICO
                            </span>
                        {% else %}
                            <span class="bg-gradient-to-r from-amber-700 to-amber-900 text-white font-black text-[11px] px-3.5 py-1 rounded-full shadow-lg">
                                #3 HISTÓRICO
                            </span>
                        {% endif %}
                    </div>

                    <div>
                        {% if h.media_url %}
                        <div class="h-48 overflow-hidden relative bg-slate-950 flex items-center justify-center">
                            {% if h.media_url.endswith(('.mp4', '.webm', '.ogg')) %}
                            <video src="{{ h.media_url }}" controls class="w-full h-full object-cover"></video>
                            {% else %}
                            <img src="{{ h.media_url }}" alt="" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700">
                            {% endif %}
                            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent"></div>
                        </div>
                        {% endif %}

                        <div class="p-6 space-y-3">
                            <h4 class="text-xl font-bold text-white group-hover:text-amber-300 transition-colors">{{ h.nombre }}</h4>
                            <div class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-300 to-emerald-400 tracking-tight">
                                ${{ "%.2f"|format(h.monto) }} <span class="text-xs text-slate-400 font-normal">USD</span>
                            </div>

                            <div class="space-y-2 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
                                {% if h.web %}
                                <p class="truncate flex items-center gap-2">
                                    <i class="fa-solid fa-globe text-amber-400"></i>
                                    <a href="{{ h.web }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-amber-300 font-medium">
                                        {{ h.web.replace('https://', '').replace('http://', '').replace('www.', '') }}
                                    </a>
                                </p>
                                {% endif %}

                                {% if h.telefono %}
                                <p class="flex items-center gap-2">
                                    <i class="fa-brands fa-whatsapp text-emerald-400"></i>
                                    <a href="https://wa.me/{{ h.telefono }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-medium">
                                        WhatsApp (+{{ h.telefono }})
                                    </a>
                                </p>
                                {% endif %}

                                {% if h.redes_url %}
                                <p class="flex items-center gap-2">
                                    <i class="fa-solid fa-at text-amber-400"></i>
                                    <a href="{{ h.redes_url }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-amber-300 font-medium">
                                        {{ h.redes_nombre }}
                                    </a>
                                </p>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="p-4 bg-slate-950/90 border-t border-amber-500/20 text-[11px] text-slate-400 flex justify-between items-center">
                        <span>Récord registrado:</span>
                        <strong class="text-amber-300 font-semibold">{{ h.fecha }}</strong>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- TOP 50 TRIMESTRAL VERTICAL -->
        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <div>
                    <span class="bg-emerald-500/10 text-emerald-400 font-bold text-[11px] uppercase tracking-widest px-3 py-1 rounded-lg border border-emerald-500/30 inline-block mb-1">
                        <i class="fa-solid fa-calendar-days mr-1"></i> {{ mes_actual }}
                    </span>
                    <h3 class="text-2xl md:text-3xl font-black text-white">Top 50 Trimestral (Provincia del Guayas)</h3>
                </div>
            </div>

            <div class="space-y-3.5">
                {% for m in mensual %}
                <div class="group bg-slate-900/50 border border-slate-800/90 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-4 backdrop-blur-xl">
                    <div class="flex items-center gap-4">
                        <div class="relative flex-shrink-0">
                            <div class="w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 p-0.5 flex items-center justify-center shadow-lg overflow-hidden">
                                {% if m.logo_url %}
                                <img src="{{ m.logo_url }}" alt="" class="w-full h-full object-cover rounded-xl">
                                {% else %}
                                <i class="fa-solid fa-building text-slate-600 text-xl"></i>
                                {% endif %}
                            </div>
                            <span class="absolute -top-2 -right-2 bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-lg shadow-lg">
                                #{{ loop.index }}
                            </span>
                        </div>

                        <div class="space-y-0.5">
                            <h4 class="font-bold text-white text-lg group-hover:text-emerald-300 transition-colors">{{ m.nombre }}</h4>
                            {% if m.direccion %}
                            <p class="text-xs text-slate-400 flex items-center gap-1.5"><i class="fa-solid fa-location-dot text-emerald-400 text-[10px]"></i> {{ m.direccion }}</p>
                            {% endif %}

                            <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 pt-1">
                                {% if m.web %}
                                <a href="{{ m.web }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline font-medium">
                                    <i class="fa-solid fa-link text-[10px]"></i> Web
                                </a>
                                {% endif %}
                                {% if m.telefono %}
                                <a href="https://wa.me/{{ m.telefono }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline font-medium">
                                    <i class="fa-brands fa-whatsapp text-[11px]"></i> WhatsApp
                                </a>
                                {% endif %}
                                {% if m.redes_url %}
                                <a href="{{ m.redes_url }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline font-medium">
                                    <i class="fa-solid fa-at text-[10px]"></i> {{ m.redes_nombre }}
                                </a>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center justify-between md:justify-end gap-4 border-t md:border-t-0 border-slate-800/80 pt-3 md:pt-0">
                        <span class="text-2xl font-black text-emerald-400">${{ "%.2f"|format(m.monto) }} <span class="text-xs text-slate-400 font-normal">USD</span></span>
                    </div>
                </div>
                {% else %}
                <div class="text-center py-10 bg-slate-900/30 border border-slate-800 rounded-2xl text-slate-400 text-sm">
                    No hay pujas registradas este trimestre aún. ¡Sé el primero en posicionarte en Guayas!
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- FORMULARIO DE PUJA -->
        <section id="participar" class="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-10 backdrop-blur-2xl shadow-2xl relative">
            <div class="mb-8 space-y-1">
                <h3 class="text-2xl font-black text-white flex items-center gap-2">
                    <i class="fa-solid fa-paper-plane text-amber-400"></i> Formulario de Posicionamiento (Guayas)
                </h3>
                <p class="text-xs text-slate-400">Tu puja te posicionará en el Top 50 Trimestral o Top 3 Inmortal.</p>
            </div>

            <form action="/pujar" method="POST" enctype="multipart/form-data" class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div class="md:col-span-2">
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Nombre de la Persona / Empresa / Marca *</label>
                    <input type="text" name="nombre" placeholder="Ej: Mi Negocio Guayaquil / Samborondón" required 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-amber-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Dirección <span class="text-emerald-400 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="text" name="direccion" placeholder="Ej: Puerto Santa Ana, Guayaquil" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Página Web <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="url" name="web" placeholder="https://miweb.com" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Número de Contacto / WhatsApp <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="text" name="telefono" placeholder="Ej: 0991234567" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Redes Sociales <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="text" name="redes" placeholder="Ej: @minegociogye" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Logotipo de la Empresa <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <div class="relative border-2 border-dashed border-slate-800 hover:border-emerald-500 rounded-2xl p-4 text-center bg-slate-950/60 transition-all cursor-pointer group">
                        <input type="file" name="logo_file" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onchange="document.getElementById('logo-text').innerText = '✓ ' + this.files[0].name">
                        <i class="fa-solid fa-image text-slate-500 group-hover:text-emerald-400 text-xl mb-1.5 block"></i>
                        <span id="logo-text" class="text-xs text-slate-400 block truncate font-medium">Haz clic o arrastra tu logo aquí</span>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Subir Foto o Video <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <div class="relative border-2 border-dashed border-slate-800 hover:border-amber-400 rounded-2xl p-4 text-center bg-slate-950/60 transition-all cursor-pointer group">
                        <input type="file" name="media_file" accept="image/*,video/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onchange="document.getElementById('media-text').innerText = '✓ ' + this.files[0].name">
                        <i class="fa-solid fa-cloud-arrow-up text-slate-500 group-hover:text-amber-400 text-xl mb-1.5 block"></i>
                        <span id="media-text" class="text-xs text-slate-400 block truncate font-medium">Haz clic o arrastra tu foto o video aquí</span>
                    </div>
                </div>

                <div class="md:col-span-2 pt-3">
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Monto a Pujar ($ USD) *</label>
                    <div class="flex gap-3">
                        <div class="relative flex-1">
                            <span class="absolute left-4 top-3 text-sm font-bold text-amber-400">$</span>
                            <input type="number" name="monto" min="1" step="1" placeholder="Ej: 2.00" required 
                                   class="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-8 pr-4 py-3 text-base text-white font-black focus:outline-none focus:border-amber-400">
                        </div>
                        <button type="submit" class="bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 hover:from-amber-300 hover:to-yellow-200 text-slate-950 font-black px-8 py-3 rounded-xl text-xs uppercase tracking-wider shadow-[0_0_20px_rgba(245,158,11,0.4)]">
                            <i class="fa-solid fa-bolt mr-1"></i> Confirmar Puja
                        </button>
                    </div>
                </div>
            </form>
        </section>

    </main>

    <footer class="border-t border-slate-800/80 bg-slate-950/90 py-10 text-center text-xs text-slate-500 space-y-2">
        <p>© 2026 MetroPuja.ec — Plataforma de Posicionamiento Competitivo Exclusiva para la Provincia del Guayas.</p>
        <p class="text-slate-400 font-medium">
            Creado por <a href="https://www.instagram.com/nobartys/" target="_blank" rel="noopener noreferrer" class="text-amber-400 hover:underline font-bold inline-flex items-center gap-1"><i class="fa-brands fa-instagram"></i> @nobartys</a>
        </p>
        <p class="text-slate-400">Soporte Técnico: <a href="mailto:nobartysinformacion@gmail.com" class="text-amber-400 hover:underline font-bold">nobartysinformacion@gmail.com</a></p>
    </footer>

</body>
</html>
"""

# --------------------------------------------------------------------------
# PLANTILLA HTML PANEL DE ADMINISTRACIÓN PROTEGIDO
# --------------------------------------------------------------------------
ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Administración Protegido | MetroPuja.ec</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">

    <div class="max-w-4xl mx-auto space-y-6">

        <div class="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
                <h1 class="text-2xl font-black text-amber-400"><i class="fa-solid fa-shield-halved"></i> Panel de Control Dueño</h1>
                <p class="text-xs text-slate-400">Modifica, edita o borra marcas en tiempo real en menos de 1 segundo.</p>
            </div>
            <div class="flex items-center gap-2">
                <a href="/" class="text-xs bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg"><i class="fa-solid fa-globe mr-1"></i> Ver Sitio Web</a>
                <form action="/admin/reiniciar-trimestre" method="POST">
                    <button type="submit" onclick="return confirm('¿Deseas reiniciar los contadores a $0.00 conservando las marcas en sus posiciones actuales?')" class="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-3 py-2 rounded-lg">
                        <i class="fa-solid fa-rotate-left mr-1"></i> Reiniciar Trimestre ($0.00)
                    </button>
                </form>
                <a href="/admin/logout" class="text-xs bg-rose-950 text-rose-300 hover:bg-rose-900 px-3 py-2 rounded-lg"><i class="fa-solid fa-power-off"></i></a>
            </div>
        </div>

        {% if msg %}
        <div class="bg-emerald-950 border border-emerald-500 text-emerald-300 p-3 rounded-lg text-xs font-bold">
            {{ msg }}
        </div>
        {% endif %}

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 class="text-lg font-bold text-white"><i class="fa-solid fa-list-check text-amber-400"></i> Editar Ránking Trimestral Actual</h2>

            <div class="space-y-3">
                {% for item in mensual %}
                <form action="/admin/editar-marca" method="POST" class="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
                    <input type="hidden" name="id" value="{{ item.id }}">

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-2 w-full">
                        <input type="text" name="nombre" value="{{ item.nombre }}" required class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-white">
                        <input type="text" name="direccion" value="{{ item.direccion }}" placeholder="Dirección" class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-white">
                        <input type="number" name="monto" value="{{ item.monto }}" step="0.5" required class="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-amber-400 font-bold">
                    </div>

                    <div class="flex gap-2 w-full md:w-auto justify-end">
                        <button type="submit" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold px-3 py-1.5 rounded text-xs">
                            <i class="fa-solid fa-floppy-disk"></i> Guardar
                        </button>
                        <a href="/admin/eliminar-marca/{{ item.id }}" onclick="return confirm('¿Borrar esta marca del ranking?')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-1.5 rounded text-xs">
                            <i class="fa-solid fa-trash"></i> Borrar
                        </a>
                    </div>
                </form>
                {% endfor %}
            </div>
        </div>

    </div>

</body>
</html>
"""


# --------------------------------------------------------------------------
# RUTAS DE NAVEGACIÓN Y ACCIONES
# --------------------------------------------------------------------------


@app.route('/')
def index():
    verificar_reinicio_trimestral()
    msg = request.args.get('msg', '')
    err = request.args.get('err', '')
    return render_template_string(
        HTML_TEMPLATE,
        top3=top3_historico,
        mensual=ranking_mensual,
        mes_actual=mes_actual_nombre,
        msg=msg,
        err=err,
    )


@app.route('/pujar', methods=['POST'])
def pujar():
    try:
        verificar_reinicio_trimestral()
        nombre = request.form.get('nombre', '').strip()
        direccion = request.form.get('direccion', '').strip()
        web = request.form.get('web', '').strip()
        telefono = request.form.get('telefono', '').strip()
        redes = request.form.get('redes', '').strip()
        monto = float(request.form.get('monto', 0))

        logo_file = request.files.get('logo_file')
        media_file = request.files.get('media_file')

        # 🛡️ FILTRO ANTI-CONTENIDO EXPLÍCITO O SEXUAL
        if logo_file and logo_file.filename != '':
            es_valida, causa = es_imagen_apropiada(logo_file)
            if not es_valida:
                return redirect(url_for('index', err=causa))

        if media_file and media_file.filename != '':
            es_valida, causa = es_imagen_apropiada(media_file)
            if not es_valida:
                return redirect(url_for('index', err=causa))

        logo_url = guardar_archivo(logo_file) if logo_file else ''
        media_url = guardar_archivo(media_file) if media_file else ''

        if nombre and monto > 0:
            nuevo_registro = {
                'nombre': nombre,
                'direccion': direccion,
                'web': web,
                'telefono': telefono,
                'redes': redes,
                'logo_url': logo_url,
                'media_url': media_url,
                'monto': monto,
            }

            actualizar_rankings(nuevo_registro)
            return redirect(
                url_for(
                    'index',
                    msg=(
                        f'¡Puja de ${monto:.2f} USD registrada exitosamente para'
                        f' {nombre}!'
                    ),
                )
            )

    except Exception as e:
        print(f'Error registrando puja: {e}')

    return redirect(url_for('index'))


# --------------------------------------------------------------------------
# PANEL DE ADMINISTRACIÓN SEGURO Y ACCIONES EN TIEMPO REAL
# --------------------------------------------------------------------------


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        clave = request.form.get('password')
        if clave == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_panel'))
        return render_template_string(
            "<body style='background:#030712; color:white; font-family:sans-serif;"
            " display:flex; justify-content:center; align-items:center;"
            " height:100vh;'><form method='POST' style='background:#111827;"
            " padding:30px; border-radius:16px;'><h3 style='color:#f59e0b;'>Clave"
            " Incorrecta</h3><input type='password' name='password'"
            " placeholder='Ingresa la clave' style='padding:8px;"
            " border-radius:8px;'><button type='submit'"
            " style='background:#f59e0b; padding:8px 16px; border-radius:8px;"
            " font-weight:bold;'>Entrar</button></form></body>"
        )

    return render_template_string(
        "<body style='background:#030712; color:white; font-family:sans-serif;"
        " display:flex; justify-content:center; align-items:center;"
        " height:100vh;'><form method='POST' style='background:#111827;"
        " padding:30px; border-radius:16px; display:flex; flex-direction:column;"
        " gap:12px; width:300px;'><h3 style='color:#f59e0b; margin:0;'>Panel de"
        " Dueño</h3><input type='password' name='password' placeholder='Clave de"
        " Administración' required style='padding:10px; border-radius:8px;"
        " border:1px solid #374151; background:#030712; color:white;'><button"
        " type='submit' style='background:#f59e0b; color:#030712; padding:10px;"
        " border-radius:8px; font-weight:bold; cursor:pointer;'>Acceder"
        " Ahora</button></form></body>"
    )


@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    msg = request.args.get('msg', '')
    return render_template_string(
        ADMIN_PANEL_TEMPLATE, mensual=ranking_mensual, msg=msg
    )


@app.route('/admin/reiniciar-trimestre', methods=['POST'])
def reiniciar_trimestre_manual():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    global ranking_mensual
    for item in ranking_mensual:
        item['monto'] = 0.00
    return redirect(
        url_for(
            'admin_panel',
            msg=(
                '¡El trimestre fue reiniciado a $0.00 USD manteniendo las'
                ' marcas en sus posiciones!'
            ),
        )
    )


@app.route('/admin/editar-marca', methods=['POST'])
def editar_marca():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    try:
        item_id = int(request.form.get('id'))
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        monto = float(request.form.get('monto'))

        for item in ranking_mensual:
            if item['id'] == item_id:
                item['nombre'] = nombre
                item['direccion'] = direccion
                item['monto'] = monto
                break

        actualizar_rankings({'nombre': '', 'monto': 0})
        return redirect(
            url_for('admin_panel', msg='¡Marca actualizada en tiempo real!')
        )
    except Exception as e:
        print(e)
    return redirect(url_for('admin_panel'))


@app.route('/admin/eliminar-marca/<int:item_id>')
def eliminar_marca(item_id):
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    global ranking_mensual
    ranking_mensual = [item for item in ranking_mensual if item['id'] != item_id]
    return redirect(
        url_for(
            'admin_panel', msg='¡Marca borrada del ranking instantáneamente!'
        )
    )


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
