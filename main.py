import os
import discord
from discord.ext import commands

from estructura import ROLES, ROLES_ADMIN, ESTRUCTURA

PREFIJO = "r!"
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIJO, intents=intents, help_command=None)


def construir_overwrites(acceso, guild, roles):
    everyone = guild.default_role
    acceso_total = discord.PermissionOverwrite(view_channel=True, connect=True, speak=True, send_messages=True)

    if acceso == "abierta":
        return {everyone: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)}

    overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False, connect=False),
        roles["ALG | Presidencia"]: acceso_total,
        roles["ALG | Junta Directiva"]: acceso_total,
        roles["ALG | Bot"]: acceso_total,
    }

    if acceso == "primer_equipo":
        overwrites[roles["ALG | Entrenador"]] = acceso_total
        overwrites[roles["ALG | Titular"]] = acceso_total
        overwrites[roles["ALG | Suplente"]] = acceso_total
    elif acceso == "cantera":
        overwrites[roles["ALG | Entrenador"]] = acceso_total
        overwrites[roles["ALG | Canterano"]] = acceso_total
    elif acceso == "visorias":
        overwrites[roles["ALG | Entrenador"]] = acceso_total
        overwrites[roles["ALG | Aspirante"]] = acceso_total

    return overwrites


async def borrar_todo(guild):
    errores = []

    for canal in list(guild.channels):
        try:
            await canal.delete()
        except discord.Forbidden:
            errores.append(f"No pude borrar el canal **{canal.name}**")
        except discord.HTTPException:
            pass

    for rol in list(guild.roles):
        if rol.is_default() or rol.managed:
            continue
        try:
            await rol.delete()
        except discord.Forbidden:
            errores.append(f"No pude borrar el rol **{rol.name}**")

    return errores


async def crear_estructura(guild):
    errores = []

    # 1. Crear los roles
    roles_creados = {}
    for nombre_rol in ROLES:
        permisos = discord.Permissions(administrator=True) if nombre_rol in ROLES_ADMIN else discord.Permissions.none()
        rol = await guild.create_role(name=nombre_rol, permissions=permisos, mentionable=True)
        roles_creados[nombre_rol] = rol

    # 2. Asignarle el rol de Bot al propio bot
    try:
        await guild.me.add_roles(roles_creados["ALG | Bot"])
    except discord.Forbidden:
        errores.append("No pude asignarme a mí mismo el rol **ALG | Bot**")

    # 3. Crear categorías y canales
    for datos in ESTRUCTURA:
        overwrites = construir_overwrites(datos["acceso"], guild, roles_creados)
        categoria = await guild.create_category(datos["nombre"], overwrites=overwrites)

        for canal in datos["canales"]:
            if canal["tipo"] == "voz":
                await guild.create_voice_channel(canal["nombre"], category=categoria)
            else:
                await guild.create_text_channel(canal["nombre"], category=categoria)

    return errores


class ConfirmarReset(discord.ui.View):
    def __init__(self, autor_id):
        super().__init__(timeout=60)
        self.autor_id = autor_id
        self.confirmado = None

    @discord.ui.button(label="⚠️ Sí, borrar todo y crear la estructura", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message("Solo quien ejecutó el comando puede confirmar.", ephemeral=True)
            return
        self.confirmado = True
        await interaction.response.edit_message(
            content="⏳ Borrando todo y creando la nueva estructura... esto puede tardar un minuto.",
            embed=None, view=None
        )
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message("Solo quien ejecutó el comando puede cancelar.", ephemeral=True)
            return
        self.confirmado = False
        await interaction.response.edit_message(content="❌ Operación cancelada.", embed=None, view=None)
        self.stop()


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Solo un administrador del servidor puede usar este comando.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Ocurrió un error: `{error}`")
        print(f"Error: {error}")


@bot.command(name="setup_servidor")
@commands.has_permissions(administrator=True)
async def setup_servidor(ctx):
    """Borra TODO (canales, categorías, roles) y crea la estructura completa desde cero."""
    embed = discord.Embed(
        title="⚠️ Esto va a borrar TODO el servidor",
        description=(
            "Se van a eliminar **todos** los canales, categorías y roles actuales, "
            "y se va a crear la estructura nueva desde cero.\n\n"
            "**Esta acción no se puede deshacer.**"
        ),
        color=discord.Color.red()
    )
    vista = ConfirmarReset(ctx.author.id)
    await ctx.send(embed=embed, view=vista)
    await vista.wait()

    if not vista.confirmado:
        return

    try:
        errores = await borrar_todo(ctx.guild)
        errores += await crear_estructura(ctx.guild)
    except Exception as e:
        await ctx.send(f"❌ Algo falló a mitad de camino: `{e}`\nRevisá el servidor, puede haber quedado incompleto.")
        return

    resumen = discord.Embed(
        title="✅ Estructura creada",
        description=f"Se crearon {len(ROLES)} roles, {len(ESTRUCTURA)} categorías y sus canales.",
        color=discord.Color.green()
    )
    if errores:
        resumen.add_field(name="⚠️ Avisos", value="\n".join(errores[:10]), inline=False)
    await ctx.send(embed=resumen)


bot.run(TOKEN)
