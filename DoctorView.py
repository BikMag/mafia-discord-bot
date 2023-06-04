import discord
from Player import *
from Player import game_data

players = game_data.players


class DoctorButton(discord.ui.Button['ForDoctor']):
    def __init__(self, player: Player, r: int):
        super().__init__(style=discord.ButtonStyle.green, label=player.user.name, row=r)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        view: ForDoctor = self.view

        if self.player.user == game_data.killed_pers.user:
            await interaction.response.edit_message(content=f"Вы исцелили игрока {self.player.user.name}", view=None)
            game_data.healed_pers = self.player
            print(game_data.healed_pers.user.name)
        else:
            await interaction.response.edit_message(content=f"Игроку {self.player.user.name}"
                                                            f" не нужно лечение", view=None)
            game_data.healed_pers = None
            print("None")

        view.stop()


class ForDoctor(discord.ui.View):
    def __init__(self):
        super().__init__()

        civilians = []
        for player in players:
            if player.role != "doctor":
                civilians.append(player)

        for i in range(len(civilians)):
            self.add_item(DoctorButton(civilians[i], i//5))


class DoctorView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.vw = ForDoctor()

    @discord.ui.button(label="Действие для доктора!", style=discord.ButtonStyle.green)
    async def heal(self, interaction: discord.Interaction, button: discord.ui.Button):
        for player in players:
            if player.user == interaction.user and player.role == "doctor":
                await interaction.response.send_message("Кого исцелить", view=self.vw, ephemeral=True)
                self.stop()
                return None

        await interaction.response.send_message("Вы не доктор, дождитесь своего хода", ephemeral=True)