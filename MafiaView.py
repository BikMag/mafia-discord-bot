import discord
from Player import *
from Player import game_data

players = game_data.players


class MafiaButton(discord.ui.Button['ForMafia']):
    def __init__(self, player: Player, r: int):
        super().__init__(style=discord.ButtonStyle.red, label=player.user.name, row=r)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        view: ForMafia = self.view

        game_data.killed_pers = self.player
        print(game_data.killed_pers.user.name)

        view.stop()
        await interaction.response.edit_message(content=f"Выбор сделан, убит {self.player.user.name}", view=None)


class ForMafia(discord.ui.View):
    def __init__(self):
        super().__init__()

        civilians = []
        for player in players:
            if player.role != "mafia":
                civilians.append(player)

        for i in range(len(civilians)):
            self.add_item(MafiaButton(civilians[i], i//5))


class MafiaView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.vw = ForMafia()

    @discord.ui.button(label="Действие для мафии!", style=discord.ButtonStyle.red)
    async def kill(self, interaction: discord.Interaction, button: discord.ui.Button):
        for player in players:
            if player.user == interaction.user and player.role == "mafia":
                await interaction.response.send_message("Кого убить", view=self.vw, ephemeral=True)
                self.stop()
                return None

        await interaction.response.send_message("Вы не мафия, дождитесь своего хода", ephemeral=True)

