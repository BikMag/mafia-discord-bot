import discord
from discord.ext import commands
import configs
from mafia import GameBotCommands


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or(configs.PREFIX), intents=intents)

    async def on_ready(self):
        print(f'We have logged in as {self.user} (ID: {self.user.id})')

        await self.add_cog(GameBotCommands(bot))


bot = GameBot()

bot.run(configs.TOKEN)
