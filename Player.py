import asyncio
from discord.ext import tasks
import random
from States import States


class GameData:
    def __init__(self):
        self.players = []
        self.killed_pers = None
        self.healed_pers = None
        self.day = 0
        self.state = States.OFF
        self.time_left = 0

    def clear(self):
        self.players.clear()
        self.killed_pers = None
        self.healed_pers = None
        self.day = 0
        self.time_left = 0

    def get_players(self):
        text = "\nИгроки:"
        for i in range(len(self.players)):
            text += f"\n{i+1}) {self.players[i].user.name}"
        return text

    async def set_roles(self):
        print("Players:", len(self.players))
        for player in self.players:
            print(player.num, player.user)
        print()
        random.shuffle(self.players)
        for player in self.players:
            print(player.num, player.user)
        print()

        self.players[0].role = "mafia"
        self.players[1].role = "sherif"
        self.players[2].role = "doctor"

        random.shuffle(self.players)  # comment if you want to know players' roles

        roles = {"mafia": "мафия", "sherif": "шериф", "doctor": "доктор", "citizen": "горожанин"}

        for player in self.players:
            await player.user.send(f"Вы {roles[player.role]}")

    async def get_votes(self, ctx):
        votes = [player.votes for player in self.players]

        text = "Результаты голосования:\n"
        for i in range(len(self.players)):
            text += self.players[i].user.name + " - " + str(votes[i]) + "\n"

        await ctx.send(text)

        max_vote = max(votes)
        if max_vote != 0 and votes.count(max_vote) == 1:
            accused = self.players.pop(votes.index(max_vote))
            await ctx.send(f"Горожане проголосовали за {accused.user.name}")
            if accused.role == "mafia":
                await ctx.send("Он был мафией")
            else:
                await ctx.send("Он не был мафией")
        else:
            await ctx.send("Горожане не пришли к единому результату")

        game_data.clear_votes()
        game_data.get_players()

    def clear_votes(self):
        for player in self.players:
            player.votes = 0

    async def timer(self, ctx, sec: int):
        self.countdown.start()
        self.time_left = sec

        minutes, seconds = divmod(self.time_left, 60)
        time_format = "{:02d}:{:02d}".format(minutes, seconds)
        message = await ctx.send(time_format)

        while self.time_left > 0:
            minutes, seconds = divmod(self.time_left, 60)
            time_format = "{:02d}:{:02d}".format(minutes, seconds)
            await message.edit(content="Time: "+time_format)
            await asyncio.sleep(1)  # So it only does this every second

        await message.delete()
        self.countdown.stop()

    @tasks.loop(seconds=1)
    async def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1


class Player:
    def __init__(self, user, num):
        self.num = num
        self.user = user
        self.role = "citizen"
        # self.was_killed = False
        self.votes = 0


game_data = GameData()
