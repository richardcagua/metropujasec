from datetime import datetime
import json
import os
from urllib.parse import quote
from flask import Flask, jsonify, redirect, render_template_string, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de carpeta para archivos subidos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite 16MB

# --------------------------------------------------------------------------
# LOGOTIPOS EMBEBIDOS (DATA URIs VECTORIALES NÍTIOS)
# --------------------------------------------------------------------------

LOGO_TEATRO = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'><rect width='300' height='300' fill='%237A1A22'/><text x='150' y='45' fill='%23E2B3B7' font-family='Georgia, serif' font-size='20' font-weight='bold' text-anchor='middle' letter-spacing='5'>TEATRO</text><g stroke='%23E2B3B7' stroke-width='2' fill='none'><rect x='50' y='60' width='200' height='120' rx='2'/><line x1='50' y1='80' x2='250' y2='80'/><line x1='50' y1='100' x2='250' y2='100'/><line x1='50' y1='140' x2='250' y2='140'/><line x1='75' y1='60' x2='75' y2='180'/><line x1='105' y1='60' x2='105' y2='180'/><line x1='135' y1='60' x2='135' y2='180'/><line x1='165' y1='60' x2='165' y2='180'/><line x1='195' y1='60' x2='195' y2='180'/><line x1='225' y1='60' x2='225' y2='180'/><path d='M 135 140 A 15 15 0 0 1 165 140 Z' fill='%23E2B3B7'/></g><text x='150' y='225' fill='%23E2B3B7' font-family='Georgia, serif' font-size='30' font-weight='bold' text-anchor='middle' letter-spacing='2'>SANCHEZ</text><text x='150' y='265' fill='%23E2B3B7' font-family='Georgia, serif' font-size='30' font-weight='bold' text-anchor='middle' letter-spacing='2'>AGUILAR</text></svg>"

LOGO_SWEET = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'><rect width='300' height='300' fill='%230E542C'/><text x='150' y='105' fill='%23FFFFFF' font-family='Georgia, serif' font-size='52' font-style='italic' font-weight='bold' text-anchor='middle'>Sweet</text><text x='150' y='175' fill='%23FFFFFF' font-family='Georgia, serif' font-size='58' font-style='italic' text-anchor='middle'>&amp;</text><text x='150' y='240' fill='%23FFFFFF' font-family='Georgia, serif' font-size='52' font-style='italic' font-weight='bold' text-anchor='middle'>Coffee</text></svg>"

LOGO_UG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 250'><rect width='300' height='250' fill='%23FFFFFF'/><g font-family='Arial, sans-serif' font-weight='900'><path d='M 35 40 L 80 40 L 80 140 C 80 175 110 175 110 140 L 110 40 L 155 40 L 155 140 C 155 210 35 210 35 140 Z' fill='%2300A3E0'/><path d='M 135 125 C 135 50 215 50 255 80 L 220 112 C 200 95 178 95 178 125 C 178 155 205 155 220 140 L 195 140 L 195 112 L 260 112 L 260 170 C 230 205 160 205 135 155 Z' fill='%23003366'/><path d='M 210 100 Q 235 80 250 65 Q 235 95 218 112 Z' fill='%2300A3E0'/></g></svg>"

# --------------------------------------------------------------------------
# BASE DE DATOS EN MEMORIA
# --------------------------------------------------------------------------

mes_actual_nombre = "Septiembre 2026"

ranking_mensual = [
    {
        "id": 1,
        "nombre": "Teatro Sánchez Aguilar",
        "monto": 5.00,
        "direccion": "Km 1.5 Av. Samborondón, Samborondón",
        "web": "https://www.teatrosanchezaguilar.org",
        "telefono": "",
        "redes_nombre": "",
        "redes_url": "",
        "logo_url": LOGO_TEATRO,
    },
    {
        "id": 2,
        "nombre": "Sweet & Coffee",
        "monto": 3.00,
        "direccion": "Puerto Santa Ana, Guayaquil",
        "web": "https://www.sweetandcoffee.com.ec",
        "telefono": "",
        "redes_nombre": "",
        "redes_url": "",
        "logo_url": LOGO_SWEET,
    },
    {
        "id": 3,
        "nombre": "Universidad de Guayaquil",
        "monto": 2.00,
        "direccion": "Av. Delta y Av. Kennedy, Guayaquil",
        "web": "https://www.ug.edu.ec",
        "telefono": "",
        "redes_nombre": "",
        "redes_url": "",
        "logo_url": LOGO_UG,
    },
]

top3_historico = [
    {
        "id": 101,
        "nombre": ranking_mensual[0]["nombre"],
        "monto": ranking_mensual[0]["monto"],
        "web": ranking_mensual[0]["web"],
        "telefono": ranking_mensual[0]["telefono"],
        "redes_nombre": ranking_mensual[0]["redes_nombre"],
        "redes_url": ranking_mensual[0]["redes_url"],
        "media_url": (
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80"
        ),
        "fecha": mes_actual_nombre,
    },
    {
        "id": 102,
        "nombre": ranking_mensual[1]["nombre"],
        "monto": ranking_mensual[1]["monto"],
        "web": ranking_mensual[1]["web"],
        "telefono": ranking_mensual[1]["telefono"],
        "redes_nombre": ranking_mensual[1]["redes_nombre"],
        "redes_url": ranking_mensual[1]["redes_url"],
        "media_url": (
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80"
        ),
        "fecha": mes_actual_nombre,
    },
    {
        "id": 103,
        "nombre": ranking_mensual[2]["nombre"],
        "monto": ranking_mensual[2]["monto"],
        "web": ranking_mensual[2]["web"],
        "telefono": ranking_mensual[2]["telefono"],
        "redes_nombre": ranking_mensual[2]["redes_nombre"],
        "redes_url": ranking_mensual[2]["redes_url"],
        "media_url": (
            "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80"
        ),
        "fecha": mes_actual_nombre,
    },
]


def formatear_telefono_wa(num):
  if not num:
    return ""
  num_clean = "".join(filter(str.isdigit, str(num)))
  if not num_clean:
    return ""
  if num_clean.startswith("0"):
    num_clean = "593" + num_clean[1:]
  elif not num_clean.startswith("593"):
    num_clean = "593" + num_clean
  return num_clean


def formatear_redes_url(redes):
  if not redes:
    return "", ""
  redes = redes.strip()
  if not redes:
    return "", ""
  if redes.startswith("http"):
    username = "@" + redes.rstrip("/").split("/")[-1]
    return username, redes
  username = redes if redes.startswith("@") else "@" + redes
  clean_user = username.replace("@", "")
  return username, f"https://www.instagram.com/{clean_user}"


def guardar_archivo(file_obj):
  if file_obj and file_obj.filename != "":
    filename = secure_filename(
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_obj.filename}"
    )
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_obj.save(filepath)
    return f"/static/uploads/{filename}"
  return ""


def actualizar_rankings(nuevo_registro):
  global top3_historico, ranking_mensual

  monto = nuevo_registro["monto"]
  redes_nombre, redes_url = formatear_redes_url(nuevo_registro.get("redes", ""))
  tel_wa = (
      formatear_telefono_wa(nuevo_registro.get("telefono", ""))
      if nuevo_registro.get("telefono")
      else ""
  )

  # 1. Actualizar Ránking Mensual (Top 50)
  existente = next(
      (
          item
          for item in ranking_mensual
          if item["nombre"].lower() == nuevo_registro["nombre"].lower()
      ),
      None,
  )

  if existente:
    existente["monto"] += monto
    if nuevo_registro.get("web"):
      existente["web"] = nuevo_registro["web"]
    if nuevo_registro.get("direccion"):
      existente["direccion"] = nuevo_registro["direccion"]
    if nuevo_registro.get("logo_url"):
      existente["logo_url"] = nuevo_registro["logo_url"]
    if tel_wa:
      existente["telefono"] = tel_wa
    if redes_url:
      existente["redes_nombre"] = redes_nombre
      existente["redes_url"] = redes_url
  else:
    ranking_mensual.append({
        "id": len(ranking_mensual) + 1,
        "nombre": nuevo_registro["nombre"],
        "monto": monto,
        "direccion": nuevo_registro.get("direccion", ""),
        "logo_url": nuevo_registro.get("logo_url", ""),
        "web": nuevo_registro.get("web", ""),
        "telefono": tel_wa,
        "redes_nombre": redes_nombre,
        "redes_url": redes_url,
    })

  ranking_mensual = sorted(
      ranking_mensual, key=lambda x: x["monto"], reverse=True
  )[:50]

  # 2. Evaluar ingreso automático al Top 3 Inmortal
  media_inmortal = nuevo_registro.get("media_url") or (
      nuevo_registro.get("logo_url")
      or "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80"
  )

  top3_historico.append({
      "id": len(top3_historico) + 100,
      "nombre": nuevo_registro["nombre"],
      "monto": monto,
      "web": nuevo_registro.get("web", ""),
      "telefono": tel_wa,
      "redes_nombre": redes_nombre,
      "redes_url": redes_url,
      "media_url": media_inmortal,
      "fecha": mes_actual_nombre,
  })

  top3_historico = sorted(
      top3_historico, key=lambda x: x["monto"], reverse=True
  )[:3]


# --------------------------------------------------------------------------
# PLANTILLA HTML CON DISEÑO "WOW", GLASSMORPHISM & SEO
# --------------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetroPuja.ec | Plataforma de Posicionamiento Comercial en Guayas</title>
    
    <!-- ================================================================= -->
    <!-- METADATOS SEO INVISIBLES PARA INDEXACIÓN AUTOMÁTICA EN GOOGLE     -->
    <!-- ================================================================= -->
    <meta name="description" content="MetroPuja.ec es la subasta interactiva de visibilidad web y posicionamiento comercial líder en Guayaquil, Samborondón, Daule y la provincia del Guayas. Destaca tu marca en el Top 50.">
    <meta name="keywords" content="MetroPuja, MetroPuja.ec, posicionamiento comercial Guayaquil, publicidad digital Guayas, marcas Samborondón, empresas Daule, subasta web Ecuador, directorio de empresas Guayaquil, publicidad marcas Guayas, SEO Ecuador">
    <meta name="author" content="MetroPuja.ec - @nobartys">
    <meta name="robots" content="index, follow">

    <!-- OPEN GRAPH FOR SOCIAL MEDIA PREVIEWS (WHATSAPP, FACEBOOK) -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="MetroPuja.ec | Lidera la Visibilidad de Marcas en Guayas">
    <meta property="og:description" content="Posiciona tu negocio en el Puesto #1 del ránking mensual de la provincia del Guayas.">
    <meta property="og:url" content="https://metropuja.ec/">
    <meta property="og:site_name" content="MetroPuja.ec">

    <!-- ESTRUCTURA SCHEMA JSON-LD (GOOGLE SEARCH KNOWLEDGE GRAPH) -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "MetroPuja.ec",
      "url": "https://metropuja.ec/",
      "description": "Plataforma de posicionamiento y subasta de tráfico comercial para empresas en la Provincia del Guayas.",
      "publisher": {
        "@type": "Organization",
        "name": "MetroPuja.ec",
        "url": "https://metropuja.ec/"
      },
      "areaServed": {
        "@type": "AdministrativeArea",
        "name": "Guayas, Ecuador"
      }
    }
    </script>

    <!-- ESTILOS Y FUENTES PREMIUM -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    
    <style>
        body { 
            font-family: 'Outfit', sans-serif; 
            background-color: #030712;
        }

        /* ANIMACIONES AMBIENTALES DE ALTA FLUIDEZ */
        @keyframes orbDrift1 {
            0%, 100% { transform: translate(0px, 0px) scale(1); }
            50% { transform: translate(60px, 40px) scale(1.15); }
        }
        @keyframes orbDrift2 {
            0%, 100% { transform: translate(0px, 0px) scale(1); }
            50% { transform: translate(-50px, -30px) scale(1.2); }
        }
        @keyframes borderGlow {
            0%, 100% { border-color: rgba(16, 185, 129, 0.25); box-shadow: 0 0 15px rgba(16, 185, 129, 0.1); }
            50% { border-color: rgba(16, 185, 129, 0.6); box-shadow: 0 0 30px rgba(16, 185, 129, 0.25); }
        }

        .animate-orb-1 { animation: orbDrift1 14s ease-in-out infinite; }
        .animate-orb-2 { animation: orbDrift2 18s ease-in-out infinite; }
        .glow-card { animation: borderGlow 5s infinite; }

        /* MESH PATTERN DE FONDO */
        .bg-grid-pattern {
            background-image: radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px);
            background-size: 24px 24px;
        }

        /* DRAG & DROP ACTIVE STYLES */
        .dropzone-active {
            border-color: #10b981 !important;
            background-color: rgba(16, 185, 129, 0.1) !important;
        }
    </style>
</head>
<body class="text-slate-100 min-h-screen relative overflow-x-hidden bg-grid-pattern selection:bg-emerald-500 selection:text-slate-950">

    <!-- LUCES NEÓN DE FONDO (LUZ DINÁMICA FLUIDA) -->
    <div class="fixed top-[-100px] left-1/2 -translate-x-1/2 -z-10 w-[800px] h-[500px] bg-emerald-500/15 blur-[160px] rounded-full pointer-events-none animate-orb-1"></div>
    <div class="fixed bottom-[-100px] right-[-100px] -z-10 w-[600px] h-[400px] bg-cyan-500/10 blur-[150px] rounded-full pointer-events-none animate-orb-2"></div>
    <div class="fixed top-[40%] left-[-150px] -z-10 w-[500px] h-[500px] bg-amber-500/10 blur-[170px] rounded-full pointer-events-none"></div>

    <!-- NAVBAR CRISTALINO -->
    <header class="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-50 transition-all shadow-2xl">
        <div class="max-w-5xl mx-auto px-4 py-3.5 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="relative group">
                    <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
                    <div class="relative bg-slate-950 text-emerald-400 font-black text-xl px-3.5 py-1 rounded-xl">MP</div>
                </div>
                <div>
                    <h1 class="font-black text-xl tracking-tight text-white flex items-center gap-1">
                        MetroPuja<span class="text-emerald-400">.ec</span>
                    </h1>
                    <p class="text-[11px] text-slate-400 font-medium tracking-wide">Exclusivo Guayas • Guayaquil • Samborondón • Daule</p>
                </div>
            </div>

            <a href="#participar" class="relative group">
                <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-teal-400 rounded-xl blur opacity-70 group-hover:opacity-100 transition duration-300"></div>
                <span class="relative bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-extrabold text-xs px-5 py-2.5 rounded-xl transition-all flex items-center gap-2 shadow-lg">
                    <i class="fa-solid fa-bolt text-slate-950 animate-pulse"></i> Pujar Mi Marca
                </span>
            </a>
        </div>
    </header>

    <!-- NOTIFICACIÓN DE PUJA EXITOSA -->
    {% if msg %}
    <div class="max-w-5xl mx-auto px-4 pt-6">
        <div class="bg-emerald-950/80 border border-emerald-500/60 text-emerald-200 px-5 py-3.5 rounded-2xl flex items-center gap-3 text-sm shadow-2xl backdrop-blur-md animate-fade-in">
            <i class="fa-solid fa-circle-check text-emerald-400 text-xl animate-bounce"></i>
            <span class="font-semibold">{{ msg }}</span>
        </div>
    </div>
    {% endif %}

    <main class="max-w-5xl mx-auto px-4 py-8 space-y-10">

        <!-- HERO BANNER INTERACTIVO CON GLASSMORPHISM -->
        <section>
            <div class="relative bg-slate-900/60 border border-slate-800 rounded-3xl p-7 md:p-10 backdrop-blur-2xl shadow-2xl overflow-hidden glow-card">
                <div class="absolute -right-12 -top-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                
                <div class="max-w-2xl relative z-10 space-y-4">
                    <div class="inline-flex items-center gap-2 bg-emerald-950/80 border border-emerald-500/40 px-3.5 py-1 rounded-full text-[11px] font-bold text-emerald-300 tracking-wider uppercase shadow-inner">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> SUBASTA EN VIVO • GUAYAS
                    </div>

                    <h2 class="text-3xl md:text-5xl font-black text-white leading-tight tracking-tight">
                        Puja para posicionar tu Marca en el <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">Puesto #1</span>.
                    </h2>

                    <p class="text-slate-300 text-sm md:text-base leading-relaxed">
                        Las empresas y proyectos con mayor valor acumulado ocupan la cima del ranking comercial, captando la atención directa de clientes en la provincia del Guayas.
                    </p>
                </div>
            </div>
        </section>

        <!-- AVISO DE REINICIO MENSUAL -->
        <div class="bg-amber-950/30 border border-amber-500/30 rounded-2xl p-4 flex items-start gap-4 backdrop-blur-md hover:border-amber-500/50 transition-colors shadow-lg">
            <div class="bg-amber-500/20 text-amber-400 p-2.5 rounded-xl flex-shrink-0 text-lg">
                <i class="fa-solid fa-rotate-left"></i>
            </div>
            <div class="text-xs leading-relaxed space-y-0.5">
                <strong class="text-amber-300 text-sm font-bold block">Tablas Restablecidas Cada 1° de Mes</strong>
                <p class="text-slate-300">
                    Para garantizar igualdad de oportunidades a nuevos emprendimientos de Guayaquil, Samborondón y Daule, las pujas mensuales inician en $0.00 al comenzar cada mes.
                </p>
            </div>
        </div>

        <!-- SECCIÓN 1: RÁNKING INMORTAL (TOP 3 HISTÓRICO) -->
        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <div>
                    <span class="bg-amber-500/10 text-amber-400 font-bold text-[11px] uppercase tracking-widest px-3 py-1 rounded-lg border border-amber-500/30 shadow-sm inline-block mb-1">
                        <i class="fa-solid fa-crown mr-1"></i> Ránking Inmortal
                    </span>
                    <h3 class="text-2xl md:text-3xl font-black text-white">Top 3 Histórico de Todos los Tiempos</h3>
                </div>
                <span class="text-xs text-slate-400 bg-slate-900/80 px-3.5 py-1.5 rounded-xl border border-slate-800 hidden md:inline-flex items-center gap-1.5 shadow-inner">
                    <i class="fa-solid fa-infinity text-amber-400"></i> Récords Permanentes
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {% for h in top3 %}
                <div class="group relative bg-slate-900/60 border border-amber-500/30 hover:border-amber-400/80 rounded-3xl overflow-hidden shadow-2xl flex flex-col justify-between transition-all duration-300 hover:-translate-y-2 hover:shadow-amber-500/10 backdrop-blur-xl">
                    
                    <div class="absolute top-3 left-3 z-20">
                        {% if loop.index == 1 %}
                            <span class="bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 font-black text-[11px] px-3.5 py-1 rounded-full shadow-lg flex items-center gap-1.5">
                                <i class="fa-solid fa-trophy"></i> #1 INMORTAL
                            </span>
                        {% elif loop.index == 2 %}
                            <span class="bg-slate-200 text-slate-950 font-black text-[11px] px-3.5 py-1 rounded-full shadow-lg">
                                #2 INMORTAL
                            </span>
                        {% else %}
                            <span class="bg-amber-800 text-white font-black text-[11px] px-3.5 py-1 rounded-full shadow-lg">
                                #3 INMORTAL
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
                            <div class="text-3xl font-black text-emerald-400 tracking-tight">${{ "%.2f"|format(h.monto) }} <span class="text-xs text-slate-400 font-normal">USD</span></div>

                            <div class="space-y-2 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
                                {% if h.web %}
                                <p class="truncate flex items-center gap-2">
                                    <i class="fa-solid fa-globe text-emerald-400"></i>
                                    <a href="{{ h.web }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-medium">
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
                                    <i class="fa-solid fa-at text-emerald-400"></i>
                                    <a href="{{ h.redes_url }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-medium">
                                        {{ h.redes_nombre }}
                                    </a>
                                </p>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="p-4 bg-slate-950/90 border-t border-slate-800/80 text-[11px] text-slate-400 flex justify-between items-center">
                        <span>Récord registrado:</span>
                        <strong class="text-slate-300 font-semibold">{{ h.fecha }}</strong>
                    </div>

                </div>
                {% endfor %}
            </div>
        </section>

        <!-- SECCIÓN 2: TOP 50 MENSUAL VERTICAL -->
        <section class="space-y-6">
            <div class="flex items-center justify-between">
                <div>
                    <span class="bg-emerald-500/10 text-emerald-400 font-bold text-[11px] uppercase tracking-widest px-3 py-1 rounded-lg border border-emerald-500/30 shadow-sm inline-block mb-1">
                        <i class="fa-solid fa-calendar-days mr-1"></i> Ciclo {{ mes_actual }}
                    </span>
                    <h3 class="text-2xl md:text-3xl font-black text-white">Top 50 Mensual (Provincia del Guayas)</h3>
                </div>

                <form action="/admin/reiniciar-mes" method="POST">
                    <button type="submit" onclick="return confirm('¿Deseas reiniciar las pujas de este mes?')" class="text-xs text-slate-400 hover:text-rose-400 bg-slate-900/80 px-3.5 py-2 rounded-xl border border-slate-800 transition-colors shadow-sm">
                        <i class="fa-solid fa-rotate-left mr-1"></i> Reiniciar
                    </button>
                </form>
            </div>

            <div class="space-y-3.5">
                {% for m in mensual %}
                <div class="group bg-slate-900/50 border border-slate-800/90 hover:border-emerald-500/50 rounded-2xl p-4 transition-all duration-300 hover:bg-slate-900/80 hover:shadow-xl hover:shadow-emerald-500/5 flex flex-col md:flex-row md:items-center justify-between gap-4 backdrop-blur-xl">
                    
                    <div class="flex items-center gap-4">
                        <!-- CONTENEDOR DE LOGOTIPO -->
                        <div class="relative flex-shrink-0">
                            <div class="w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 p-0.5 flex items-center justify-center shadow-lg overflow-hidden group-hover:border-emerald-500/40 transition-colors">
                                {% if m.logo_url %}
                                <img src="{{ m.logo_url }}" alt="" class="w-full h-full object-cover rounded-xl">
                                {% else %}
                                <i class="fa-solid fa-building text-slate-600 text-xl"></i>
                                {% endif %}
                            </div>
                            <span class="absolute -top-2 -right-2 bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-lg shadow-lg border border-emerald-300">
                                #{{ loop.index }}
                            </span>
                        </div>

                        <div class="space-y-0.5">
                            <h4 class="font-bold text-white text-lg group-hover:text-emerald-300 transition-colors">
                                {{ m.nombre }}
                            </h4>

                            {% if m.direccion %}
                            <p class="text-xs text-slate-400 flex items-center gap-1.5">
                                <i class="fa-solid fa-location-dot text-emerald-400 text-[10px]"></i> {{ m.direccion }}
                            </p>
                            {% endif %}
                            
                            <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 pt-1">
                                {% if m.web %}
                                <a href="{{ m.web }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold">
                                    <i class="fa-solid fa-link text-[10px]"></i> {{ m.web.replace('https://', '').replace('http://', '').replace('www.', '') }}
                                </a>
                                {% endif %}

                                {% if m.telefono %}
                                <a href="https://wa.me/{{ m.telefono }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold">
                                    <i class="fa-brands fa-whatsapp text-[11px]"></i> WhatsApp
                                </a>
                                {% endif %}

                                {% if m.redes_url %}
                                <a href="{{ m.redes_url }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold">
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
                    No hay pujas registradas este mes aún. ¡Sé el primero en posicionarte en Guayas!
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- SECCIÓN 3: FORMULARIO DE PUJA CON ZONAS DRAG & DROP DINÁMICAS -->
        <section id="participar" class="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-10 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
            <div class="absolute top-0 right-0 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

            <div class="mb-8 space-y-1">
                <h3 class="text-2xl font-black text-white flex items-center gap-2">
                    <i class="fa-solid fa-paper-plane text-emerald-400"></i> Formulario de Posicionamiento (Guayas)
                </h3>
                <p class="text-xs text-slate-400">Tu puja te posicionará en el **Top 50 Mensual**. Si tu monto supera un récord histórico, ingresarás automáticamente al **Top 3 Inmortal**.</p>
            </div>

            <form action="/pujar" method="POST" enctype="multipart/form-data" class="grid grid-cols-1 md:grid-cols-2 gap-5">
                
                <div class="md:col-span-2">
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Nombre de la Persona / Empresa / Marca *</label>
                    <input type="text" name="nombre" placeholder="Ej: Mi Negocio Guayaquil / Samborondón" required 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Dirección <span class="text-emerald-400 font-normal text-[11px]">(Ránking Mensual - Opcional)</span></label>
                    <input type="text" name="direccion" placeholder="Ej: Puerto Santa Ana, Edificio Torre 1, Guayaquil" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Página Web <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="url" name="web" placeholder="https://miweb.com" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Número de Contacto / WhatsApp <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="text" name="telefono" placeholder="Ej: 0991234567" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Redes Sociales <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <input type="text" name="redes" placeholder="Ej: @minegociogye o enlace de Instagram" 
                           class="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                </div>

                <!-- SUBIDA DE LOGO CON DRAG & DROP INTERACTIVO -->
                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Logotipo de la Empresa <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <div id="dropzone-logo" class="relative border-2 border-dashed border-slate-800 hover:border-emerald-500 rounded-2xl p-4 text-center bg-slate-950/60 transition-all duration-300 cursor-pointer group">
                        <input type="file" name="logo_file" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                               onchange="handleFileSelect(this, 'logo-text', 'logo-icon')">
                        <i id="logo-icon" class="fa-solid fa-image text-slate-500 group-hover:text-emerald-400 text-xl mb-1.5 block transition-colors"></i>
                        <span id="logo-text" class="text-xs text-slate-400 block truncate font-medium">Haz clic o arrastra tu logo aquí</span>
                    </div>
                </div>

                <!-- SUBIDA DE FOTO / VIDEO CON DRAG & DROP INTERACTIVO -->
                <div>
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Subir Foto o Video <span class="text-slate-500 font-normal text-[11px]">(Opcional)</span></label>
                    <div id="dropzone-media" class="relative border-2 border-dashed border-slate-800 hover:border-amber-500 rounded-2xl p-4 text-center bg-slate-950/60 transition-all duration-300 cursor-pointer group">
                        <input type="file" name="media_file" accept="image/*,video/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                               onchange="handleFileSelect(this, 'media-text', 'media-icon')">
                        <i id="media-icon" class="fa-solid fa-cloud-arrow-up text-slate-500 group-hover:text-amber-400 text-xl mb-1.5 block transition-colors"></i>
                        <span id="media-text" class="text-xs text-slate-400 block truncate font-medium">Haz clic o arrastra tu foto o video aquí</span>
                    </div>
                </div>

                <div class="md:col-span-2 pt-3">
                    <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Monto a Pujar ($ USD) *</label>
                    <div class="flex gap-3">
                        <div class="relative flex-1">
                            <span class="absolute left-4 top-3 text-sm font-bold text-slate-500">$</span>
                            <input type="number" name="monto" min="1" step="1" placeholder="Ej: 2.00" required 
                                   class="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-8 pr-4 py-3 text-base text-white font-black focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all">
                        </div>
                        <button type="submit" class="bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-black px-8 py-3 rounded-xl text-xs uppercase tracking-wider transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-400/40 hover:scale-[1.02]">
                            <i class="fa-solid fa-bolt mr-1"></i> Confirmar Puja
                        </button>
                    </div>
                </div>

            </form>
        </section>

    </main>

    <!-- FOOTER ELEGANTE Y COMPLETO -->
    <footer class="border-t border-slate-800/80 bg-slate-950/90 backdrop-blur-xl py-10 text-center text-xs text-slate-500 space-y-2 mt-12">
        <p>© 2026 MetroPuja.ec — Plataforma de Posicionamiento Competitivo Exclusiva para la Provincia del Guayas.</p>
        <p class="text-slate-400 font-medium">
            Creado por <a href="https://www.instagram.com/nobartys/" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline font-bold inline-flex items-center gap-1"><i class="fa-brands fa-instagram"></i> @nobartys</a>
        </p>
        <p class="text-slate-400">Soporte Técnico: <a href="mailto:nobartysinformacion@gmail.com" class="text-emerald-400 hover:underline font-bold">nobartysinformacion@gmail.com</a></p>
        <p class="text-[10px] text-slate-600 pt-3 max-w-xl mx-auto px-4 leading-relaxed">Las marcas y logotipos exhibidos en la plataforma de prueba pertenecen a sus respectivos titulares. Si eres representante legal de alguna marca y deseas gestionar o retirar tu perfil, contáctanos vía soporte técnico.</p>
    </footer>

    <!-- SCRIPT DE INTERACCIÓN DRAG & DROP FLUIDO -->
    <script>
        function handleFileSelect(input, textId, iconId) {
            const textElem = document.getElementById(textId);
            const iconElem = document.getElementById(iconId);
            if (input.files && input.files[0]) {
                textElem.innerText = "✓ " + input.files[0].name;
                textElem.classList.add("text-emerald-400", "font-bold");
                iconElem.classList.add("text-emerald-400");
            }
        }

        // Efectos visuales de Arrastrar Archivo por encima de la zona de carga
        ['dropzone-logo', 'dropzone-media'].forEach(id => {
            const zone = document.getElementById(id);
            if(zone) {
                zone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    zone.classList.add('dropzone-active');
                });
                zone.addEventListener('dragleave', () => {
                    zone.classList.remove('dropzone-active');
                });
                zone.addEventListener('drop', () => {
                    zone.classList.remove('dropzone-active');
                });
            }
        });
    </script>

</body>
</html>
"""


# --------------------------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# --------------------------------------------------------------------------


@app.route("/")
def index():
  msg = request.args.get("msg", "")
  return render_template_string(
      HTML_TEMPLATE,
      top3=top3_historico,
      mensual=ranking_mensual,
      mes_actual=mes_actual_nombre,
      msg=msg,
  )


@app.route("/pujar", methods=["POST"])
def pujar():
  try:
    nombre = request.form.get("nombre", "").strip()
    direccion = request.form.get("direccion", "").strip()
    web = request.form.get("web", "").strip()
    telefono = request.form.get("telefono", "").strip()
    redes = request.form.get("redes", "").strip()
    monto = float(request.form.get("monto", 0))

    # Guardar archivos subidos
    logo_file = request.files.get("logo_file")
    media_file = request.files.get("media_file")

    logo_url = guardar_archivo(logo_file) if logo_file else ""
    media_url = guardar_archivo(media_file) if media_file else ""

    if nombre and monto > 0:
      nuevo_registro = {
          "nombre": nombre,
          "direccion": direccion,
          "web": web,
          "telefono": telefono,
          "redes": redes,
          "logo_url": logo_url,
          "media_url": media_url,
          "monto": monto,
      }

      actualizar_rankings(nuevo_registro)

      return redirect(
          url_for(
              "index",
              msg=(
                  f"¡Puja de ${monto:.2f} USD registrada exitosamente para"
                  f" {nombre}!"
              ),
          )
      )

  except Exception as e:
    print(f"Error registrando puja: {e}")

  return redirect(url_for("index"))


@app.route("/admin/reiniciar-mes", methods=["POST"])
def reiniciar_mes():
  global ranking_mensual
  ranking_mensual = []
  return redirect(
      url_for(
          "index",
          msg=(
              "¡El Ránking Mensual de Guayas se ha reiniciado a $0 para el"
              " nuevo ciclo!"
          ),
      )
  )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)
