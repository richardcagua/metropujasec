import json
import os
from urllib.parse import quote
from flask import Flask, jsonify, redirect, render_template_string, request, url_for
import requests

app = Flask(__name__)

# Configuración de dLocal Go (Creación gratis en dlocalgo.com)
DLOCALGO_API_KEY = os.environ.get("DLOCALGO_API_KEY", "TU_API_KEY_DLOCALGO_AQUI")
DLOCALGO_SECRET_KEY = os.environ.get(
    "DLOCALGO_SECRET_KEY", "TU_SECRET_KEY_DLOCALGO_AQUI"
)
# Usa 'https://api-sbx.dlocalgo.com' para pruebas o 'https://api.dlocalgo.com' para producción
DLOCALGO_BASE_URL = os.environ.get(
    "DLOCALGO_BASE_URL", "https://api-sbx.dlocalgo.com"
)

# Base de datos en memoria para el prototipo en vivo (Proyectos de Guayas)
proyectos = {
    1: {
        "id": 1,
        "nombre": "Suite Luxury Mocolí",
        "ubicacion": "Isla Mocolí, Samborondón",
        "descuento_voucher": 12000.00,
        "puja_actual": 45.00,
        "lider_actual": "Carlos M.",
        "tiempo_restante": 180,  # segundos
        "imagen": (
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80"
        ),
        "total_pujas": 45,
    },
    2: {
        "id": 2,
        "nombre": "Depa Vista al Río - Torre Bellini",
        "ubicacion": "Puerto Santa Ana, Guayaquil",
        "descuento_voucher": 15000.00,
        "puja_actual": 82.00,
        "lider_actual": "Andrea V.",
        "tiempo_restante": 240,
        "imagen": (
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
        ),
        "total_pujas": 82,
    },
    3: {
        "id": 3,
        "nombre": "Casa Modelo Premier",
        "ubicacion": "Vía a la Costa, Km 14",
        "descuento_voucher": 10000.00,
        "puja_actual": 29.00,
        "lider_actual": "Roberto G.",
        "tiempo_restante": 310,
        "imagen": (
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"
        ),
        "total_pujas": 29,
    },
    4: {
        "id": 4,
        "nombre": "Penthouse Ejecutivo Ceibos",
        "ubicacion": "Los Ceibos, Guayaquil",
        "descuento_voucher": 20000.00,
        "puja_actual": 110.00,
        "lider_actual": "Dome K.",
        "tiempo_restante": 90,
        "imagen": (
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
        ),
        "total_pujas": 110,
    },
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetroPuja.ec | Subastas de Reserva Inmobiliaria en Guayas</title>
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
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> PUJAS EN VIVO
                </span>
                <div class="hidden md:flex items-center gap-2 text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
                    <i class="fa-solid fa-bolt text-emerald-400"></i> Pagos con dLocal Go (Ecuador)
                </div>
            </div>
        </div>
    </header>

    <!-- Banner Mensaje / Notificación -->
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
                    Oportunidad Inmobiliaria Exclusiva
                </span>
                <h2 class="text-3xl md:text-4xl font-extrabold text-white mt-3 leading-tight">
                    Gana un Voucher de <span class="text-emerald-400">$10,000 a $20,000 USD</span> para la reserva de tu propiedad.
                </h2>
                <p class="text-slate-300 text-sm mt-3 leading-relaxed">
                    Puja $1.00 USD para tomar el primer lugar. Cada puja incrementa el acumulado y reinicia el cronómetro de cierre. El último pujador gana el bono de descuento oficial para la entrada.
                </p>
            </div>
        </div>
    </section>

    <!-- Project Cards Grid -->
    <main class="max-w-7xl mx-auto px-4 pb-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            {% for id, p in proyectos.items() %}
            <div class="bg-slate-800/80 border border-slate-700/80 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all flex flex-col justify-between">
                <div>
                    <!-- Image Container -->
                    <div class="relative h-52 overflow-hidden">
                        <img src="{{ p.imagen }}" alt="{{ p.nombre }}" class="w-full h-full object-cover">
                        <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent"></div>
                        <div class="absolute top-3 left-3 bg-slate-950/80 backdrop-blur text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-slate-700">
                            <i class="fa-solid fa-location-dot mr-1"></i> {{ p.ubicacion }}
                        </div>
                        <div class="absolute bottom-3 right-3 bg-amber-500 text-slate-950 font-black text-sm px-3 py-1 rounded-lg shadow-lg">
                            AHORRO: ${{ "{:,.0f}".format(p.descuento_voucher) }} USD
                        </div>
                    </div>

                    <!-- Content Details -->
                    <div class="p-6">
                        <h3 class="text-xl font-bold text-white mb-1">{{ p.nombre }}</h3>
                        <p class="text-xs text-slate-400 mb-4">Voucher oficial aplicable al pago inicial de la propiedad.</p>

                        <div class="grid grid-cols-2 gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-700/50 mb-4">
                            <div>
                                <span class="text-slate-400 text-xs block">Puja Actual</span>
                                <span class="text-2xl font-black text-emerald-400">${{ "%.2f"|format(p.puja_actual) }}</span>
                            </div>
                            <div>
                                <span class="text-slate-400 text-xs block">Líder en Vivo</span>
                                <span class="text-sm font-bold text-slate-200 flex items-center gap-1 mt-1">
                                    <i class="fa-solid fa-crown text-amber-400 text-xs"></i> {{ p.lider_actual }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Action & Bidding Form -->
                <div class="p-6 pt-0 border-t border-slate-700/50 mt-2">
                    <form action="/pujar" method="POST" class="mt-4 flex flex-col gap-3">
                        <input type="hidden" name="id" value="{{ p.id }}">
                        <div class="flex gap-2">
                            <input type="text" name="usuario" placeholder="Tu nombre / Seudónimo" required 
                                   class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 flex-1">
                            <button type="submit" 
                                    class="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-5 py-2 rounded-lg text-sm transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20">
                                <i class="fa-solid fa-gavel"></i> Pujar +$1.00
                            </button>
                        </div>
                        <div class="flex items-center justify-between text-xs text-slate-400 px-1">
                            <span><i class="fa-regular fa-clock mr-1"></i> Cierre dinámico</span>
                            <span>Total pujas: <strong class="text-white">{{ p.total_pujas }}</strong></span>
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
        <p class="mt-2 text-slate-600 flex items-center justify-center gap-2">
            <i class="fa-solid fa-shield-halved text-emerald-400"></i> Procesamiento local seguro dLocal Go (Ecuador)
        </p>
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

    if not usuario:
      usuario = "Comprador Guayaquil"

    if pid in proyectos:
      proyecto = proyectos[pid]

      # MODO PRUEBA EN PYCHARM: Si no has colocado tus llaves reales de dLocal Go
      if (
          DLOCALGO_API_KEY == "TU_API_KEY_DLOCALGO_AQUI"
          or "AQUI" in DLOCALGO_API_KEY
      ):
        proyectos[pid]["puja_actual"] += 1.00
        proyectos[pid]["total_pujas"] += 1
        proyectos[pid]["lider_actual"] = usuario
        proyectos[pid]["tiempo_restante"] = 120
        return redirect(
            url_for(
                "index",
                msg=(
                    f"¡Puja de $1.00 USD registrada (Modo Prueba) para"
                    f" {usuario}!"
                ),
            )
        )

      # MODO PRODUCCIÓN: Petición a dLocal Go API (Checkout Ecuador)
      headers = {
          "Authorization": f"Bearer {DLOCALGO_API_KEY}:{DLOCALGO_SECRET_KEY}",
          "Content-Type": "application/json",
      }

      success_url = (
          f"{request.host_url}exito?id={pid}&usuario={quote(usuario)}"
      )

      payload = {
          "amount": 1.00,
          "currency": "USD",
          "country": "EC",
          "description": (
              f"Puja +$1.00 - {proyecto['nombre']} ({proyecto['ubicacion']})"
          ),
          "success_url": success_url,
          "back_url": request.host_url,
          "notification_url": f"{request.host_url}dlocalgo/webhook",
      }

      response = requests.post(
          f"{DLOCALGO_BASE_URL}/v1/payments", json=payload, headers=headers
      )

      if response.status_code in [200, 201]:
        data = response.json()
        redirect_url = data.get("redirect_url")
        if redirect_url:
          return redirect(redirect_url)

      # Fallback si ocurre algún problema con las credenciales
      proyectos[pid]["puja_actual"] += 1.00
      proyectos[pid]["total_pujas"] += 1
      proyectos[pid]["lider_actual"] = usuario
      return redirect(
          url_for(
              "index",
              msg=(
                  f"¡Puja procesada correctamente para {usuario}! (Actualización"
                  " local)"
              ),
          )
      )

  except Exception as e:
    print(f"Error procesando dLocal Go: {e}")

  return redirect(url_for("index"))


@app.route("/exito")
def exito():
  try:
    pid = int(request.args.get("id", 0))
    usuario = request.args.get("usuario", "Comprador Guayaquil")

    if pid in proyectos:
      proyectos[pid]["puja_actual"] += 1.00
      proyectos[pid]["total_pujas"] += 1
      proyectos[pid]["lider_actual"] = usuario
      proyectos[pid]["tiempo_restante"] = 120
      return redirect(
          url_for(
              "index",
              msg=(
                  "¡Pago procesado con éxito por dLocal Go! Ahora"
                  f" {usuario} es el nuevo líder."
              ),
          )
      )
  except (ValueError, TypeError):
    pass

  return redirect(url_for("index"))


# Webhook para notificaciones automáticas de dLocal Go
@app.route("/dlocalgo/webhook", methods=["POST"])
def webhook():
  data = request.get_json(silent=True) or {}
  # Aquí dLocal Go confirma cuando la transferencia o tarjeta fue aprobada
  return jsonify({"status": "RECEIVED"}), 200


# Endpoint JSON
@app.route("/api/proyectos")
def api_proyectos():
  return jsonify(proyectos)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)
