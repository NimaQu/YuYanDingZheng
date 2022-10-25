import asyncio
import discord
import logging
import os
import random

import config
from yuyan import TTS

yid = config.yid
subscription_key = config.subscription_key
region = config.region
language = config.language
end = config.end

tts = TTS(subscription_key, region, language)
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = discord.Client(intents=intents)

vc = None


@bot.event
async def on_ready():
    logging.info("Logged in as {}".format(bot.user))


@bot.event
async def on_message(message):
    global vc
    if message.content == "":
        # empty message
        return

    if message.content == '/summon':
        if vc is not None:
            await message.channel.send('I am already in a voice channel.')
            return
        channel = message.author.voice.channel
        if channel is None:
            await message.channel.send('You are not in a voice channel.')
            return
        vc = await channel.connect()
        return
    elif message.content == '/dc':
        if vc is None:
            await message.channel.send('I am not in a voice channel.')
            return
        await vc.disconnect()
        vc = None
        return
    elif list(message.content)[0] == '<' and list(message.content)[-1] == '>':
        # 忽略贴纸消息 <:xie_majyo_sleep:769228515647684649>
        return
    elif '```' in message.content or 'https://' in message.content or 'http://' in message.content:
        # 忽略代码和链接
        return

    if message.author.id != yid:
        return
    rnd = random.randint(0, len(end) - 1)
    text = message.content + end[rnd]
    filename = str(hash(text))
    if vc:
        if not os.path.exists("tmp/" + filename):
            tts.to_file(text)
        while vc.is_playing():
            await asyncio.sleep(1)
        vc.play(discord.FFmpegOpusAudio(source="tmp/" + filename))
        # delete temporary file after playing
        while vc.is_playing():
            await asyncio.sleep(1)
        os.remove("tmp/" + filename)


@bot.event
async def on_voice_state_update(member, before, after):
    global vc
    if member.id != yid:
        return
    if before.channel is None and after.channel:
        logging.info('joined channel')
        vc = await after.channel.connect()
    elif after.channel is None and before.channel:
        if vc:
            logging.info('left channel')
            await vc.disconnect(force=False)
            vc = None
    elif before.channel != after.channel:
        logging.info('switched channel')
        if after.channel:
            if vc:
                await vc.disconnect(force=True)
                vc = await after.channel.connect()
    else:
        return


def main():
    try:
        bot.run(config.token)
    except KeyboardInterrupt:
        print('Exiting...')
        bot.close()


if __name__ == "__main__":
    try:
        bot.run(config.token)
    except KeyboardInterrupt:
        print('Exiting...')
        bot.close()
