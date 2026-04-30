import discord
from discord.ext import commands
import asyncio
from database import supabase, DISCORD_TOKEN, ID_CANAL_PLATINO

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class DecisionPlatino(discord.ui.View):
    def __init__(self, datos):
        super().__init__(timeout=120) # 2 minutos de vida para los botones
        self.datos = datos
        self.procesado = False

    @discord.ui.button(label="Quedármelo (Privado)", style=discord.ButtonStyle.danger)
    async def privado(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.procesado = True
        await interaction.response.send_message(f"✅ Has marcado {self.datos['item_id']} como PRIVADO.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Liberar a Oro", style=discord.ButtonStyle.success)
    async def liberar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.procesado = True
        # Aquí podrías añadir lógica para actualizar Supabase si quisieras
        await interaction.response.send_message(f"🔓 {self.datos['item_id']} liberado a la web como ORO.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        if not self.procesado:
            # Si pasan 2 min y no tocaste nada, se considera liberado
            print(f"⏰ Tiempo agotado para {self.datos['item_id']}. Se libera automáticamente.")

@bot.event
async def on_ready():
    print(f'✅ Bot Platino conectado como {bot.user}')

# ESTA ES LA FUNCIÓN QUE TE FALTABA
async def enviar_alerta_platino(datos):
    """Llamada desde market_service.py para enviar el mensaje con botones"""
    canal = bot.get_channel(int(ID_CANAL_PLATINO))
    if canal:
        embed = discord.Embed(
            title="💎 ¡NUEVA OPORTUNIDAD PLATINO!",
            description=f"Se ha detectado un margen masivo en **{datos['city']}**",
            color=0x9b59b6
        )
        embed.add_field(name="Objeto", value=datos['item_id'], inline=True)
        embed.add_field(name="Profit", value=f"{datos['profit']:,} Silver", inline=True)
        embed.set_footer(text="Tienes 2 minutos para decidir antes de que se libere a Oro.")
        
        view = DecisionPlatino(datos)
        await canal.send(embed=embed, view=view)
    else:
        print("❌ Error: No se encontró el canal de Discord. Revisa el ID en connection.py")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)