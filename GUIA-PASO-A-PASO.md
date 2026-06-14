# 🛵 Guía Completa — Bot de Delivery para Instagram

## ¿Qué vas a tener cuando termines?

Un bot que:
- Responde solo los mensajes de Instagram
- Muestra el menú y verifica stock
- Pide la dirección al cliente y calcula la demora
- Te manda un WhatsApp con el resumen del pedido

---

## PARTE 1 — Instalar lo necesario en tu computadora

### Paso 1.1 — Instalar Python
1. Abrí el navegador y entrá a **python.org/downloads**
2. Hacé clic en "Download Python 3.12" (el botón amarillo grande)
3. Ejecutá el instalador. **MUY IMPORTANTE:** tildá la opción que dice *"Add Python to PATH"* antes de instalar
4. Hacé clic en "Install Now"

### Paso 1.2 — Instalar las librerías del bot
1. Buscá en tu PC la aplicación **"CMD"** o **"Símbolo del sistema"** (en Windows) o **"Terminal"** (en Mac)
2. Pegá estos comandos uno por uno y presioná Enter:

```
cd Desktop
mkdir delivery-bot
cd delivery-bot
```

3. Copiá los archivos `bot.py`, `requirements.txt`, `.env.example` y `.gitignore` a esa carpeta
4. Luego ejecutá:

```
pip install -r requirements.txt
```

Esperá a que termine (puede tardar 1-2 minutos).

---

## PARTE 2 — Crear cuenta en Twilio (para el WhatsApp)

Twilio es el servicio que manda el mensaje a tu WhatsApp cuando llega un pedido.

1. Entrá a **twilio.com** y creá una cuenta gratis
2. Verificá tu número de teléfono cuando te lo pida
3. Una vez dentro, vas a ver tu **Account SID** y **Auth Token** — copiálos
4. Buscá en el menú "Messaging > Try it out > Send a WhatsApp message"
5. Seguí los pasos para conectar tu WhatsApp personal al sandbox de Twilio
   (básicamente mandás un mensaje a un número de Twilio)

---

## PARTE 3 — Crear la App en Meta Developers (para Instagram)

Esta parte conecta el bot con tu cuenta de Instagram.

1. Entrá a **developers.facebook.com** con tu cuenta de Facebook
2. Hacé clic en "Create App" (Crear App)
3. Elegí el tipo **"Business"**
4. Poné un nombre (ej: "Bot Delivery") y hacé clic en Crear
5. En el panel de la app, buscá **"Instagram"** y hacé clic en "Set up"
6. Seguí los pasos para conectar tu cuenta de Instagram Business
7. En la sección "Access Tokens", generá un **Page Access Token** — copialo
8. Guardá también el número de tu Instagram Business Account ID

---

## PARTE 4 — Obtener clave de Google Maps

Para calcular la demora de entrega necesitás una clave de Google Maps.

1. Entrá a **console.cloud.google.com** con tu cuenta de Google
2. Creá un proyecto nuevo (botón arriba a la izquierda > "New Project")
3. Buscá "Distance Matrix API" y habilitala
4. Andá a "Credentials" > "Create Credentials" > "API Key"
5. Copiá la clave que aparece

> 💡 Google da $200 de crédito gratis por mes, más que suficiente para un delivery pequeño.

---

## PARTE 5 — Configurar tus datos en el bot

1. Abrí el archivo **`.env.example`**, copialo y renombralo como **`.env`**
2. Completalo con tus datos reales:

```
VERIFY_TOKEN=delivery_secreto_2024        ← Inventate una palabra cualquiera
PAGE_ACCESS_TOKEN=EAAxxxxxxxxxx...        ← El que copiaste de Meta
TWILIO_SID=ACxxxxxxxxxxxxxxxxx            ← De tu cuenta Twilio
TWILIO_AUTH=xxxxxxxxxxxxxxxxxx            ← De tu cuenta Twilio
TWILIO_WHATSAPP=whatsapp:+14155238886     ← El número del sandbox de Twilio
GOOGLE_MAPS_KEY=AIzaSyxxxxxxxxxx          ← De Google Cloud
```

3. Abrí el archivo **`bot.py`** con el Bloc de Notas y editá la sección de configuración:

```python
TU_UBICACION = "Tu dirección real de despacho"
TU_WHATSAPP  = "+549XXXXXXXXXX"   # Tu número con código de país
HORA_APERTURA = 20                # 20 = 8pm
HORA_CIERRE   = 3                 # 3 = 3am
```

4. También editá el `STOCK` con tus productos y precios reales.

---

## PARTE 6 — Subir el bot a internet (Railway)

El bot necesita estar online 24/7 para recibir mensajes. Railway lo hace gratis.

1. Entrá a **railway.app** y creá una cuenta (podés entrar con GitHub)
2. Si no tenés GitHub, creá una cuenta en **github.com** primero (es gratis)
3. En Railway, hacé clic en **"New Project" > "Deploy from GitHub repo"**
4. Subí los archivos del bot a GitHub (podés usar github.com/new para crear el repo)
5. Una vez conectado, Railway detecta automáticamente que es Python
6. Hacé clic en tu proyecto > "Variables" y cargá todas las variables del `.env`
7. Railway te da una URL pública, algo como: `https://tu-bot.up.railway.app`
   — Copiá esa URL, la necesitás para el paso siguiente

---

## PARTE 7 — Conectar Instagram con tu bot (Webhook)

1. Volvé a **developers.facebook.com** > Tu App > Instagram > Webhooks
2. Hacé clic en "Configure"
3. En "Callback URL" poné: `https://tu-bot.up.railway.app/webhook`
4. En "Verify Token" poné la misma palabra que pusiste en `VERIFY_TOKEN`
5. Hacé clic en "Verify and Save"
6. Suscribite al evento: **"messages"**

¡Listo! A partir de ahora, cada vez que alguien te escriba por Instagram el bot responde solo.

---

## PARTE 8 — Actualizar el stock

Para actualizar el stock abrís el archivo `bot.py` y modificás los números en la sección `STOCK`:

```python
"1": {"nombre": "Cerveza Quilmes 1L", "precio": 2500, "stock": 20, ...},
#                                                              ↑
#                                              Cambiá este número
```

Guardá el archivo y Railway actualiza el bot automáticamente.

---

## Costos mensuales estimados

| Servicio | Costo |
|---|---|
| Railway | Gratis (hasta 500hs/mes) |
| Twilio | ~$1 USD por 100 mensajes WhatsApp |
| Google Maps | Gratis hasta 40.000 pedidos/mes |
| **Total** | **Casi $0 para empezar** |

---

## ¿Algo no funciona?

Chequeá estos puntos comunes:

- ❌ El bot no responde → Verificá que el Webhook esté configurado y que Railway esté corriendo
- ❌ No te llega el WhatsApp → Revisá que tu número esté conectado al sandbox de Twilio
- ❌ Error de token → Verificá que las variables de entorno en Railway estén bien escritas
- ❌ La demora dice siempre 45 min → Revisá que la Google Maps API Key sea correcta

---

*Cualquier duda, escribile a Claude y te ayuda a resolver el problema paso a paso 😊*
