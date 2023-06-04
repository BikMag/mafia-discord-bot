import discord
from Player import *
from Player import game_data
import configs

players = game_data.players


class JoinView(discord.ui.View):
    def __init__(self, text):
        super().__init__()
        self.text = text

        game_data.players.clear()

    def disable(self):
        for child in self.children:  # loop through all the children of the view
            child.disabled = True

    @discord.ui.button(label='Присоединиться', style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(players) >= 10:
            await interaction.response.send_message("Макс. число игроков достигнуто")
        elif interaction.user not in [player.user for player in players] or configs.ONE_PLAYER:
            players.append(Player(interaction.user, len(players)))

            content = self.text + game_data.get_players()

            await interaction.response.edit_message(content=content, view=self)
        else:
            await interaction.response.send_message("Вы уже в присоединились", ephemeral=True)

    @discord.ui.button(label="Начать игру!", style=discord.ButtonStyle.green)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(players) >= 4:
            self.disable()
            await interaction.response.edit_message(content="Игра началась!", view=None)
            self.stop()
        else:
            await interaction.response.send_message("Недостаточно игроков, должно быть мин. 4")


class VoteButton(discord.ui.Button['VoteView']):
    def __init__(self, player: Player, r: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=player.user.name, row=r)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        view: VoteView = self.view
        if interaction.user not in view.voted_players or configs.ONE_PLAYER:
            if interaction.user in [p.user for p in game_data.players] or configs.ONE_PLAYER:
                view.voted_players.append(interaction.user)
                view.count += 1
                self.player.votes += 1
                await interaction.response.send_message("Голос принят", ephemeral=True)
            else:
                await interaction.response.send_message("Вы не можете проголосовать, так как были убиты", ephemeral=True)
        else:
            await interaction.response.send_message("Вы уже проголосовали", ephemeral=True)

        if view.count >= len(players):
            game_data.time_left = 0


class VoteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.voted_players = []

        for i in range(len(players)):
            self.add_item(VoteButton(players[i], i // 5))

