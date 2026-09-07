# -*- coding: utf-8 -*-
# Definición de toda la estructura del servidor.
# Los nombres usan caracteres unicode en negrita a propósito — son EXACTAMENTE
# los que pediste, no los cambies salvo que quieras modificar el resultado final.

ROLES = [
    "ALG | Presidencia",
    "ALG | Junta Directiva",
    "ALG | Entrenador",
    "ALG | Titular",
    "ALG | Suplente",
    "ALG | Canterano",
    "ALG | Aspirante",
    "ALG | Bot",
]

# Roles con permiso de Administrador a nivel servidor (control total)
ROLES_ADMIN = ["ALG | Presidencia", "ALG | Bot"]

ESTRUCTURA = [
    {
        "nombre": "👋 ━━━ 𝗕𝗶𝗲𝗻𝘃𝗲𝗻𝗶𝗱𝗮𝘀 𝗬 𝗗𝗲𝘀𝗽𝗲𝗱𝗶𝗱𝗮𝘀 ━━━ 👋",
        "acceso": "abierta",
        "canales": [
            {"nombre": "📥 ︱ Bienvenidas", "tipo": "texto"},
            {"nombre": "📤 ︱ Despedidas", "tipo": "texto"},
        ],
    },
    {
        "nombre": "👑 ━━━ 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝗰𝗶𝗼𝗻 𝗜𝗻𝘀𝘁𝗶𝘁𝘂𝗰𝗶𝗼𝗻𝗮𝗹 ━━━ 👑",
        "acceso": "abierta",
        "canales": [
            {"nombre": "📜 ︱ Reglas", "tipo": "texto"},
            {"nombre": "📢 ︱ Anuncios-Globales", "tipo": "texto"},
        ],
    },
    {
        "nombre": "💬 ━━━ 𝗖𝗼𝗺𝘂𝗻𝗶𝗱𝗮𝗱 𝗬 𝗩𝗲𝘀𝘁𝘂𝗮𝗿𝗶𝗼 ━━━ 💬",
        "acceso": "abierta",
        "canales": [
            {"nombre": "💬 ︱ Chat-Global", "tipo": "texto"},
            {"nombre": "🤖 ︱ Comandos", "tipo": "texto"},
        ],
    },
    {
        "nombre": "👑 ━━━ 𝗣𝗿𝗶𝗺𝗲𝗿 𝗘𝗾𝘂𝗶𝗽𝗼 ━━━ 👑",
        "acceso": "primer_equipo",
        "canales": [
            {"nombre": "📋 ︱ Alineacion-Y-Tactica", "tipo": "texto"},
            {"nombre": "📌 ︱ Convocados", "tipo": "texto"},
            {"nombre": "⚽ ︱ Partidos", "tipo": "texto"},
            {"nombre": "📊 ︱ Resultados", "tipo": "texto"},
            {"nombre": "🔊 ︱ VC-Primer-Equipo", "tipo": "voz"},
        ],
    },
    {
        "nombre": "🌱 ━━━ 𝗖𝗮𝗻𝘁𝗲𝗿𝗮 ━━━ 🌱",
        "acceso": "cantera",
        "canales": [
            {"nombre": "📢 ︱ Anuncios-Cantera", "tipo": "texto"},
            {"nombre": "⚽ ︱ Partidos-Cantera", "tipo": "texto"},
            {"nombre": "💬 ︱ Vestuario-Cantera", "tipo": "texto"},
            {"nombre": "🔊 ︱ VC-Cantera", "tipo": "voz"},
        ],
    },
    {
        "nombre": "🛡️ ━━━ 𝗩𝗶𝘀𝗼𝗿𝗶𝗮𝘀 ━━━ 🛡️",
        "acceso": "visorias",
        "canales": [
            {"nombre": "💬 ︱ Chat-Visorias", "tipo": "texto"},
            {"nombre": "✅ ︱ Seleccionados", "tipo": "texto"},
            {"nombre": "🔊 ︱ VC-Visorias", "tipo": "voz"},
        ],
    },
]
