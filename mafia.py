from discord.ext import commands
import Views
from MafiaView import MafiaView
from SherifView import SherifView
from DoctorView import DoctorView
from Player import game_data
from States import States


class GameBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.command(aliases=["мафиози"])
    async def mafia(self, ctx):
        if game_data.state == States.OFF:
            game_data.state = States.JOIN

            text = "Добро пожаловать в игру МАФИЯ. Для игры нажмите на кнопку 'Присоединиться'"
            view = Views.JoinView(text)
            await ctx.send(text, view=view)

            await view.wait()

            await ctx.send("Правила игры:")
            await ctx.send(game_data.get_players())
            await ctx.send("Назначение ролей...")
            await game_data.set_roles()

            game_data.state = States.DAY
        else:
            await ctx.send("Закончите текущую игру")

    @commands.command()
    async def day(self, ctx):
        if game_data.state == States.DAY:
            game_data.state = States.DAY

            view = MafiaView()
            msg = await ctx.send("Город засыпает, просыпается мафия", view=view)
            await view.wait()
            await msg.edit(content="Город засыпает, просыпается мафия", view=None)
            await view.vw.wait()

            if game_data.day > 0:
                if "sherif" in [player.role for player in game_data.players] and game_data.killed_pers.role != "sherif":
                    view = SherifView()
                    msg = await ctx.send("Просыпается шериф", view=view)
                    await view.wait()
                    await msg.edit(content="Просыпается шериф", view=None)
                    await view.vw.wait()

                if "doctor" in [player.role for player in game_data.players] and game_data.killed_pers.role != "doctor":
                    view = DoctorView()
                    msg = await ctx.send("Просыпается доктор", view=view)
                    await view.wait()
                    await msg.edit(content="Просыпается доктор", view=None)
                    await view.vw.wait()

            if game_data.healed_pers is None or game_data.killed_pers.user != game_data.healed_pers.user:
                game_data.players.remove(game_data.killed_pers)
                await game_data.killed_pers.user.send("Вас убила мафия")

            if len(game_data.players) < 3:
                await ctx.send("Мафия одержала победу\n"
                               f"Мафией был игрок "
                               f"{', '.join([player.user.name for player in game_data.players if player.role == 'mafia'])}")
                game_data.state = States.OFF
                game_data.clear()
                return

            if game_data.killed_pers not in game_data.players:
                await ctx.send(f"Наступает день. Горожане узнают о гибели игрока {game_data.killed_pers.user.name}\n"
                               f"Объявляется начало обсуждения, после чего начнётся голосование")
            else:
                await ctx.send(f"Наступает день. Горожане узнают о покушении на игрока "
                               f"{game_data.killed_pers.user.name}\n"
                               f"Однако его вылечил доктор\n"
                               f"Объявляется начало обсуждения, после чего начнётся голосование")

            await ctx.send(game_data.get_players())

            game_data.state = States.VOTE
        else:
            await ctx.send("Сейчас нельзя начать новый день")

    @commands.command()
    async def vote(self, ctx):
        if game_data.state == States.VOTE:

            view = Views.VoteView()
            msg = await ctx.send("Голосуем! Кто, по-вашему, являеся мафией?", view=view)
            await game_data.timer(ctx, 30)
            view.stop()
            await view.wait()

            game_data.day += 1

            await msg.edit(content="Голосование окончено", view=None)

            await game_data.get_votes(ctx)

            if "mafia" in [player.role for player in game_data.players] and len(game_data.players) < 3:
                await ctx.send("Мафия одержала победу\n"
                               f"Мафией был игрок "
                               f"{', '.join([player.user.name for player in game_data.players if player.role == 'mafia'])}")
                game_data.state = States.OFF
                game_data.clear()
            elif "mafia" not in [player.role for player in game_data.players]:
                await ctx.send("Горожане одержали победу")
                game_data.state = States.OFF
                game_data.clear()
            else:
                await ctx.send("Игра продолжается")
                game_data.state = States.DAY

            view.stop()
        else:
            await ctx.send("Сейчас не время для голосования")

    @commands.command(aliases=['end'])
    async def quit(self, ctx):
        game_data.state = States.OFF
        game_data.clear()
        await ctx.send("Текущая игра завершена")
