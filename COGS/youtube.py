import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command()
    async def download(self, ctx, url):
        title = await self.download_audio(url)
        await ctx.send(f'Download complete: {title}.mp3')

    @commands.command()
    async def play(self, ctx):
        channel = ctx.message.author.voice.channel
        voice_channel = await channel.connect()

        # ダウンロード先のディレクトリから、最新のMP3ファイルを取得
        mp3_files = [f for f in os.listdir('downloads') if f.endswith('.mp3')]
        if mp3_files:
            mp3_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join('downloads', x)))

            # MP3 ファイルを再生
            voice_channel.play(discord.FFmpegPCMAudio(f'downloads/{mp3_file}'))

            # 再生完了まで待機
            while voice_channel.is_playing():
                await asyncio.sleep(1)

            # 接続を切断
            await asyncio.sleep(1)  # 1秒待機
            await voice_channel.disconnect()
        else:
            await ctx.send('No MP3 files found to play.')


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    print("[SystemLog] youtube ")