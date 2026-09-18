import json
import os
from urllib.parse import quote
from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import requests

app = Flask(__name__)

# Configuración de dLocal Go
DLOCALGO_API_KEY = os.environ.get("DLOCALGO_API_KEY", "TU_API_KEY_DLOCALGO_AQUI")
DLOCALGO_SECRET_KEY = os.environ.get(
    "DLOCALGO_SECRET_KEY", "TU_SECRET_KEY_DLOCALGO_AQUI"
)
DLOCALGO_BASE_URL = os.environ.get(
    "DLOCALGO_BASE_URL", "https://api-sbx.dlocalgo.com"
)

# Base de datos en memoria con Tabla de Posiciones Top 5 por Proyecto
proyectos = {
    1: {
        "id": 1,
        "nombre": "Suite Luxury Mocolí",
        "ubicacion": "Isla Mocolí, Samborondón",
        "descuento_voucher": 12000.00,
        "imagen": (
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80"
        ),
        "ranking": [
            {"puesto": 1, "nombre": "Carlos M.", "monto": 150.00},
            {"puesto": 2, "nombre": "Andrea V.", "monto": 110.00},
            {"puesto": 3, "nombre": "Roberto G.", "monto": 75.00},
            {"puesto": 4, "nombre": "Dome K.", "monto": 40.00},
            {"puesto": 5, "nombre": "Luis P.", "monto": 25.00},
        ],
    },
    2: {
        "id": 2,
        "nombre": "Depa Vista al Río - Torre Bellini",
        "ubicacion": "Puerto Santa Ana, Guayaquil",
        "descuento_voucher": 15000.00,
        "imagen": (
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
        ),
        "ranking": [
            {"puesto": 1, "nombre": "Valeria S.", "monto": 220.00},
            {"puesto": 2, "nombre": "Fernando C.", "monto": 180.00},
            {"puesto": 3, "nombre": "Xavier T.", "monto": 130.00},
            {"puesto": 4, "nombre": "Ma. José R.", "monto": 90.00},
            {"puesto": 5, "nombre": "Esteban B.", "monto": 50.00},
        ],
    },
    3: {
        "id": 3,
        "nombre": "Casa Modelo Premier",
        "ubicacion": "Vía a la Costa, Km 14",
        "descuento_voucher": 10000.00,
        "imagen": (
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"
        ),
        "ranking": [
            {"puesto": 1, "nombre": "Gabriel M.", "monto": 95.00},
            {"puesto": 2, "nombre": "Patricia L.", "monto": 70.00},
            {"puesto": 3, "nombre": "Daniel A.", "monto": 50.00},
            {"puesto": 4, "nombre": "Javier H.", "monto": 30.00},
            {"puesto": 5, "nombre": "Sofia V.", "monto": 15.00},
        ],
    },
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetroPuja.ec | Subastas Inmobiliarias en Guayas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

    <!-- Header Navigation -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="bg-emerald-500 text-slate-950 font-black text-xl px-3 py-1 rounded-lg">MP</div>
                <div>
                    <h1 class="font-extrabold text-xl tracking-tight text-white">MetroPuja<span class="text-emerald-400">.ec</span></h1>
                    <p class="text-xs text-slate-400">Guayaquil • Samborondón • Vía a la Costa</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <span class="bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> TABLA EN VIVO
                </span>
            </div>
        </div>
    </header>

    <!-- Banner Mensaje -->
    {% if msg %}
    <div class="max-w-7xl mx-auto px-4 pt-4">
        <div class="bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 px-4 py-3 rounded-xl flex items-center gap-3 text-sm">
            <i class="fa-solid fa-circle-check text-emerald-400 text-lg"></i>
            <span>{{ msg }}</span>
        </div>
    </div>
    {% endif %}

    <!-- Hero Banner -->
    <section class="max-w-7xl mx-auto px-4 py-8">
        <div class="bg-gradient-to-r from-emerald-900/40 via-slate-800 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 md:p-8 relative overflow-hidden">
            <div class="max-w-2xl">
                <span class="text-emerald-400 font-bold text-xs uppercase tracking-widest bg-emerald-950/80 px-3 py-1 rounded-md border border-emerald-800">
                    Subasta de Vouchers Inmobiliarios
                </span>
                <h2 class="text-3xl md:text-4xl font-extrabold text-white mt-3 leading-tight">
                    Puja el monto que desees y posicionate en el <span class="text-emerald-400">Puesto #1</span>.
                </h2>
                <p class="text-slate-300 text-sm mt-3 leading-relaxed">
                    Ingresa tu valor a pujar para desplazar a los competidores. Quien cierre en la posición #1 al finalizar el tiempo obtiene el Voucher de Descuento Oficial para la cuota inicial de la propiedad.
                </p>
            </div>
        </div>
    </section>

    <!-- Cards Grid -->
    <main class="max-w-7xl mx-auto px-4 pb-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for id, p in proyectos.items() %}
            <div class="bg-slate-800/80 border border-slate-700/80 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all flex flex-col justify-between">
                <div>
                    <!-- Image Container -->
                    <div class="relative h-48 overflow-hidden">
                        <img src="{{ p.imagen }}" alt="{{ p.nombre }}" class="w-full h-full object-cover">
                        <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent"></div>
                        <div class="absolute top-3 left-3 bg-slate-950/80 backdrop-blur text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-slate-700">
                            <i class="fa-solid fa-location-dot mr-1"></i> {{ p.ubicacion }}
                        </div>
                        <div class="absolute bottom-3 right-3 bg-amber-500 text-slate-950 font-black text-xs px-2.5 py-1 rounded-lg shadow-lg">
                            BONO: ${{ "{:,.0f}".format(p.descuento_voucher) }} USD
                        </div>
                    </div>

                    <!-- Details & Leaderboard -->
                    <div class="p-5">
                        <h3 class="text-lg font-bold text-white mb-1">{{ p.nombre }}</h3>
                        <p class="text-xs text-slate-400 mb-4">Top 5 Candidatos por el Voucher:</p>

                        <!-- TOP 5 RANKING TABLE -->
                        <div class="bg-slate-900/90 rounded-xl border border-slate-700/60 overflow-hidden mb-4">
                            {% for r in p.ranking %}
                            <div class="flex items-center justify-between px-3.5 py-2 border-b border-slate-800/80 text-xs {% if loop.first %}bg-emerald-950/40{% endif %}">
                                <div class="flex items-center gap-2">
                                    {% if loop.index == 1 %}
                                        <span class="w-5 text-amber-400 font-bold"><i class="fa-solid fa-trophy"></i></span>
                                    {% elif loop.index == 2 %}
                                        <span class="w-5 text-slate-300 font-bold">2.</span>
                                    {% elif loop.index == 3 %}
                                        <span class="w-5 text-amber-600 font-bold">3.</span>
                                    {% else %}
                                        <span class="w-5 text-slate-500 font-bold">{{ loop.index }}.</span>
                                    {% endif %}
                                    <span class="font-semibold {% if loop.first %}text-emerald-300 font-bold{% else %}text-slate-200{% endif %}">
                                        {{ r.nombre }}
                                    </span>
                                </div>
                                <span class="font-mono font-bold text-emerald-400">${{ "%.2f"|format(r.monto) }} USD</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Bidding Form -->
                <div class="p-5 pt-0 border-t border-slate-700/50 mt-2">
                    <form action="/pujar" method="POST" class="mt-3 flex flex-col gap-2.5">
                        <input type="hidden" name="id" value="{{ p.id }}">
                        
                        <input type="text" name="usuario" placeholder="Tu Nombre / Seudónimo" required 
                               class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 w-full">
                        
                        <div class="flex gap-2">
                            <div class="relative flex-1">
                                <span class="absolute left-3 top-2 text-xs text-slate-400">$</span>
                                <input type="number" name="monto" min="5" step="1" placeholder="Monto a pujar" required 
                                       class="bg-slate-900 border border-slate-700 rounded-lg pl-6 pr-2 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 w-full">
                            </div>
                            <button type="submit" 
                                    class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-4 py-2 rounded-lg text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-500/20">
                                <i class="fa-solid fa-bolt"></i> Pujar Ahora
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800 bg-slate-950 py-8 text-center text-xs text-slate-500">
        <p>© 2026 MetroPuja.ec — Subastas Inmobiliarias para Guayaquil y Samborondón.</p>
        <p class="mt-2 text-slate-600"><i class="fa-solid fa-lock text-emerald-400"></i> Pagos procesados vía dLocal Go Ecuador</p>
    </footer>

</body>
</html>
"""


@app.route("/")
def index():
  msg = request.args.get("msg", "")
  return render_template_string(HTML_TEMPLATE, proyectos=proyectos, msg=msg)


@app.route("/pujar", methods=["POST"])
def pujar():
  try:
    pid = int(request.form.get("id"))
    usuario = request.form.get("usuario", "Anónimo").strip()
    monto = float(request.form.get("monto", 0))

    if not usuario:
      usuario = "Comprador Guayaquil"

    if pid in proyectos and monto > 0:
      proyecto = proyectos[pid]

      # MODO PRUEBA LOCAL EN PYCHARM
      if (
          DLOCALGO_API_KEY == "TU_API_KEY_DLOCALGO_AQUI"
          or "AQUI" in DLOCALGO_API_KEY
      ):
        # Insertar puja y reordenar ranking Top 5
        proyecto["ranking"].append({"nombre": usuario, "monto": monto})
        # Ordenar de mayor a menor monto
        proyecto["ranking"] = sorted(
            proyecto["ranking"], key=lambda x: x["monto"], reverse=True
        )[:5]

        # Recalcular número de puesto
        for idx, item in enumerate(proyecto["ranking"]):
          item["puesto"] = idx + 1

        return redirect(
            url_for(
                "index",
                msg=(
                    f"¡Puja de ${monto:.2f} USD registrada exitosamente para"
                    f" {usuario}!"
                ),
            )
        )

      # MODO PRODUCCIÓN DLOCAL GO (Cobro dinámico por el monto ingresado)
      headers = {
          "Authorization": f"Bearer {DLOCALGO_API_KEY}:{DLOCALGO_SECRET_KEY}",
          "Content-Type": "application/json",
      }

      success_url = f"{request.host_url}exito?id={pid}&usuario={quote(usuario)}&monto={monto}"

      payload = {
          "amount": monto,
          "currency": "USD",
          "country": "EC",
          "description": (
              f"Puja Posicionamiento ${monto:.2f} - {proyecto['nombre']}"
          ),
          "success_url": success_url,
          "back_url": request.host_url,
      }

      response = requests.post(
          f"{DLOCALGO_BASE_URL}/v1/payments", json=payload, headers=headers
      )

      if response.status_code in [200, 201]:
        data = response.json()
        redirect_url = data.get("redirect_url")
        if redirect_url:
          return redirect(redirect_url)

      # Fallback local
      proyecto["ranking"].append({"nombre": usuario, "monto": monto})
      proyecto["ranking"] = sorted(
          proyecto["ranking"], key=lambda x: x["monto"], reverse=True
      )[:5]
      for idx, item in enumerate(proyecto["ranking"]):
        item["puesto"] = idx + 1

  except Exception as e:
    print(f"Error en puja: {e}")

  return redirect(url_for("index"))


@app.route("/exito")
def exito():
  try:
    pid = int(request.args.get("id", 0))
    usuario = request.args.get("usuario", "Comprador Guayaquil")
    monto = float(request.args.get("monto", 0))

    if pid in proyectos and monto > 0:
      proyecto = proyectos[pid]
      proyecto["ranking"].append({"nombre": usuario, "monto": monto})
      proyecto["ranking"] = sorted(
          proyecto["ranking"], key=lambda x: x["monto"], reverse=True
      )[:5]
      for idx, item in enumerate(proyecto["ranking"]):
        item["puesto"] = idx + 1

      return redirect(
          url_for(
              "index",
              msg=(
                  f"¡Pago confirmado de ${monto:.2f} USD! {usuario} se ha"
                  " posicionado en el ranking."
              ),
          )
      )
  except (ValueError, TypeError):
    pass

  return redirect(url_for("index"))


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)
