from pysplus import Client

bot = Client("test",number_phone="9017760881")

async def m():
    await bot.login()
import asyncio
asyncio.run(m())