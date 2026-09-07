# -*- coding: utf-8 -*-
"""
Cog para discord.py 2.x que crea de un solo comando TODA la estructura
del servidor de la liga: roles (con colores), categorías, canales y
permisos, tal como está definida en el documento de referencia.

INSTALACIÓN
-----------
1. Copia este archivo a tu repo (por ejemplo en /cogs/setup_liga.py).
2. En tu bot principal, cárgalo con:
       await bot.load_extension("cogs.setup_liga")
   (o "setup_liga" si lo pones en la raíz).
3. Asegúrate de que tu bot tenga el permiso "Administrador" en el
   servidor, y que los intents incluyan guilds (Guild) y members si
   los usas en otro lado.
4. En el servidor, ejecuta:
       !setup_liga
   (solo lo puede correr alguien con permiso de Administrador).

IMPORTANTE - SUPUESTOS QUE HICE
--------------------------------
La matriz de permisos del documento usa nombres de grupo genéricos
("Jugadores", "DTs", "Arbitros", "Staff", "Administracion",
"Staff superior") que no coinciden 1 a 1 con los nombres exactos de
los roles ("LIGA | Jugador Primera", "LIGA | Director Tecnico / DT",
etc.). Tuve que decidir qué roles reales caen en cada grupo genérico;
mira el diccionario ROLE_GROUPS más abajo y ajústalo si algo no
calza con lo que tenías en mente.

Discord solo permite 250 roles y 500 canales por servidor, así que
esto entra sin problema. El comando es "idempotente a medias": si
corres el comando dos veces, te va a duplicar roles/canales (no
revisa si ya existen), así que úsalo una sola vez en un servidor
limpio, o bórralo todo antes de reintentar.
"""

import discord
from discord.ext import commands

# ---------------------------------------------------------------------
# 1) ROLES (nombre, color hex o None). El orden de la lista = de más
#    alto a más bajo en la jerarquía final (arriba = más poder).
#    Las entradas con color None son separadores visuales: se crean
#    SIN color (color por defecto de Discord) para que no choquen
#    con los colores reales de los roles.
# ---------------------------------------------------------------------
ROLES = [
    ("────────── 𝖠𝖣𝖬𝖨𝖭𝖨𝖲𝖳𝖱𝖠𝖢𝖨𝖮𝖭 ──────────", None),
    ("LIGA | Administrador", "#F1C40F"),
    ("LIGA | Admin Senior", "#E67E22"),
    ("LIGA | Admin", "#E74C3C"),
    ("LIGA | Asistente De Admin", "#C0392B"),

    ("────────── 𝖬𝖮𝖣𝖤𝖱𝖠𝖢𝖨𝖮𝖭 ──────────", None),
    ("LIGA | Moderador", "#3498DB"),
    ("LIGA | Moderador Senior", "#2980B9"),
    ("LIGA | Moderador En Practicas", "#5DADE2"),

    ("────────── 𝖧𝖤𝖫𝖯𝖤𝖱𝖲 ──────────", None),
    ("LIGA | Helper", "#2ECC71"),
    ("LIGA | Helper Senior", "#27AE60"),
    ("LIGA | Helper En Practicas", "#58D68D"),

    ("────────── 𝖲𝖳𝖠𝖥𝖥 ──────────", None),
    ("LIGA | Presidente Ejecutivo", "#F1C40F"),
    ("LIGA | Comite Disciplinario", "#E74C3C"),
    ("LIGA | Encargado de Fichajes", "#2ECC71"),
    ("LIGA | Arbitro Oficial", "#E67E22"),
    ("LIGA | KAR / Revisor", "#34495E"),
    ("LIGA | Prensa / Caster", "#9B59B6"),
    ("LIGA | Bot", "#131416"),

    ("────────── 𝖣𝖨𝖱𝖤𝖢𝖢𝖨𝖮𝖭 𝖸 𝖬𝖠𝖭𝖣𝖮 ──────────", None),
    ("LIGA | Director Tecnico / DT", "#1ABC9C"),
    ("LIGA | Jugador Primera", "#F5F5F5"),
    ("LIGA | Jugador Segunda", "#BDC3C7"),
    ("LIGA | Agente Libre", "#7F8C8D"),

    ("────────── 𝟣𝖣 | 𝖯𝖱𝖨𝖬𝖤𝖱𝖠 𝖣𝖨𝖵𝖨𝖲𝖨𝖮𝖭 ──────────", None),
    ("LIGA | 1D | Real Madrid", "#F5F5F5"),
    ("LIGA | 1D | FC Barcelona", "#3498DB"),
    ("LIGA | 1D | Bayern Munchen", "#E74C3C"),
    ("LIGA | 1D | Manchester City", "#74B9FF"),
    ("LIGA | 1D | Liverpool FC", "#C0392B"),
    ("LIGA | 1D | Paris Saint-Germain", "#2980B9"),
    ("LIGA | 1D | Juventus", "#111111"),
    ("LIGA | 1D | Inter de Milan", "#1F4E9E"),
    ("LIGA | 1D | Arsenal FC", "#D63031"),
    ("LIGA | 1D | Atletico de Madrid", "#E74C3C"),
    ("LIGA | 1D | Borussia Dortmund", "#F1C40F"),
    ("LIGA | 1D | Bayer Leverkusen", "#D63031"),
    ("LIGA | 1D | Flamengo", "#111111"),
    ("LIGA | 1D | River Plate", "#F5F5F5"),
    ("LIGA | 1D | Boca Juniors", "#F1C40F"),
    ("LIGA | 1D | Palmeiras", "#27AE60"),

    ("────────── 𝟤𝖣 | 𝖲𝖤𝖦𝖴𝖭𝖣𝖠 𝖣𝖨𝖵𝖨𝖲𝖨𝖮𝖭 ──────────", None),
    ("LIGA | 2D | AC Milan", "#C0392B"),
    ("LIGA | 2D | Chelsea FC", "#2980B9"),
    ("LIGA | 2D | Manchester United", "#C0392B"),
    ("LIGA | 2D | SL Benfica", "#E74C3C"),
    ("LIGA | 2D | FC Porto", "#2980B9"),
    ("LIGA | 2D | Ajax", "#E74C3C"),
    ("LIGA | 2D | Sporting CP", "#27AE60"),
    ("LIGA | 2D | Sevilla FC", "#E74C3C"),
    ("LIGA | 2D | AS Roma", "#C0392B"),
    ("LIGA | 2D | SS Lazio", "#74B9FF"),
    ("LIGA | 2D | Olympique Marseille", "#3498DB"),
    ("LIGA | 2D | Aston Villa", "#7A263A"),
    ("LIGA | 2D | Tottenham Hotspur", "#ECF0F1"),
    ("LIGA | 2D | Independiente", "#E74C3C"),
    ("LIGA | 2D | Club America", "#DDE000"),
    ("LIGA | 2D | Tigres UANL", "#F1C40F"),

    ("────────── 𝖱𝖤𝖢𝖮𝖭𝖮𝖢𝖨𝖬𝖨𝖤𝖭𝖳𝖮𝖲 ──────────", None),
    ("LIGA | MVP de la Semana", "#F39C12"),
    ("LIGA | Campeon de Liga", "#F1C40F"),
    ("LIGA | Campeon de Copa", "#E74C3C"),
    ("LIGA | Leyenda / Hall of Fame", "#9B59B6"),
]

# ---------------------------------------------------------------------
# 2) MAPEO de los nombres genéricos de la matriz de permisos a los
#    roles reales que sí existen. AJUSTA ESTO si no te calza.
# ---------------------------------------------------------------------
ROLE_GROUPS = {
    "Jugadores": ["LIGA | Jugador Primera", "LIGA | Jugador Segunda"],
    "DTs": ["LIGA | Director Tecnico / DT"],
    "Arbitros": ["LIGA | Arbitro Oficial"],
    "Staff": [
        "LIGA | Moderador", "LIGA | Moderador Senior", "LIGA | Moderador En Practicas",
        "LIGA | Helper", "LIGA | Helper Senior", "LIGA | Helper En Practicas",
    ],
    "Administracion": [
        "LIGA | Administrador", "LIGA | Admin Senior",
        "LIGA | Admin", "LIGA | Asistente De Admin",
    ],
    "Staff superior": [
        "LIGA | Presidente Ejecutivo", "LIGA | Administrador", "LIGA | Admin Senior",
    ],
    "Prensa / Caster": ["LIGA | Prensa / Caster"],
    "Comite Disciplinario": ["LIGA | Comite Disciplinario"],
    "Encargado de Fichajes": ["LIGA | Encargado de Fichajes"],
}

# ---------------------------------------------------------------------
# 3) NIVELES de permiso reutilizables. "texto" y "voz" se combinan
#    automáticamente según el tipo de canal.
# ---------------------------------------------------------------------
def ow(**kwargs):
    return discord.PermissionOverwrite(**kwargs)

NIVELES = {
    "sin_acceso": ow(view_channel=False),
    "ver": ow(view_channel=True, send_messages=False, connect=False),
    "ver_escribir": ow(view_channel=True, send_messages=True, read_message_history=True),
    "ver_publicar": ow(view_channel=True, send_messages=True, embed_links=True, attach_files=True),
    "escribir_gestionar": ow(view_channel=True, send_messages=True, manage_messages=True),
    "gestion_total": ow(view_channel=True, send_messages=True, manage_messages=True,
                         manage_channels=True, manage_permissions=True),
    "administrar": ow(view_channel=True, send_messages=True, manage_messages=True),
    "publicar_resultados": ow(view_channel=True, send_messages=True, embed_links=True),
    "escribir_transmitir": ow(view_channel=True, send_messages=True, connect=True,
                               speak=True, stream=True),
    "conectar_hablar": ow(view_channel=True, connect=True, speak=True),
    "transmitir": ow(view_channel=True, connect=True, speak=True, stream=True),
    "moderar_controlar": ow(view_channel=True, connect=True, speak=True,
                             mute_members=True, move_members=True, manage_channels=True),
}

# ---------------------------------------------------------------------
# 4) CATEGORÍAS Y CANALES.
#    Cada canal: (nombre, "texto" | "voz")
#    Cada categoría trae también su matriz de permisos:
#    lista de (nombre_de_rol_o_grupo, nivel)
# ---------------------------------------------------------------------
CATEGORIAS = [
    {
        "nombre": "👋 ━━━ 𝖡𝗂𝖾𝗇𝗏𝖾𝗇𝗂𝖽𝖺𝗌 𝖸 𝖱𝖾𝗀𝗅𝖺𝗆𝖾𝗇𝗍𝗈 ━━━ 👋",
        "canales": [
            ("📥 ︱ 𝖡𝗂𝖾𝗇𝗏𝖾𝗇𝗂𝖽𝖺𝗌", "texto"),
            ("📤 ︱ 𝖣𝖾𝗌𝗉𝖾𝖽𝗂𝖽𝖺𝗌", "texto"),
            ("📜 ︱ 𝖱𝖾𝗀𝗅𝖺𝗆𝖾𝗇𝗍𝗈-𝖮𝖿𝗂𝖼𝗂𝖺𝗅", "texto"),
            ("📌 ︱ 𝖦𝗎𝗂𝖺𝗌-𝖸-𝖳𝗎𝗍𝗈𝗋𝗂𝖺𝗅𝖾𝗌", "texto"),
            ("❓ ︱ 𝖠𝗒𝗎𝖽𝖺𝗌-𝖸-𝖲𝗈𝗉𝗈𝗋𝗍𝖾", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Arbitros", "ver"),
            ("Staff", "ver_escribir"),
            ("Staff superior", "gestion_total"),
        ],
    },
    {
        "nombre": "📢 ━━━ 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝖼𝗂𝗈𝗇 𝖮𝖿𝗂𝖼𝗂𝖺𝗅 ━━━ 📢",
        "canales": [
            ("📢 ︱ 𝖠𝗇𝗎𝗇𝖼𝗂𝗈𝗌-𝖣𝖾-𝖫𝖺-𝖫𝗂𝗀𝖺", "texto"),
            ("📅 ︱ 𝖢𝖺𝗅𝖾𝗇𝖽𝖺𝗋𝗂𝗈-𝖦𝖾𝗇𝖾𝗋𝖺𝗅", "texto"),
            ("🧑‍⚖️ ︱ 𝖡𝗈𝗅𝖾𝗍𝗂𝗇-𝖲𝖺𝗇𝖼𝗂𝗈𝗇𝖾𝗌", "texto"),
            ("🏆 ︱ 𝖯𝗋𝖾𝗆𝗂𝗈𝗌-𝖸-𝖯𝗋𝖾𝗆𝗂𝗈𝗌-𝖬𝖾𝗍𝖺", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Staff", "escribir_gestionar"),
            ("Administracion", "gestion_total"),
        ],
    },
    {
        "nombre": "🔒 ━━━ 𝖢𝗈𝗆𝗂𝗍𝖾 𝖸 𝖣𝗂𝗋𝖾𝖼𝗍𝗂𝗏𝗈𝗌 ━━━ 🔒",
        "canales": [
            ("📌 ︱ 𝖠𝗏𝗂𝗌𝗈𝗌-𝖯𝖺𝗋𝖺-𝖣𝖳𝗌", "texto"),
            ("💬 ︱ 𝖢𝗎𝗆𝖻𝗋𝖾-𝖣𝖾-𝖯𝗋𝖾𝗌𝗂𝖽𝖾𝗇𝗍𝖾𝗌", "texto"),
            ("🤝 ︱ 𝖯𝖺𝖼𝗍𝗈𝗌-𝖸-𝖭𝖾𝗀𝗈𝖼𝗂𝖺𝖼𝗂𝗈𝗇𝖾𝗌", "texto"),
            ("🗳️ ︱ 𝖵𝗈𝗍𝖺𝖼𝗂𝗈𝗇𝖾𝗌-𝖫𝗂𝗀𝖺", "texto"),
            ("🚨 ︱ 𝖲𝗈𝗉𝗈𝗋𝗍𝖾-𝖸-𝖱𝖾𝖼𝗅𝖺𝗆𝗈𝗌-𝖣𝖳", "texto"),
            ("🔊 ︱ 𝖪𝖢-𝖲𝖾𝖽𝖾-𝖯𝗋𝖾𝗌𝗂𝖽𝖾𝗇𝗍𝖾𝗌", "voz"),
        ],
        "permisos": [
            ("@everyone", "sin_acceso"),
            ("Jugadores", "sin_acceso"),
            ("DTs", "ver"),
            ("Arbitros", "sin_acceso"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "💬 ━━━ 𝖢𝗈𝗆𝗎𝗇𝗂𝖽𝖺𝖽 ━━━ 💬",
        "canales": [
            ("💬 ︱ 𝖢𝗁𝖺𝗍-𝖦𝗅𝗈𝖻𝖺𝗅", "texto"),
            ("🤖 ︱ 𝖢𝗈𝗆𝖺𝗇𝖽𝗈𝗌-𝖡𝗈𝗍", "texto"),
            ("🥊 ︱ 𝖣𝖾𝖻𝖺𝗍𝖾𝗌-𝖸-𝖯𝗂𝖼𝖺𝗇𝗍𝖾", "texto"),
            ("🎮 ︱ 𝖡𝗎𝗌𝖼𝗈-𝖯𝖺𝗋𝗍𝗂𝖽𝗈-𝖮𝖮𝖢", "texto"),
            ("🔊 ︱ 𝖪𝖢-𝖢𝗈𝗆𝗎𝗇𝗂𝖽𝖺𝖽", "voz"),
        ],
        "permisos": [
            ("@everyone", "ver_escribir"),
            ("Jugadores", "ver_escribir"),
            ("DTs", "ver_escribir"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "📺 ━━━ 𝖳𝖾𝗅𝖾𝗏𝗂𝗌𝗂𝗈𝗇 𝖸 𝖬𝖾𝖽𝗂𝗈𝗌 ━━━ 📺",
        "canales": [
            ("🎥 ︱ 𝖳𝗋𝖺𝗇𝗌𝗆𝗂𝗌𝗂𝗈𝗇𝖾𝗌-𝖤𝗇-𝖵𝗂𝗏𝗈", "texto"),
            ("🎙️ ︱ 𝖱𝗎𝖾𝖽𝖺𝗌-𝖣𝖾-𝖯𝗋𝖾𝗇𝗌𝖺", "texto"),
            ("📹 ︱ 𝖬𝖾𝗃𝗈𝗋𝖾𝗌-𝖩𝗎𝗀𝖺𝖽𝖺𝗌-𝖢𝗅𝗂𝗉𝗌", "texto"),
            ("📰 ︱ 𝖭𝗈𝗍𝗂𝖼𝗂𝖺𝗌-𝖸-𝖣𝗂𝖺𝗋𝗂𝗈𝗌", "texto"),
            ("📻 ︱ 𝖯𝗈𝖽𝖼𝖺𝗌𝗍-𝖸-𝖣𝖾𝖻𝖺𝗍𝖾-𝖤𝗌𝗉𝖾𝖼𝗂𝖺𝗅", "texto"),
            ("🔊 ︱ 𝖪𝖢-𝖲𝖾𝗍-𝖣𝖾-𝖳𝗋𝖺𝗇𝗌𝗆𝗂𝗌𝗂𝗈𝗇", "voz"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("Prensa / Caster", "escribir_transmitir"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "📝 ━━━ 𝖬𝖾𝗋𝖼𝖺𝖽𝗈 𝖣𝖾 𝖥𝗂𝖼𝗁𝖺𝗃𝖾𝗌 ━━━ 📝",
        "canales": [
            ("📋 ︱ 𝖠𝗀𝖾𝗇𝖼𝗂𝖺-𝖫𝗂𝖻𝗋𝖾-𝖩𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌", "texto"),
            ("💼 ︱ 𝖮𝖿𝖾𝗋𝗍𝖺𝗌-𝖸-𝖳𝗋𝖺𝗌𝗉𝖺𝗌𝗈𝗌", "texto"),
            ("✅ ︱ 𝖥𝗂𝖼𝗁𝖺𝗃𝖾𝗌-𝖢𝗈𝗇𝖿𝗂𝗋𝗆𝖺𝖽𝗈𝗌", "texto"),
            ("❌ ︱ 𝖡𝖺𝗃𝖺𝗌-𝖣𝖾-𝖯𝗅𝖺𝗇𝗍𝗂𝗅𝗅𝖺", "texto"),
            ("🔍 ︱ 𝖡𝗎𝗌𝖼𝗈-𝖤𝗊𝗎𝗂𝗉𝗈", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver_publicar"),
            ("DTs", "ver_escribir"),
            ("Encargado de Fichajes", "gestion_total"),
        ],
    },
    {
        "nombre": "🏆 ━━━ 𝖫𝗂𝗀𝖺 𝖯𝗋𝗂𝗇𝖼𝗂𝗉𝖺𝗅 (𝟣𝗌𝗍 𝖣𝗂𝗏) ━━━ 🏆",
        "canales": [
            ("📌 ︱ 𝖠𝗏𝗂𝗌𝗈𝗌-𝖯𝗋𝗂𝗆𝖾𝗋𝖺", "texto"),
            ("📊 ︱ 𝖳𝖺𝖻𝗅𝖺-𝖣𝖾-𝖯𝗈𝗌𝗂𝖼𝗂𝗈𝗇𝖾𝗌-𝟣𝗌𝗍", "texto"),
            ("⚽ ︱ 𝖱𝖾𝗌𝗎𝗅𝗍𝖺𝖽𝗈𝗌-𝖩𝗈𝗋𝗇𝖺𝖽𝖺𝗌-𝟣𝗌𝗍", "texto"),
            ("⚽ ︱ 𝖯𝗋𝗈𝗀𝗋𝖺𝗆𝖺𝖼𝗂𝗈𝗇-𝖯𝖺𝗋𝗍𝗂𝖽𝗈𝗌-𝟣𝗌𝗍", "texto"),
            ("🎯 ︱ 𝖳𝖺𝖻𝗅𝖺-𝖦𝗈𝗅𝖾𝖺𝖽𝗈𝗋𝖾𝗌-𝟣𝗌𝗍", "texto"),
            ("🅰️ ︱ 𝖳𝖺𝖻𝗅𝖺-𝖠𝗌𝗂𝗌𝗍𝖾𝗇𝖼𝗂𝖺𝗌-𝟣𝗌𝗍", "texto"),
            ("🧤 ︱ 𝖦𝗎𝖺𝗇𝗍𝖾-𝖣𝖾-𝖮𝗋𝗈-𝟣𝗌𝗍", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Arbitros", "publicar_resultados"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "🥈 ━━━ 𝖲𝖾𝗀𝗎𝗇𝖽𝖺 𝖣𝗂𝗏𝗂𝗌𝗂𝗈𝗇 (𝟤𝗇𝖽 𝖣𝗂𝗏) ━━━ 🥈",
        "canales": [
            ("📌 ︱ 𝖠𝗏𝗂𝗌𝗈𝗌-𝖲𝖾𝗀𝗎𝗇𝖽𝖺", "texto"),
            ("📊 ︱ 𝖳𝖺𝖻𝗅𝖺-𝖣𝖾-𝖯𝗈𝗌𝗂𝖼𝗂𝗈𝗇𝖾𝗌-𝟤𝗇𝖽", "texto"),
            ("⚽ ︱ 𝖱𝖾𝗌𝗎𝗅𝗍𝖺𝖽𝗈𝗌-𝖩𝗈𝗋𝗇𝖺𝖽𝖺𝗌-𝟤𝗇𝖽", "texto"),
            ("⚽ ︱ 𝖯𝗋𝗈𝗀𝗋𝖺𝗆𝖺𝖼𝗂𝗈𝗇-𝖯𝖺𝗋𝗍𝗂𝖽𝗈𝗌-𝟤𝗇𝖽", "texto"),
            ("🎯 ︱ 𝖳𝖺𝖻𝗅𝖺-𝖦𝗈𝗅𝖾𝖺𝖽𝗈𝗋𝖾𝗌-𝟤𝗇𝖽", "texto"),
            ("🅰️ ︱ 𝖳𝖺𝖻𝗅𝖺-𝖠𝗌𝗂𝗌𝗍𝖾𝗇𝖼𝗂𝖺𝗌-𝟤𝗇𝖽", "texto"),
            ("🧤 ︱ 𝖦𝗎𝖺𝗇𝗍𝖾-𝖣𝖾-𝖮𝗋𝗈-𝟤𝗇𝖽", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Arbitros", "publicar_resultados"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "📈 ━━━ 𝖹𝗈𝗇𝖺 𝖣𝖾 𝖠𝗌𝖼𝖾𝗇𝗌𝗈 𝖸 𝖣𝖾𝗌𝖼𝖾𝗇𝗌𝗈 ━━━ 📈",
        "canales": [
            ("📉 ︱ 𝖢𝖺𝗅𝖼𝗎𝗅𝖺𝖽𝗈𝗋𝖺-𝖯𝗋𝗈𝗆𝖾𝖽𝗂𝗈𝗌", "texto"),
            ("⚔️ ︱ 𝖯𝗋𝗈𝗆𝗈𝖼𝗂𝗈𝗇-𝖯𝗅𝖺𝗒𝗈𝖿𝖿𝗌", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver_escribir"),
            ("Staff", "ver_escribir"),
        ],
    },
    {
        "nombre": "🥊 ━━━ 𝖢𝗈𝗉𝖺 𝖨𝗇𝗍𝖾𝗋𝗇𝖺𝖼𝗂𝗈𝗇𝖺𝗅 ━━━ 🥊",
        "canales": [
            ("📜 ︱ 𝖥𝗈𝗋𝗆𝖺𝗍𝗈-𝖸-𝖱𝖾𝗀𝗅𝖺𝗌-𝖢𝗈𝗉𝖺", "texto"),
            ("🥊 ︱ 𝖫𝗅𝖺𝗏𝖾𝗌-𝖸-𝖲𝗈𝗋𝗍𝖾𝗈", "texto"),
            ("⚽ ︱ 𝖱𝖾𝗌𝗎𝗅𝗍𝖺𝖽𝗈𝗌-𝖢𝗈𝗉𝖺", "texto"),
            ("🏆 ︱ 𝖡𝖺𝗅𝖾𝗋𝗂𝖺-𝖣𝖾-𝖢𝖺𝗆𝗉𝖾𝗈𝗇𝖾𝗌", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Arbitros", "ver_escribir"),
            ("Staff", "gestion_total"),
        ],
    },
    {
        "nombre": "🎖️ ━━━ 𝖱𝖾𝖼𝗈𝗇𝗈𝖼𝗂𝗆𝗂𝖾𝗇𝗍𝗈𝗌 𝖸 𝖯𝗋𝖾𝗆𝗂𝗈𝗌 ━━━ 🎖️",
        "canales": [
            ("🌟 ︱ 𝖤𝗊𝗎𝗂𝗉𝗈-𝖣𝖾-𝖫𝖺-𝖲𝖾𝗆𝖺𝗇𝖺-𝖳𝖮𝖳𝖶", "texto"),
            ("🎖️ ︱ 𝖩𝗎𝗀𝖺𝖽𝗈𝗋-𝖣𝖾𝗅-𝖬𝖾𝗌-𝖯𝖮𝖳𝖬", "texto"),
            ("🏆 ︱ 𝖢𝗎𝖺𝖽𝗋𝗈-𝖣𝖾-𝖧𝗈𝗇𝗈𝗋", "texto"),
            ("🏛️ ︱ 𝖲𝖺𝗅𝗈𝗇-𝖣𝖾-𝖫𝖺-𝖥𝖺𝗆𝖺", "texto"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "ver"),
            ("DTs", "ver"),
            ("Staff", "escribir_gestionar"),
        ],
    },
    {
        "nombre": "🏟️ ━━━ 𝖢𝖺𝗇𝖼𝗁𝖺𝗌 𝖸 𝖤𝗌𝗍𝖺𝖽𝗂𝗈𝗌 ━━━ 🏟️",
        "canales": [
            ("🔊 ︱ 𝖤𝗌𝗍𝖺𝖽𝗂𝗈-𝟣-𝖮𝖿𝗂𝖼𝗂𝖺𝗅", "voz"),
            ("🔊 ︱ 𝖤𝗌𝗍𝖺𝖽𝗂𝗈-𝟤-𝖮𝖿𝗂𝖼𝗂𝖺𝗅", "voz"),
            ("🔊 ︱ 𝖤𝗌𝗍𝖺𝖽𝗂𝗈-𝟥-𝖮𝖿𝗂𝖼𝗂𝖺𝗅", "voz"),
            ("🔊 ︱ 𝖤𝗌𝗍𝖺𝖽𝗂𝗈-𝟦-𝖮𝖿𝗂𝖼𝗂𝖺𝗅", "voz"),
            ("🔊 ︱ 𝖢𝖺𝖻𝗂𝗇𝖺-𝖣𝖾-𝖢𝖺𝗌𝗍𝖾𝗋𝗌", "voz"),
        ],
        "permisos": [
            ("@everyone", "ver"),
            ("Jugadores", "conectar_hablar"),
            ("DTs", "conectar_hablar"),
            ("Prensa / Caster", "transmitir"),
            ("Staff", "moderar_controlar"),
        ],
    },
    {
        "nombre": "🧑‍⚖️ ━━━ 𝖹𝗈𝗇𝖺 𝖠𝗋𝖻𝗂𝗍𝗋𝖺𝗅 𝖸 𝖢𝗈𝗆𝗂𝗍𝖾 ━━━ 🧑‍⚖️",
        "canales": [
            ("📝 ︱ 𝖱𝖾𝗉𝗈𝗋𝗍𝖾-𝖯𝗈𝗌𝗍-𝖯𝖺𝗋𝗍𝗂𝖽𝗈", "texto"),
            ("🎥 ︱ 𝖱𝖾𝗏𝗂𝗌𝗂𝗈𝗇-𝖪𝖠𝖱-𝖸-𝖰𝗎𝖾𝗃𝖺𝗌", "texto"),
            ("💬 ︱ 𝖢𝗁𝖺𝗍-𝖠𝗋𝖻𝗂𝗍𝗋𝗈𝗌", "texto"),
            ("🔊 ︱ 𝖪𝖢-𝖱𝖾𝗎𝗇𝗂𝗈𝗇-𝖠𝗋𝖻𝗂𝗍𝗋𝖺𝗅", "voz"),
        ],
        "permisos": [
            ("@everyone", "sin_acceso"),
            ("Jugadores", "sin_acceso"),
            ("DTs", "sin_acceso"),
            ("Arbitros", "ver_escribir"),
            ("Comite Disciplinario", "ver_escribir"),
            ("Staff", "gestion_total"),
        ],
    },
]


class SetupLiga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _resolve_roles(self, guild: discord.Guild, nombre_o_grupo: str):
        """Devuelve la lista de objetos discord.Role para un nombre de
        rol real, un nombre de grupo genérico, o @everyone."""
        if nombre_o_grupo == "@everyone":
            return [guild.default_role]
        if nombre_o_grupo in ROLE_GROUPS:
            nombres = ROLE_GROUPS[nombre_o_grupo]
        else:
            nombres = [nombre_o_grupo]
        roles = []
        for n in nombres:
            r = discord.utils.get(guild.roles, name=n)
            if r:
                roles.append(r)
        return roles

    @commands.command(name="setup_liga")
    @commands.has_permissions(administrator=True)
    async def setup_liga(self, ctx: commands.Context):
        guild = ctx.guild
        msg = await ctx.send("⏳ Borrando roles antiguos de la liga...")

        # --- 0. Borrar los roles de la liga que ya existan, para
        #         recrearlos limpios en el orden correcto ---
        nombres_liga = {nombre for nombre, _ in ROLES}
        for rol in list(guild.roles):
            if rol.name in nombres_liga:
                try:
                    await rol.delete(reason="Recreando roles de la liga en el orden correcto")
                except discord.Forbidden:
                    pass

        await msg.edit(content="⏳ Creando roles nuevos...")

        # --- 1. Crear roles en el orden normal de la lista.
        #         Discord inserta cada rol nuevo justo encima de
        #         @everyone y empuja hacia arriba a los ya creados,
        #         así que crear en este orden deja el primero de la
        #         lista (arriba) como el más alto en la jerarquía. ---
        creados = {}
        for nombre, color_hex in ROLES:
            # Separadores visuales: sin color (color por defecto) para
            # que no choquen con los colores reales de los roles.
            if color_hex is None:
                color = discord.Color.default()
            else:
                color = discord.Color(int(color_hex.replace("#", ""), 16))

            rol = await guild.create_role(
                name=nombre,
                color=color,
                hoist=False,
                mentionable=False,
                reason="Setup automático de liga",
            )
            creados[nombre] = rol

        await msg.edit(content="⏳ Roles listos. Creando categorías y canales...")

        # --- 2. Crear categorías + canales con sus permisos ---
        for cat in CATEGORIAS:
            overwrites = {}
            for nombre_rol, nivel in cat["permisos"]:
                roles = self._resolve_roles(guild, nombre_rol)
                for r in roles:
                    overwrites[r] = NIVELES[nivel]

            categoria = await guild.create_category(
                name=cat["nombre"],
                overwrites=overwrites,
                reason="Setup automático de liga",
            )

            for nombre_canal, tipo in cat["canales"]:
                if tipo == "voz":
                    await guild.create_voice_channel(
                        name=nombre_canal, category=categoria, overwrites=overwrites
                    )
                else:
                    await guild.create_text_channel(
                        name=nombre_canal, category=categoria, overwrites=overwrites
                    )

        await msg.edit(content="✅ ¡Listo! Servidor de liga creado por completo.")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupLiga(bot))
