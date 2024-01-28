import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
import random

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.played_history = set()  # 再生した曲の履歴を管理するセット

    async def download_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = await self.bot.loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        return info["title"]

    async def play_random_mp3(self, voice_channel):
        # ダウンロード先のディレクトリから、MP3ファイルを取得
        mp3_files = [f for f in os.listdir('downloads') if f.endswith('.mp3') and f not in self.played_history]
        if mp3_files:
            mp3_file = random.choice(mp3_files)

            # MP3 ファイルを再生
            voice_channel.play(discord.FFmpegPCMAudio(f'downloads/{mp3_file}'))

            # 再生履歴に追加
            self.played_history.add(mp3_file)

            # 再生完了まで待機
            while voice_channel.is_playing():
                await asyncio.sleep(1)

            return True
        else:
            return False

    @commands.command()
    async def download(self, ctx, url):
        await ctx.send("Start")
        title = await self.download_audio(url)
        await ctx.send(f'Download complete: {title}.mp3')

    @commands.command()
    async def play_all(self, ctx):
        channel = ctx.message.author.voice.channel
        voice_channel = await channel.connect()

        while await self.play_random_mp3(voice_channel):
            pass  # ファイルがある限り再生を続ける

        # 全ての再生が終わったらボイスチャンネルから切断
        await asyncio.sleep(1)  # 必要に応じて調整
        await voice_channel.disconnect()
        await ctx.send('All MP3 files played. Bot disconnected.')

    @commands.command()
    async def skip(self, ctx):
        # スキップ時に再生履歴をクリア
        self.played_history.clear()

        # ボイスチャンネルから切断
        voice_channel = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_channel:
            await voice_channel.disconnect()
            await ctx.send('Skipped. Bot disconnected.')


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    print("[SystemLog] youtube ")