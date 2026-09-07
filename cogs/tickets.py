# -*- coding: utf-8 -*-
"""
Sistema de tickets.

COMANDOS
--------
!create_ticket
    Publica el embed con el botón "Crear Ticket 🎫" en el canal donde
    lo ejecutes. Solo lo puede correr alguien con "Manage Channels".

!add_ticket @usuario
    Se usa DENTRO de un canal de ticket. Le da acceso a ese usuario
    al ticket (por ejemplo, para que el reportado pueda defenderse).

FLUJO
-----
1. Usuario presiona "Crear Ticket 🎫"
2. Le aparece (solo a él) un menú "Elegir tipo de ayuda" donde puede
   marcar una o varias opciones.
3. Al confirmar, se abre un modal "Describa su problema".
4. Al enviar el modal, se crea un canal privado visible solo para:
   Admins / Mods / Helpers + quien abrió el ticket.

AJUSTA ESTO A TU SERVIDOR
--------------------------
- STAFF_ROLE_NAMES: nombres EXACTOS de los roles que deben poder ver
  todos los tickets.
- TICKET_CATEGORY_NAME: la categoría donde se van a crear los canales
  de ticket (se crea sola si no existe).
"""

import re
import asyncio

import discord
from discord.ext import commands

TICKET_CATEGORY_NAME = "🎫 ━━━ TICKETS ━━━ 🎫"

STAFF_ROLE_NAMES = [
    "LIGA | Administrador",
    "LIGA | Admin Senior",
    "LIGA | Admin",
    "LIGA | Asistente De Admin",
    "LIGA | Moderador",
    "LIGA | Moderador Senior",
    "LIGA | Moderador En Practicas",
    "LIGA | Helper",
    "LIGA | Helper Senior",
    "LIGA | Helper En Practicas",
]

TIPOS_AYUDA = [
    discord.SelectOption(label="Reportar usuario", emoji="⚠️", value="reportar_usuario"),
    discord.SelectOption(label="Alianzas", emoji="🤝", value="alianzas"),
    discord.SelectOption(label="Apelaciones", emoji="📢", value="apelaciones"),
    discord.SelectOption(label="Otros", emoji="❓", value="otros"),
    discord.SelectOption(label="Pedir club", emoji="👨🏼‍💼", value="pedir_club"),
]


def _slug(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto[:20] or "usuario"


def _staff_overwrites(guild: discord.Guild):
    overwrites = {}
    for nombre_rol in STAFF_ROLE_NAMES:
        rol = discord.utils.get(guild.roles, name=nombre_rol)
        if rol:
            overwrites[rol] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
    return overwrites


class DescribirProblemaModal(discord.ui.Modal, title="Describe tu problema"):
    descripcion = discord.ui.TextInput(
        label="Describa su problema",
        style=discord.TextStyle.paragraph,
        placeholder="Cuéntanos qué pasó con el mayor detalle posible...",
        max_length=1000,
        required=True,
    )

    def __init__(self, tipos_seleccionados):
        super().__init__(timeout=300)
        self.tipos_seleccionados = tipos_seleccionados

    async def on_submit(self, interaction: discord.Interaction):
        await crear_canal_ticket(interaction, self.tipos_seleccionados, str(self.descripcion))


class TipoAyudaSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Elegir tipo de ayuda",
            min_values=1,
            max_values=len(TIPOS_AYUDA),
            options=TIPOS_AYUDA,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DescribirProblemaModal(self.values))


class TipoAyudaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(TipoAyudaSelect())


class CerrarTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cerrar Ticket", emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="liga:cerrar_ticket_btn",
    )
    async def cerrar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Cerrando este ticket en 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket cerrado por {interaction.user}")


async def crear_canal_ticket(interaction: discord.Interaction, tipos, descripcion: str):
    guild = interaction.guild
    autor = interaction.user

    categoria = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if categoria is None:
        categoria = await guild.create_category(TICKET_CATEGORY_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        autor: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    overwrites.update(_staff_overwrites(guild))

    canal = await guild.create_text_channel(
        name=f"ticket-{_slug(autor.display_name)}",
        category=categoria,
        overwrites=overwrites,
        reason=f"Ticket abierto por {autor}",
    )

    tipos_legibles = ", ".join(
        next((o.label for o in TIPOS_AYUDA if o.value == v), v) for v in tipos
    )

    embed = discord.Embed(
        title="🎫 Nuevo ticket",
        description=descripcion,
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Abierto por", value=autor.mention, inline=True)
    embed.add_field(name="Tipo de ayuda", value=tipos_legibles, inline=True)
    embed.set_footer(text="Un miembro del staff te atenderá pronto.")

    menciones_staff = [
        f"<@&{r.id}>" for r in (
            discord.utils.get(guild.roles, name=n) for n in STAFF_ROLE_NAMES
        ) if r
    ]

    await canal.send(
        content=f"{autor.mention} " + " ".join(menciones_staff),
        embed=embed,
        view=CerrarTicketView(),
    )
    await interaction.response.send_message(f"✅ Tu ticket fue creado: {canal.mention}", ephemeral=True)


class CrearTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistente entre reinicios

    @discord.ui.button(
        label="Crear Ticket", emoji="🎫",
        style=discord.ButtonStyle.blurple,
        custom_id="liga:crear_ticket_btn",
    )
    async def crear_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "**Elegir tipo de ayuda**\nPuedes seleccionar más de una opción si lo necesitas.",
            view=TipoAyudaView(),
            ephemeral=True,
        )


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Registra las vistas como persistentes para que los botones
        # sigan funcionando aunque el bot se reinicie.
        bot.add_view(CrearTicketView())
        bot.add_view(CerrarTicketView())

    @commands.command(name="create_ticket")
    @commands.has_permissions(manage_channels=True)
    async def create_ticket(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎫 Soporte / Tickets",
            description="Presiona aquí si quieres sacar ticket",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=CrearTicketView())

    @commands.command(name="add_ticket")
    async def add_ticket(self, ctx: commands.Context, miembro: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("⚠️ Este comando solo se puede usar dentro de un canal de ticket.")
        await ctx.channel.set_permissions(
            miembro, view_channel=True, send_messages=True, read_message_history=True
        )
        await ctx.send(f"✅ {miembro.mention} fue agregado a este ticket.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
