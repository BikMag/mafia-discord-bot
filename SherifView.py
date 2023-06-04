import discord
from Player import *
from Player import game_data

players = game_data.players


class SherifButton(discord.ui.Button['ForSherif']):
    def __init__(self, player: Player, r: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=player.user.name, row=r)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        view: ForSherif = self.view

        if self.player.role == "mafia":
            await interaction.response.edit_message(content=f"Игрок {self.player.user.name} - мафия", view=None)
        else:
            await interaction.response.edit_message(content=f"Игрок {self.player.user.name} не мафия", view=None)

        view.stop()


class ForSherif(discord.ui.View):
    def __init__(self):
        super().__init__()

        civilians = []
        for player in players:
            if player.role != "sherif":
                civilians.append(player)

        for i in range(len(civilians)):
            self.add_item(SherifButton(civilians[i], i//5))


class SherifView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.vw = ForSherif()

    @discord.ui.button(label="Действие для шерифа!", style=discord.ButtonStyle.blurple)
    async def detect(self, interaction: discord.Interaction, button: discord.ui.Button):
        for player in players:
            if player.user == interaction.user and player.role == "sherif":
                await interaction.response.send_message("Кого проверить", view=self.vw, ephemeral=True)
                self.stop()
                return None

        await interaction.response.send_message("Вы не шериф, дождитесь своего хода", ephemeral=True)