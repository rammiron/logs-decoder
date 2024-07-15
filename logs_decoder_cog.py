import discord
import base64
from discord.ext import commands


class LogsCheckerCog(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def parse_logs(self, data: str):
        data_dict = {}
        event = ""
        index = 0.1
        for line in data.splitlines():
            split = line.strip("   ").split(":", maxsplit=1)
            if len(split) > 1:
                if split[0].startswith("Event["):
                    if split[0] in data_dict.keys():
                        event = f"Event[{index}]"
                        data_dict[event] = {}
                        index += 1
                        continue
                    event = split[0]
                    data_dict[event] = {}
                    continue
                if (split[0].startswith("Предыдущее завершение работы системы") or
                        split[0].startswith("Система перезагрузилась") and event != ""):
                    data_dict[event]["Description"] = split[0] + ":" + split[1]
                if event != "":
                    data_dict[event][split[0]] = split[1]
        return data_dict

    @commands.command(name="read_logs", descriprion="Прочесть логи.")
    async def read_logs(self, ctx: discord.ApplicationContext):
        if not ctx.message.attachments:
            return
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".ds"):
            return
        file = await attachment.read()
        decoded = base64.b64decode(file).decode()
        parsed_logs = self.parse_logs(decoded)
        if len(parsed_logs) < 1:
            await ctx.channel.send("Завершений работы с ошибкой не обнаружено.")
            return
        print(parsed_logs)

        embed = discord.Embed(
            title="Логи завершения работы.",
            colour=discord.Colour.red()

        )
        for log in parsed_logs:
            embed.add_field(name=f"{log}:", value=f"Описание: {parsed_logs[log]
            ['Description']}\nДата: {parsed_logs[log]['Date']}"
                                                  f" \nКод: {parsed_logs[log]["Event ID"]}\n", inline=False)

        await ctx.channel.send(embed=embed)
