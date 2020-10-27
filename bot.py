import discord
# from discord import colour
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil
from os import system


TOKEN = ''
BOT_PREFIX = '.'

bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('type .help to get started'))
    print(f'Logged in as: {bot.user.name}\n')

# Bot commands


@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    help_embed = discord.Embed(colour=discord.Colour.green(
    ), title='Bot commands', description='Commands for the music bot')
    help_embed.set_author(
        name='Music 24/7', icon_url='https://cdn.discordapp.com/attachments/738729159685308487/738752162091499640/02mtFJaU_400x400.jpg')
    help_embed.add_field(
        name=".join", value="Bot will join the voice channel that you're currently in", inline=False)
    help_embed.add_field(
        name=".leave", value="Bot will leave the voice channel", inline=False)
    help_embed.add_field(
        name=".play", value="This will play the music that you pass in here. Works like youtube search. This also works with youtube/spotify links. Example: .play song name", inline=False)
    help_embed.add_field(name=".pause", value="Pauses the music", inline=False)
    help_embed.add_field(
        name=".resume", value="Resumes the music", inline=False)
    help_embed.add_field(
        name=".next", value="Skips the current on and plays next music", inline=False)
    help_embed.add_field(
        name=".stop", value="Stops playing music", inline=False)
    help_embed.add_field(
        name=".queue", value="Adds song to the queue. Example: .queue song name", inline=False)
    help_embed.add_field(
        name=".volume", value="Changes the volume. Default is 23. Volume limit = 1-100. Example: .volume 30", inline=False)

    await author.send(embed=help_embed)


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)

    await channel.connect()

    print(f'The bot has connected to {channel}\n')

    await ctx.send(f'Joined {channel}')


@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'The bot has left {channel}')
        await ctx.send(f'Left {channel}')
    else:
        print('Bot was told to leave voice channel, but was not in one')
        await ctx.send("Don't think I am in a voice channel")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):

    def check_queue():
        queue_infile = os.path.isdir('./Queue')
        if queue_infile is True:
            DIR = os.path.abspath(os.path.realpath('Queue'))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print('No more queued song(s)\n')
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(
                os.path.realpath('Queue') + '\\' + first_file)
            if length != 0:
                print('Song done, playing next queued\n')
                print(f'Songs still in queue: {still_q}')
                song_there = os.path.isfile('song.mp3')
                if song_there:
                    os.remove('song.mp3')
                shutil.move(song_path, main_location)
                for file in os.listdir('./'):
                    if file.endswith('.mp3'):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio('song.mp3'),
                           after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07
            else:
                queues.clear()
                return
        else:
            queues.clear()
            print('No songs were queued before the ending of the last song\n')

    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            queues.clear()
            print('Removed old song file')
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send('ERROR: Music playing')
        return

    queue_infile = os.path.isdir('./Queue')
    try:
        queue_folder = './Queue'
        if queue_infile is True:
            print('Removed old Queue Folder')
            shutil.rmtree(queue_folder)
    except:
        print('No old Queue folder')

    await ctx.send('Getting everything ready now')

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'outtmpl': './song.mp3', 'postprocessors': [
        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192', }], }

    song_search = ' '.join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print('Downloading audio now\n')
            ydl.download([f'ytsearch1:{song_search}'])
    except:
        print('FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)')
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' +
               c_path + '"' + " -s " + song_search)

    voice.play(discord.FFmpegPCMAudio('song.mp3'),
               after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.23

    await ctx.send('Playing Song')

    print('Playing')


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print('Music paused')
        voice.pause()
        await ctx.send('Music paused')
    else:
        print('Music not playing failed pause')
        await ctx.send('Music not playing failed pause')


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print('Resumed music')
        voice.resume()
        await ctx.send('Resumed music')
    else:
        print('Music is not paused')
        await ctx.send('Music is not paused')


@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir('./Queue')
    if queue_infile is True:
        shutil.rmtree('./Queue')

    if voice and voice.is_playing():
        print('Music stopped')
        voice.stop()
        await ctx.send('Music stopped')
    else:
        print('No music playing failed to stop')
        await ctx.send('No music playing failed to stop')

queues = {}


@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, *url: str):
    queues_infile = os.path.isdir('./Queue')
    if queues_infile is False:
        os.mkdir('Queue')
    DIR = os.path.abspath(os.path.realpath('Queue'))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(
        os.path.realpath('Queue') + f'\song{q_num}.%(ext)s')

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'outtmpl': queue_path, 'postprocessors': [
        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192', }], }

    song_search = ' '.join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print('Downloading audio now\n')
            ydl.download([f'ytsearch1:{song_search}'])
    except:
        print('FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)')
        q_path = os.path.abspath(os.path.realpath('Queue'))
        system(f"spotdl -ff song{q_num} -f " + '"' +
               q_path + '"' + ' -s ' + song_search)

    await ctx.send('Adding song ' + str(q_num) + ' to the queue')

    print('Song added to the queue\n')


@bot.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print('Playing next song')
        voice.stop()
        await ctx.send('Next Song')
    else:
        print('No music playing failed to play next song')
        await ctx.send('No music playing failed')


@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send('Not connected to voice channel')

    print(volume/100)

    ctx.voice_client.source.volume = volume/100
    await ctx.send(f'Changed volume to {volume}%')

bot.run(TOKEN)
