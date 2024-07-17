from .logs_decoder_cog import LogsCheckerCog


def setup(bot):
    bot.add_cog(LogsCheckerCog(bot))

