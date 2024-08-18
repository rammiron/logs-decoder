import discord
import base64
from discord.ext import commands
from utils.rsa import decrypt

class LogsCheckerCog(commands.Cog):
    local_path = __name__
    exe_path = f"{local_path}/../logs-checker/logs-checker.exe"
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def parse_logs(self, data: str):
        data_dict = {}
        event = ""
        index = 0.1
        for line in data.splitlines():
            split = line.strip("   ").split(":", maxsplit=1)
            if len(split) == 0:
                continue
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
                if len(split) > 1:
                    data_dict[event][split[0]] = split[1]
        return data_dict

    @commands.slash_command(name="help_win_logs", description="Помощь с логами Windows.")
    async def help_win_logs(self, ctx: discord.ApplicationContext):
        file = discord.File(self.exe_path)
        await ctx.respond("Здравствуйте. Чтобы Вас разбанили, "
                          "необходимо предоставить информацию,"
                          " что Вы отключились действительно по независящим от Вас причинам. "
                          "Просим предоставить логи Windows. Вы можете сделать это самостоятельно, "
                          "предоставив скриншоты с ошибками 6008, 41 из журнала Windows,  либо же запустить файл, "
                          "который соберет логи за Вас самостоятельно. "
                          "Сам файл разработан нашими программистами,"
                          " не содержит вирусов, "
                          "но для большей уверенности проверен на вирусы с помощью сервиса virustotal.\n"
                          "-> [ТЫК](https://www.virustotal.com/gui/file"
                          "/d34729fdec9fcb647ea54cdc43b362aee983c60dcce104917c61bf9f6c0ca4cf)"
                          "\n"
                          "Просим отправить в этот чат сгенерированный файл.")
        await ctx.channel.send("Файл: ", file=file)

    @commands.command(name="get_logs", descriprion="Прочесть логи.")
    async def read_logs(self, ctx: discord.ApplicationContext):

        if ctx.message.reference:
            original = await ctx.fetch_message(ctx.message.reference.message_id)
            if not original.attachments:
                return
            attachment = original.attachments[0]
        else:
            if not ctx.message.attachments:
                return
            attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".ds"):
            return
        file = await attachment.read()
        decoded_from_base64 = base64.b64decode(file).decode()
        decrypted_from_rsa = decrypt(decoded_from_base64)
        parsed_logs = self.parse_logs(decrypted_from_rsa)
        if len(parsed_logs) < 1:
            await ctx.channel.send("Завершений работы с ошибкой не обнаружено.")
            return

        embed = discord.Embed(
            title="Логи завершения работы.",
            colour=discord.Colour.red()

        )
        for log in parsed_logs:
            embed.add_field(name=f"{log}:", value=f"Описание: {parsed_logs[log]
            ['Description']}\nДата: {parsed_logs[log]['Date']}"
                                                  f" \nКод: {parsed_logs[log]["Event ID"]}\n", inline=False)

        try:
            await ctx.author.send(embed=embed)
        except:
            await ctx.channel.send(f"{ctx.author.mention}, похоже у вас закрыт лс. Откройте лс и повторите попытку.")
