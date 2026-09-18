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
# LOGOTIPOS EMBEBIDOS (DATA URIs VECTORIALES EXACTOS)
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
# PLANTILLA HTML INTEGRADA CON FOOTER CON CREDITO A INSTAGRAM
# --------------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetroPuja.ec | Ránking Exclusivo Guayas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black relative overflow-x-hidden">

    <!-- RESPLANDOR AMBIENTAL DE FONDO -->
    <div class="fixed top-0 left-1/2 -translate-x-1/2 -z-10 w-[900px] h-[400px] bg-emerald-500/10 blur-[140px] rounded-full pointer-events-none"></div>

    <!-- Header Navigation -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="bg-gradient-to-tr from-emerald-600 to-emerald-400 text-slate-950 font-black text-xl px-3 py-1 rounded-lg shadow-lg shadow-emerald-500/20">MP</div>
                <div>
                    <h1 class="font-extrabold text-xl tracking-tight text-white">MetroPuja<span class="text-emerald-400">.ec</span></h1>
                    <p class="text-xs text-slate-400">Exclusivo Guayas • Guayaquil • Samborondón • Daule</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="#participar" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs px-4 py-2 rounded-lg transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-500/20">
                    <i class="fa-solid fa-bolt"></i> Pujar Mi Marca
                </a>
            </div>
        </div>
    </header>

    <!-- Banner Notificación -->
    {% if msg %}
    <div class="max-w-5xl mx-auto px-4 pt-4">
        <div class="bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 px-4 py-3 rounded-xl flex items-center gap-3 text-sm">
            <i class="fa-solid fa-circle-check text-emerald-400 text-lg"></i>
            <span>{{ msg }}</span>
        </div>
    </div>
    {% endif %}

    <main class="max-w-5xl mx-auto px-4 py-8 space-y-8">

        <!-- HERO BANNER -->
        <section>
            <div class="bg-gradient-to-r from-emerald-900/30 via-slate-900/90 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 md:p-8 relative overflow-hidden backdrop-blur-sm shadow-2xl">
                <div class="max-w-2xl">
                    <span class="text-emerald-400 font-bold text-xs uppercase tracking-widest bg-emerald-950/80 px-3 py-1 rounded-md border border-emerald-800/80">
                        SUBASTA DE TRÁFICO & VISIBILIDAD
                    </span>
                    <h2 class="text-3xl md:text-4xl font-extrabold text-white mt-3 leading-tight">
                        Puja para posicionar tu Sitio Web o Marca en el <span class="text-emerald-400">Puesto #1</span>.
                    </h2>
                    <p class="text-slate-300 text-sm mt-3 leading-relaxed">
                        Las marcas y proyectos con mayor valor acumulado ocupan los primeros lugares de la lista vertical y reciben la mayor atención de los visitantes.
                    </p>
                </div>
            </div>
        </section>

        <!-- ADVERTENCIA DE REINICIO MENSUAL -->
        <div class="bg-amber-950/40 border border-amber-500/40 rounded-xl p-4 flex items-start gap-3.5 backdrop-blur-sm">
            <div class="bg-amber-500/20 text-amber-400 p-2 rounded-lg flex-shrink-0 text-lg">
                <i class="fa-solid fa-triangle-exclamation"></i>
            </div>
            <div class="text-xs leading-relaxed">
                <strong class="text-amber-300 text-sm block mb-0.5">Valores de Pujas Restablecidos Mensualmente</strong>
                <span class="text-slate-300">
                    Para garantizar igualdad de oportunidades a emprendimientos y pequeños negocios de Guayas, la tabla mensual inicia en $0.00 cada 1° de mes. ¡Todos tienen la oportunidad de liderar el mercado local!
                </span>
            </div>
        </div>

        <!-- SECCIÓN 1: SALÓN DE LA FAMA (TOP 3 HISTÓRICO INMORTAL) -->
        <section>
            <div class="flex items-center justify-between mb-6">
                <div>
                    <span class="text-amber-400 font-bold text-xs uppercase tracking-widest bg-amber-950/80 px-3 py-1 rounded-md border border-amber-800">
                        <i class="fa-solid fa-crown mr-1"></i> Ránking Inmortal Guayas
                    </span>
                    <h2 class="text-2xl font-extrabold text-white mt-2">Top 3 Histórico de Todos los Tiempos</h2>
                </div>
                <span class="text-xs text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 hidden md:inline-block">
                    <i class="fa-solid fa-infinity text-amber-400 mr-1"></i> Récords Permanentes
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {% for h in top3 %}
                <div class="bg-slate-900/80 border border-amber-500/40 rounded-2xl overflow-hidden shadow-xl flex flex-col justify-between relative group hover:border-amber-400 transition-all backdrop-blur-sm">
                    <div class="absolute top-3 left-3 z-10">
                        {% if loop.index == 1 %}
                            <span class="bg-amber-500 text-slate-950 font-black text-xs px-3 py-1 rounded-full shadow-lg flex items-center gap-1">
                                <i class="fa-solid fa-trophy"></i> #1 HISTÓRICO
                            </span>
                        {% elif loop.index == 2 %}
                            <span class="bg-slate-300 text-slate-950 font-black text-xs px-3 py-1 rounded-full shadow-lg">
                                #2 HISTÓRICO
                            </span>
                        {% else %}
                            <span class="bg-amber-700 text-white font-black text-xs px-3 py-1 rounded-full shadow-lg">
                                #3 HISTÓRICO
                            </span>
                        {% endif %}
                    </div>

                    <div>
                        {% if h.media_url %}
                        <div class="h-44 overflow-hidden relative bg-slate-950 flex items-center justify-center">
                            {% if h.media_url.endswith(('.mp4', '.webm', '.ogg')) %}
                            <video src="{{ h.media_url }}" controls class="w-full h-full object-cover"></video>
                            {% else %}
                            <img src="{{ h.media_url }}" alt="" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
                            {% endif %}
                            <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent"></div>
                        </div>
                        {% endif %}

                        <div class="p-5">
                            <h3 class="text-lg font-bold text-white mb-1">{{ h.nombre }}</h3>
                            <div class="text-2xl font-black text-emerald-400 mb-3">${{ "%.2f"|format(h.monto) }} <span class="text-xs text-slate-400 font-normal">USD</span></div>

                            <div class="space-y-2 text-xs text-slate-300 border-t border-slate-800 pt-3">
                                {% if h.web %}
                                <p class="truncate">
                                    <i class="fa-solid fa-globe text-emerald-400 w-4"></i> 
                                    <a href="{{ h.web }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-semibold">
                                        {{ h.web.replace('https://', '').replace('http://', '').replace('www.', '') }}
                                    </a>
                                </p>
                                {% endif %}

                                {% if h.telefono %}
                                <p>
                                    <i class="fa-brands fa-whatsapp text-emerald-400 w-4"></i> 
                                    <a href="https://wa.me/{{ h.telefono }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-semibold">
                                        WhatsApp (+{{ h.telefono }})
                                    </a>
                                </p>
                                {% endif %}

                                {% if h.redes_url %}
                                <p>
                                    <i class="fa-solid fa-at text-emerald-400 w-4"></i> 
                                    <a href="{{ h.redes_url }}" target="_blank" rel="noopener noreferrer" class="hover:underline text-emerald-300 font-semibold">
                                        {{ h.redes_nombre }}
                                    </a>
                                </p>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="p-4 bg-slate-950/80 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between items-center">
                        <span>Récord registrado:</span>
                        <strong class="text-slate-300">{{ h.fecha }}</strong>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>


        <!-- SECCIÓN 2: RÁNKING MENSUAL (TOP 50 VERTICAL GUAYAS) -->
        <section>
            <div class="flex items-center justify-between mb-4">
                <div>
                    <span class="text-emerald-400 font-bold text-xs uppercase tracking-widest bg-emerald-950/80 px-3 py-1 rounded-md border border-emerald-800">
                        <i class="fa-solid fa-calendar-days mr-1"></i> Ránking {{ mes_actual }}
                    </span>
                    <h2 class="text-2xl font-extrabold text-white mt-2">Top 50 Mensual (Provincia del Guayas)</h2>
                </div>

                <form action="/admin/reiniciar-mes" method="POST">
                    <button type="submit" onclick="return confirm('¿Deseas simular el reinicio mensual de pujas?')" class="text-xs text-slate-400 hover:text-rose-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors">
                        <i class="fa-solid fa-rotate-left mr-1"></i> Reiniciar Mes
                    </button>
                </form>
            </div>

            <div class="space-y-3">
                {% for m in mensual %}
                <div class="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 transition-all hover:border-emerald-500/50 flex flex-col md:flex-row md:items-center justify-between gap-4 backdrop-blur-sm shadow-md">
                    
                    <div class="flex items-center gap-4">
                        <!-- CAJA DE LOGO VECTORIAL -->
                        <div class="relative flex-shrink-0">
                            <div class="w-12 h-12 rounded-xl bg-slate-950 border border-slate-700/80 p-0.5 flex items-center justify-center shadow-md overflow-hidden">
                                {% if m.logo_url %}
                                <img src="{{ m.logo_url }}" alt="" class="w-full h-full object-cover rounded-lg">
                                {% else %}
                                <i class="fa-solid fa-building text-slate-500 text-lg"></i>
                                {% endif %}
                            </div>
                            <span class="absolute -top-1.5 -right-1.5 bg-emerald-500 text-slate-950 text-[10px] font-black px-1.5 py-0.2 rounded-md shadow border border-emerald-400">
                                #{{ loop.index }}
                            </span>
                        </div>

                        <div>
                            <h4 class="font-bold text-white text-base flex items-center gap-2">
                                {{ m.nombre }}
                            </h4>

                            {% if m.direccion %}
                            <p class="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                                <i class="fa-solid fa-location-dot text-emerald-400 text-[10px]"></i> {{ m.direccion }}
                            </p>
                            {% endif %}
                            
                            <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
                                {% if m.web %}
                                <a href="{{ m.web }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-medium">
                                    <i class="fa-solid fa-link text-[10px]"></i> {{ m.web.replace('https://', '').replace('http://', '').replace('www.', '') }}
                                </a>
                                {% endif %}

                                {% if m.telefono %}
                                <a href="https://wa.me/{{ m.telefono }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-medium">
                                    <i class="fa-brands fa-whatsapp text-[11px]"></i> WhatsApp
                                </a>
                                {% endif %}

                                {% if m.redes_url %}
                                <a href="{{ m.redes_url }}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline flex items-center gap-1 font-medium">
                                    <i class="fa-solid fa-at text-[10px]"></i> {{ m.redes_nombre }}
                                </a>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center justify-between md:justify-end gap-4 border-t md:border-t-0 border-slate-800/80 pt-2 md:pt-0">
                        <span class="text-xl font-black text-emerald-400">${{ "%.2f"|format(m.monto) }} <span class="text-xs text-slate-400 font-normal">USD</span></span>
                    </div>

                </div>
                {% else %}
                <div class="text-center py-8 bg-slate-900/40 border border-slate-800 rounded-xl text-slate-400 text-sm">
                    No hay pujas registradas este mes aún. ¡Sé el primero en posicionarte en Guayas!
                </div>
                {% endfor %}
            </div>
        </section>


        <!-- SECCIÓN 3: FORMULARIO DE PUJA CON ZONA DRAG & DROP -->
        <section id="participar" class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
            <h3 class="text-xl font-bold text-white mb-1 flex items-center gap-2">
                <i class="fa-solid fa-paper-plane text-emerald-400"></i> Formulario de Posicionamiento (Guayas)
            </h3>
            <p class="text-xs text-slate-400 mb-6">Tu puja te posicionará en el **Top 50 Mensual**. Si tu monto supera un récord histórico, ingresarás automáticamente al **Top 3 Inmortal**.</p>

            <form action="/pujar" method="POST" enctype="multipart/form-data" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <div class="md:col-span-2">
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Nombre de la Persona / Empresa / Marca *</label>
                    <input type="text" name="nombre" placeholder="Ej: Mi Negocio Guayaquil / Samborondón" required 
                           class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Dirección <span class="text-emerald-400 font-normal">(Ránking Mensual - Opcional)</span></label>
                    <input type="text" name="direccion" placeholder="Ej: Puerto Santa Ana, Edificio Torre 1, Guayaquil" 
                           class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Página Web <span class="text-slate-500 font-normal">(Opcional)</span></label>
                    <input type="url" name="web" placeholder="https://miweb.com" 
                           class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Número de Contacto / WhatsApp <span class="text-slate-500 font-normal">(Opcional)</span></label>
                    <input type="text" name="telefono" placeholder="Ej: 0991234567" 
                           class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Redes Sociales <span class="text-slate-500 font-normal">(Opcional)</span></label>
                    <input type="text" name="redes" placeholder="Ej: @minegociogye o enlace de Instagram" 
                           class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500">
                </div>

                <!-- SUBIDA DE LOGO -->
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Logotipo de la Empresa <span class="text-slate-500 font-normal">(Opcional)</span></label>
                    <div class="relative border-2 border-dashed border-slate-800 hover:border-emerald-500 rounded-lg p-3 text-center bg-slate-950 transition-colors cursor-pointer group">
                        <input type="file" name="logo_file" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onchange="document.getElementById('logo-text').innerText = this.files[0] ? this.files[0].name : 'Haz clic o arrastra tu imagen aquí'">
                        <i class="fa-solid fa-image text-slate-400 group-hover:text-emerald-400 mb-1 block"></i>
                        <span id="logo-text" class="text-xs text-slate-400 block truncate">Haz clic o arrastra tu logo aquí</span>
                    </div>
                </div>

                <!-- SUBIDA DE FOTO / VIDEO -->
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Subir Foto o Video <span class="text-slate-500 font-normal">(Opcional)</span></label>
                    <div class="relative border-2 border-dashed border-slate-800 hover:border-amber-500 rounded-lg p-3 text-center bg-slate-950 transition-colors cursor-pointer group">
                        <input type="file" name="media_file" accept="image/*,video/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" onchange="document.getElementById('media-text').innerText = this.files[0] ? this.files[0].name : 'Haz clic o arrastra tu foto o video aquí'">
                        <i class="fa-solid fa-cloud-arrow-up text-slate-400 group-hover:text-amber-400 mb-1 block"></i>
                        <span id="media-text" class="text-xs text-slate-400 block truncate">Haz clic o arrastra tu foto o video aquí</span>
                    </div>
                </div>

                <div class="md:col-span-2 pt-2">
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Monto a Pujar ($ USD) *</label>
                    <div class="flex gap-3">
                        <div class="relative flex-1">
                            <span class="absolute left-3 top-2.5 text-xs text-slate-400">$</span>
                            <input type="number" name="monto" min="1" step="1" placeholder="Ej: 2.00" required 
                                   class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-7 pr-3 py-2.5 text-sm text-white font-bold focus:outline-none focus:border-emerald-500">
                        </div>
                        <button type="submit" class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-6 py-2.5 rounded-lg text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20">
                            <i class="fa-solid fa-bolt"></i> Confirmar Puja
                        </button>
                    </div>
                </div>

            </form>
        </section>

    </main>

    <!-- FOOTER CON CORREO DE SOPORTE Y CREDITO DE CREADOR -->
    <footer class="border-t border-slate-800/80 bg-slate-950 py-8 text-center text-xs text-slate-500 space-y-2">
        <p>© 2026 MetroPuja.ec — Plataforma de Posicionamiento Competitivo Exclusiva para la Provincia del Guayas.</p>
        <p class="text-slate-400">
            Creado por <a href="https://www.instagram.com/nobartys/" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline font-semibold"><i class="fa-brands fa-instagram mr-0.5"></i> @nobartys</a>
        </p>
        <p class="text-slate-400">Soporte Técnico: <a href="mailto:nobartysinformacion@gmail.com" class="text-emerald-400 hover:underline font-semibold">nobartysinformacion@gmail.com</a></p>
        <p class="text-[10px] text-slate-600 pt-2 max-w-xl mx-auto px-4">Las marcas y logotipos exhibidos en el entorno de demostración pertenecen a sus respectivos titulares de derechos. Si eres representante de una entidad y deseas gestionar o retirar tu presencia, contáctanos a soporte.</p>
    </footer>

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
