import discord
from discord.ext import commands
import os
from mytsoss.commands.addprogram import add_program_command

class MyTossBot(commands.Bot):
    def __init__(self, command_prefix='-', intents=None):
        if intents is None:
            intents = discord.Intents.default()
            intents.messages = True
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self):
        pass  # لا تطبع أي شيء في الكونسول

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)

def main(token):
    bot = MyTossBot()
    bot.add_command(add_program_command)
    bot.run(token)

if __name__ == "__main__":
    TOKEN = "MTQxODY5NzgxOTIxMjA4NzMxOA.GFCDeN.S9AsDBNbANp6Cxr7BkSkUH7nLqSFGQrb9jnoGA"
    main(TOKEN)