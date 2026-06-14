"""
Bot de Delivery para Instagram
================================
Responde mensajes automáticamente, verifica stock,
pide dirección, calcula demora y te avisa por WhatsApp.
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ============================================================
#  CONFIGURACIÓN — Completá estos datos antes de empezar
# ============================================================

TU_UBICACION = "Av. Corrientes 1234, Buenos Aires"   # Tu dirección de despacho
TU_WHATSAPP  = "+549XXXXXXXXXX"                       # Tu número con código de país
HORA_APERTURA = 20                                    # Hora en que abrís (20 = 8pm)
HORA_CIERRE   = 3                                     # Hora en que cerrás (3 = 3am)

# Tokens — los obtenés siguiendo la Guía de Configuración
VERIFY_TOKEN       = os.getenv("VERIFY_TOKEN", "mi_token_secreto")
PAGE_ACCESS_TOKEN  = os.getenv("PAGE_ACCESS_TOKEN", "")
TWILIO_SID         = os.getenv("TWILIO_SID", "")
TWILIO_AUTH        = os.getenv("TWILIO_AUTH", "")
TWILIO_WHATSAPP    = os.getenv("TWILIO_WHATSAPP", "whatsapp:+14155238886")
GOOGLE_MAPS_KEY    = os.getenv("GOOGLE_MAPS_KEY", "")

# ============================================================
#  MENÚ Y STOCK — Editá esto con tus productos reales
# ============================================================

STOCK = {
    # --- COMBOS CHAMPAGNE ---
    "1":  {"nombre": "Chandon Délice + 2 Speed + Hielo",         "precio": 26500, "stock": 10, "emoji": "🥂"},
    "2":  {"nombre": "Chandon Rosé + 2 Speed + Hielo",           "precio": 26500, "stock": 10, "emoji": "🥂"},
    "3":  {"nombre": "Chandon Extra Brut + 2 Speed + Hielo",     "precio": 26500, "stock": 10, "emoji": "🥂"},
    # --- COMBOS FERNET / APERITIVOS ---
    "4":  {"nombre": "Fernet Branca 750ml + Coca + Hielo",       "precio": 24900, "stock": 10, "emoji": "🥃"},
    "5":  {"nombre": "Campari + 2 Jugos + Hielo",                "precio": 19500, "stock": 10, "emoji": "🍹"},
    # --- COMBOS VODKA SMIRNOFF ---
    "6":  {"nombre": "Smirnoff Manzana + 2 Cepita + Hielo",     "precio": 20300, "stock": 10, "emoji": "🍸"},
    "7":  {"nombre": "Smirnoff Manzana + 2 Speed + Hielo",      "precio": 20300, "stock": 10, "emoji": "🍸"},
    "8":  {"nombre": "Smirnoff Sandía + 2 Cepita + Hielo",      "precio": 20300, "stock": 10, "emoji": "🍸"},
    "9":  {"nombre": "Smirnoff Sandía + 2 Speed + Hielo",       "precio": 20300, "stock": 10, "emoji": "🍸"},
    "10": {"nombre": "Smirnoff Raspberry + 2 Cepita + Hielo",   "precio": 20300, "stock": 10, "emoji": "🍸"},
    "11": {"nombre": "Smirnoff Raspberry + 2 Speed + Hielo",    "precio": 20300, "stock": 10, "emoji": "🍸"},
    # --- COMBOS VODKA SKYY ---
    "12": {"nombre": "Skyy Cosmic + 2 Cepitas + Hielo",         "precio": 21500, "stock": 10, "emoji": "🍸"},
    "13": {"nombre": "Skyy Cosmic + 2 Speed + Hielo",           "precio": 21500, "stock": 10, "emoji": "🍸"},
    "14": {"nombre": "Skyy Raspberry + 2 Cepitas + Hielo",      "precio": 21500, "stock": 10, "emoji": "🍸"},
    "15": {"nombre": "Skyy Raspberry + 2 Speed + Hielo",        "precio": 21500, "stock": 10, "emoji": "🍸"},
    "16": {"nombre": "Skyy Apricot + 2 Cepitas + Hielo",        "precio": 21500, "stock": 10, "emoji": "🍸"},
    "17": {"nombre": "Skyy Apricot + 2 Speed + Hielo",          "precio": 21500, "stock": 10, "emoji": "🍸"},
    "18": {"nombre": "Skyy Coco + 2 Cepitas + Hielo",           "precio": 21500, "stock": 10, "emoji": "🍸"},
    "19": {"nombre": "Skyy Coco + 2 Speed + Hielo",             "precio": 15000, "stock": 10, "emoji": "🍸"},
    # --- COMBOS VODKA ABSOLUT ---
    "20": {"nombre": "Absolut Raspberry + 2 Speed + Hielo",     "precio": 29500, "stock": 10, "emoji": "🍸"},
    "21": {"nombre": "Absolut Mango + 2 Speed + Hielo",         "precio": 29500, "stock": 10, "emoji": "🍸"},
    "22": {"nombre": "Absolut Vainilla + 2 Speed + Hielo",      "precio": 29500, "stock": 10, "emoji": "🍸"},
    "23": {"nombre": "Absolut Común + 2 Speed + Hielo",         "precio": 28500, "stock": 10, "emoji": "🍸"},
    # --- COMBOS RON ---
    "24": {"nombre": "Bacardí Oro + 1 Coca + Hielo",            "precio": 23600, "stock": 10, "emoji": "🍹"},
    "25": {"nombre": "Bacardí Blanco + 1 Coca + Hielo",         "precio": 7000,  "stock": 10, "emoji": "🍹"},
    "26": {"nombre": "Havana Oro + 1 Coca + Hielo",             "precio": 23600, "stock": 10, "emoji": "🍹"},
    "27": {"nombre": "Havana Blanco + 1 Coca + Hielo",          "precio": 7000,  "stock": 10, "emoji": "🍹"},
    "28": {"nombre": "Malibu + 1 Coca + Hielo",                 "precio": 7000,  "stock": 10, "emoji": "🍹"},
    "29": {"nombre": "Malibu + 2 Cepitas + Hielo",              "precio": 7000,  "stock": 10, "emoji": "🍹"},
    # --- COMBOS GIN ---
    "30": {"nombre": "Tanqueray + Tónica + Hielo",              "precio": 35500, "stock": 10, "emoji": "🍸"},
    "31": {"nombre": "Bombay + 1 Tónica + Hielo",               "precio": 7000,  "stock": 10, "emoji": "🍸"},
    "32": {"nombre": "Heredero + 1 Tónica + Hielo",             "precio": 22500, "stock": 10, "emoji": "🍸"},
    "33": {"nombre": "Gordon's + 1 Tónica + Hielo",             "precio": 21500, "stock": 10, "emoji": "🍸"},
    "34": {"nombre": "Merlé + 1 Tónica + Hielo",                "precio": 19500, "stock": 10, "emoji": "🍸"},
    "35": {"nombre": "Aconcagua + 1 Tónica + Hielo",            "precio": 7000,  "stock": 10, "emoji": "🍸"},
    # --- COMBOS WHISKY ---
    "36": {"nombre": "Red Label + 1 Coca + Hielo",              "precio": 37500, "stock": 10, "emoji": "🥃"},
    "37": {"nombre": "Red Label + 2 Speed + Hielo",             "precio": 37500, "stock": 10, "emoji": "🥃"},
    "38": {"nombre": "Black Label + Coca + Hielo",              "precio": 56500, "stock": 10, "emoji": "🥃"},
    "39": {"nombre": "Black Label + 2 Speed + Hielo",           "precio": 56500, "stock": 10, "emoji": "🥃"},
    "40": {"nombre": "White Horse + 1 Coca + Hielo",            "precio": 7000,  "stock": 10, "emoji": "🥃"},
    "41": {"nombre": "Jägermeister 750ml + Coca 2.25L + Hielo", "precio": 36500, "stock": 10, "emoji": "🥃"},
    "42": {"nombre": "Jägermeister + 2 Speed + Hielo",          "precio": 36500, "stock": 10, "emoji": "🥃"},
    "43": {"nombre": "1882 + Coca 2.25L + Hielo",               "precio": 7000,  "stock": 10, "emoji": "🥃"},
    # --- COMBOS BUHO NEGRO ---
    "44": {"nombre": "Búho Negro + 1 Coca + Hielo",             "precio": 19000, "stock": 10, "emoji": "🥃"},
    "45": {"nombre": "Búho Negro + Coca 2.25L + Hielo",         "precio": 7000,  "stock": 10, "emoji": "🥃"},
    # --- COMBOS VINO ---
    "46": {"nombre": "Cosecha Tardía + 2 Speed + Hielo",        "precio": 15500, "stock": 10, "emoji": "🍷"},
    "47": {"nombre": "Novecento + 2 Speed + Hielo",             "precio": 14900, "stock": 10, "emoji": "🍷"},
    "48": {"nombre": "Navarro Correa + 2 Speed + Hielo",        "precio": 19800, "stock": 10, "emoji": "🍷"},
    "49": {"nombre": "Federico Alvear + 2 Speed + Hielo",       "precio": 15800, "stock": 10, "emoji": "🍷"},
    # --- BOTELLAS SOLAS ---
    "50": {"nombre": "Black Label",          "precio": 53500, "stock": 10, "emoji": "🥃"},
    "51": {"nombre": "Red Label",            "precio": 35000, "stock": 10, "emoji": "🥃"},
    "52": {"nombre": "White Horse",          "precio": 19000, "stock": 10, "emoji": "🥃"},
    "53": {"nombre": "Fernet Branca 750ml",  "precio": 19000, "stock": 10, "emoji": "🥃"},
    "54": {"nombre": "Sheridans",            "precio": 42000, "stock": 10, "emoji": "🥃"},
    "55": {"nombre": "Tía María",            "precio": 7000,  "stock": 10, "emoji": "🥃"},
    "56": {"nombre": "Tanqueray",            "precio": 28000, "stock": 10, "emoji": "🍸"},
    "57": {"nombre": "Bombay",               "precio": 33000, "stock": 10, "emoji": "🍸"},
    "58": {"nombre": "Heredero",             "precio": 16000, "stock": 10, "emoji": "🍸"},
    "59": {"nombre": "Aconcagua",            "precio": 17000, "stock": 10, "emoji": "🍸"},
    "60": {"nombre": "Merlé",                "precio": 16000, "stock": 10, "emoji": "🍸"},
    "61": {"nombre": "Smirnoff Raspberry",   "precio": 15000, "stock": 10, "emoji": "🍸"},
    "62": {"nombre": "Smirnoff Sandía",      "precio": 15000, "stock": 10, "emoji": "🍸"},
    "63": {"nombre": "Smirnoff Manzana",     "precio": 15000, "stock": 10, "emoji": "🍸"},
    "64": {"nombre": "Skyy Raspberry",       "precio": 16000, "stock": 10, "emoji": "🍸"},
    "65": {"nombre": "Skyy Apricot",         "precio": 16000, "stock": 10, "emoji": "🍸"},
    "66": {"nombre": "Skyy Cosmic",          "precio": 16000, "stock": 10, "emoji": "🍸"},
    "67": {"nombre": "Skyy Coco",            "precio": 10000, "stock": 10, "emoji": "🍸"},
    "68": {"nombre": "Bacardí Oro",          "precio": 19000, "stock": 10, "emoji": "🍹"},
    "69": {"nombre": "Bacardí Blanco",       "precio": 19000, "stock": 10, "emoji": "🍹"},
    "70": {"nombre": "Havana Oro",           "precio": 19000, "stock": 10, "emoji": "🍹"},
    "71": {"nombre": "Havana Blanco",        "precio": 19000, "stock": 10, "emoji": "🍹"},
    "72": {"nombre": "Malibu",               "precio": 17000, "stock": 10, "emoji": "🍹"},
    "73": {"nombre": "Búho Negro",           "precio": 12000, "stock": 10, "emoji": "🥃"},
    "74": {"nombre": "Campari",              "precio": 15000, "stock": 10, "emoji": "🍹"},
    "75": {"nombre": "Chandon",              "precio": 22500, "stock": 10, "emoji": "🥂"},
    # --- VINOS SOLOS ---
    "76": {"nombre": "Cosecha Tardía",       "precio": 7500,  "stock": 10, "emoji": "🍷"},
    "77": {"nombre": "Alma Mora",            "precio": 7500,  "stock": 10, "emoji": "🍷"},
    "78": {"nombre": "Portillo",             "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "79": {"nombre": "Trumpeter",            "precio": 13500, "stock": 10, "emoji": "🍷"},
    "80": {"nombre": "Navarro Correa",       "precio": 16500, "stock": 10, "emoji": "🍷"},
    "81": {"nombre": "Federico Alvear",      "precio": 10000, "stock": 10, "emoji": "🍷"},
    "82": {"nombre": "Novecento",            "precio": 10000, "stock": 10, "emoji": "🍷"},
    "83": {"nombre": "Los Árboles",          "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "84": {"nombre": "Otro Loco Más",        "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "85": {"nombre": "Benjamín",             "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "86": {"nombre": "Dadá",                 "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "87": {"nombre": "Callia",               "precio": 8000,  "stock": 10, "emoji": "🍷"},
    "88": {"nombre": "Luigi Bosca",          "precio": 18000, "stock": 10, "emoji": "🍷"},
    "89": {"nombre": "Escorihuela Gascón",   "precio": 13500, "stock": 10, "emoji": "🍷"},
    "90": {"nombre": "Privado Reserva",      "precio": 12000, "stock": 10, "emoji": "🍷"},
    "91": {"nombre": "DV Catena",            "precio": 18000, "stock": 10, "emoji": "🍷"},
    # --- BEBIDAS Y EXTRAS ---
    "92": {"nombre": "Coca-Cola 2.25L",      "precio": 5800,  "stock": 20, "emoji": "🥤"},
    "93": {"nombre": "Coca-Cola",            "precio": 5800,  "stock": 20, "emoji": "🥤"},
    "94": {"nombre": "Tónica 1.75L",         "precio": 4500,  "stock": 20, "emoji": "🥤"},
    "95": {"nombre": "Cepita 1L",            "precio": 3000,  "stock": 20, "emoji": "🧃"},
    "96": {"nombre": "Speed XL",             "precio": 3500,  "stock": 20, "emoji": "⚡"},
    "97": {"nombre": "Hielo 2 Kg",           "precio": 3000,  "stock": 20, "emoji": "🧊"},
    "98": {"nombre": "Hielo 4 Kg",           "precio": 5000,  "stock": 20, "emoji": "🧊"},
}

# ============================================================
#  ESTADO DE CONVERSACIONES EN MEMORIA
# ============================================================

conversaciones = {}

def get_estado(user_id):
    if user_id not in conversaciones:
        conversaciones[user_id] = {
            "paso": "inicio",
            "carrito": [],
            "nombre": "",
            "direccion": ""
        }
    return conversaciones[user_id]

def reset_estado(user_id):
    conversaciones[user_id] = {
        "paso": "inicio",
        "carrito": [],
        "nombre": "",
        "direccion": ""
    }

# ============================================================
#  FUNCIONES PRINCIPALES
# ============================================================

def esta_abierto():
    hora = datetime.now().hour
    if HORA_APERTURA <= HORA_CIERRE:
        return HORA_APERTURA <= hora < HORA_CIERRE
    else:  # Cierra después de medianoche
        return hora >= HORA_APERTURA or hora < HORA_CIERRE

def generar_menu():
    texto = "📋 *Nuestro menú de hoy:*\n\n"
    for num, item in STOCK.items():
        if item["stock"] > 0:
            texto += f"{item['emoji']} *{num}.* {item['nombre']} — ${item['precio']:,}\n"
        else:
            texto += f"❌ *{num}.* {item['nombre']} — *Sin stock*\n"
    texto += "\nEscribí el *número* del producto que querés pedir."
    texto += "\nPodés pedir varios, uno por vez. Cuando termines escribí *LISTO*."
    return texto

def calcular_demora(direccion_cliente):
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": TU_UBICACION,
            "destinations": direccion_cliente,
            "key": GOOGLE_MAPS_KEY,
            "language": "es",
            "mode": "driving"
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        elemento = data["rows"][0]["elements"][0]
        if elemento["status"] == "OK":
            minutos = elemento["duration"]["value"] // 60
            distancia = elemento["distance"]["text"]
            return minutos + 15, distancia  # +15 min de preparación
        return 45, "desconocida"
    except Exception:
        return 45, "desconocida"

def enviar_whatsapp_dueno(texto):
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            body=texto,
            from_=TWILIO_WHATSAPP,
            to=f"whatsapp:{TU_WHATSAPP}"
        )
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")

def armar_resumen_pedido(estado, demora, distancia):
    carrito = estado["carrito"]
    total = sum(STOCK[c["id"]]["precio"] * c["cantidad"] for c in carrito)
    lineas = []
    for c in carrito:
        item = STOCK[c["id"]]
        lineas.append(f"  • {item['nombre']} x{c['cantidad']} = ${item['precio'] * c['cantidad']:,}")
    detalle = "\n".join(lineas)
    hora_ahora = datetime.now().strftime("%H:%M")
    return (
        f"🛵 *NUEVO PEDIDO — {hora_ahora}*\n"
        f"👤 Cliente: {estado['nombre']}\n"
        f"📍 Dirección: {estado['direccion']}\n"
        f"📦 Pedido:\n{detalle}\n"
        f"💰 Total: ${total:,}\n"
        f"⏱ Demora estimada: {demora} min ({distancia})"
    )

def enviar_mensaje_instagram(user_id, texto):
    url = f"https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": texto},
        "access_token": PAGE_ACCESS_TOKEN
    }
    requests.post(url, json=payload, headers=headers)

# ============================================================
#  LÓGICA DEL BOT — Flujo de conversación
# ============================================================

def procesar_mensaje(user_id, texto):
    texto = texto.strip()
    estado = get_estado(user_id)
    paso = estado["paso"]
    respuesta = ""

    # — CERRADO —
    if not esta_abierto():
        return (
            f"😴 Hola! Por ahora estamos cerrados.\n"
            f"Abrimos a las {HORA_APERTURA}:00hs. ¡Te esperamos!"
        )

    # — INICIO —
    if paso == "inicio" or texto.lower() in ["hola", "buenas", "buen dia", "buenas noches", "hi"]:
        estado["paso"] = "pidiendo_nombre"
        return (
            "👋 ¡Hola! Bienvenido/a a nuestro delivery nocturno 🌙\n\n"
            "¿Cómo te llamás?"
        )

    # — NOMBRE —
    if paso == "pidiendo_nombre":
        estado["nombre"] = texto.title()
        estado["paso"] = "viendo_menu"
        return (
            f"¡Genial, {estado['nombre']}! 😊\n\n"
            + generar_menu()
        )

    # — ELIGIENDO PRODUCTOS —
    if paso == "viendo_menu":
        if texto.upper() == "LISTO":
            if not estado["carrito"]:
                return "Todavía no elegiste nada 😅 Escribí el número de un producto."
            estado["paso"] = "pidiendo_direccion"
            total = sum(STOCK[c["id"]]["precio"] * c["cantidad"] for c in estado["carrito"])
            resumen = "\n".join(
                f"  {STOCK[c['id']]['emoji']} {STOCK[c['id']]['nombre']} x{c['cantidad']}"
                for c in estado["carrito"]
            )
            return (
                f"🛒 Tu pedido hasta ahora:\n{resumen}\n"
                f"💰 Total: ${total:,}\n\n"
                f"📍 ¿A qué dirección te lo mandamos?\n"
                f"Escribí la calle, número y barrio."
            )

        if texto in STOCK:
            item = STOCK[texto]
            if item["stock"] == 0:
                return f"❌ Lo siento, {item['nombre']} está sin stock hoy. Elegí otra opción."
            # Agregar al carrito
            existente = next((c for c in estado["carrito"] if c["id"] == texto), None)
            if existente:
                existente["cantidad"] += 1
            else:
                estado["carrito"].append({"id": texto, "cantidad": 1})
            item["stock"] -= 1
            return (
                f"✅ Agregado: {item['emoji']} {item['nombre']}\n\n"
                f"¿Querés agregar algo más? Escribí otro número o escribí *LISTO* para confirmar."
            )

        return (
            "No entendí eso 😅\n"
            "Escribí el *número* del producto o *LISTO* para terminar."
        )

    # — DIRECCIÓN —
    if paso == "pidiendo_direccion":
        estado["direccion"] = texto
        estado["paso"] = "confirmando"
        demora, distancia = calcular_demora(texto)

        # Armar resumen para el cliente
        carrito = estado["carrito"]
        total = sum(STOCK[c["id"]]["precio"] * c["cantidad"] for c in carrito)
        detalle = "\n".join(
            f"  {STOCK[c['id']]['emoji']} {STOCK[c['id']]['nombre']} x{c['cantidad']} — ${STOCK[c['id']]['precio'] * c['cantidad']:,}"
            for c in carrito
        )

        resumen_cliente = (
            f"📦 *Resumen de tu pedido:*\n{detalle}\n"
            f"💰 Total: ${total:,}\n"
            f"📍 Entrega en: {estado['direccion']}\n"
            f"⏱ Demora estimada: *{demora} minutos*\n\n"
            f"¿Confirmás el pedido? Respondé *SÍ* o *NO*."
        )

        # Guardar demora para usarla en confirmación
        estado["demora"] = demora
        estado["distancia"] = distancia
        return resumen_cliente

    # — CONFIRMACIÓN —
    if paso == "confirmando":
        if texto.upper() in ["SI", "SÍ", "S", "YES", "OK", "DALE", "CONFIRMO"]:
            resumen_dueno = armar_resumen_pedido(estado, estado["demora"], estado["distancia"])
            enviar_whatsapp_dueno(resumen_dueno)
            reset_estado(user_id)
            return (
                f"🎉 ¡Pedido confirmado! Estamos preparando todo.\n"
                f"⏱ Llegamos en aprox. *{estado.get('demora', 45)} minutos*.\n\n"
                f"¡Gracias por elegirnos! 🙌"
            )
        elif texto.upper() in ["NO", "N", "CANCELAR", "CANCEL"]:
            reset_estado(user_id)
            return "❌ Pedido cancelado. Si querés volver a pedir, ¡escribinos cuando quieras! 👋"
        else:
            return "Por favor respondé *SÍ* para confirmar o *NO* para cancelar."

    # Fallback
    reset_estado(user_id)
    return "Hola! Escribí *hola* para empezar a pedir 🛵"


# ============================================================
#  ENDPOINTS DE INSTAGRAM (Webhook)
# ============================================================

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Meta llama a este endpoint para verificar tu bot."""
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    """Recibe los mensajes de Instagram y responde."""
    data = request.json
    try:
        for entry in data.get("entry", []):
            for evento in entry.get("messaging", []):
                user_id = evento["sender"]["id"]
                if "message" in evento and "text" in evento["message"]:
                    texto = evento["message"]["text"]
                    respuesta = procesar_mensaje(user_id, texto)
                    enviar_mensaje_instagram(user_id, respuesta)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
    return jsonify({"status": "ok"}), 200

@app.route("/stock", methods=["GET"])
def ver_stock():
    """Página simple para ver el stock actual."""
    html = "<h2>📦 Stock actual</h2><ul>"
    for num, item in STOCK.items():
        color = "green" if item["stock"] > 0 else "red"
        html += f"<li style='color:{color}'>{item['emoji']} {item['nombre']} — Stock: {item['stock']}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(debug=True, port=5000)
