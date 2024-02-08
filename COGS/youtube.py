import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
import random

class MusicCog(commands.Cog):
    """
    A class representing a Discord bot cog for playing and downloading music from YouTube.

    Attributes:
    - bot (discord.ext.commands.Bot): The Discord bot instance.
    - played_history (set): A set to manage the history of played songs.

    Methods:
    - download_audio(url): Downloads audio from the given YouTube URL.
    - play_random_mp3(voice_channel): Plays a random MP3 file in the specified voice channel.
    - download(ctx, url): Command to download audio from a YouTube URL.
    - play_all(ctx): Command to play all downloaded MP3 files in the user's voice channel.
    - stop(ctx): Command to stop playing and disconnect from the voice channel.
    - on_raw_reaction_add(payload): Event listener for reacting to YouTube URLs with a thumbs-up emoji.
    """

    def __init__(self, bot):
        self.bot = bot
        self.played_history = set()  # 再生した曲の履歴を管理するセット

    async def download_audio(self, url):
        """
        Downloads audio from the given YouTube URL.

        Args:
        - url (str): The YouTube URL.

        Returns:
        - str: The title of the downloaded audio.
        """
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
        """
        Plays a random MP3 file in the specified voice channel.

        Args:
        - voice_channel (discord.VoiceChannel): The voice channel to play the MP3 file in.

        Returns:
        - bool: True if a file was played, False otherwise.
        """
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
        """
        Command to download audio from a YouTube URL.

        Args:
        - ctx (discord.ext.commands.Context): The command context.
        - url (str): The YouTube URL.
        """
        await ctx.send("Start")
        title = await self.download_audio(url)
        await ctx.send(f'Download complete: {title}.mp3')

    @commands.command()
    async def play_all(self, ctx):
        """
        Command to play all downloaded MP3 files in the user's voice channel.

        Args:
        - ctx (discord.ext.commands.Context): The command context.
        """
        channel = ctx.message.author.voice.channel
        voice_channel = await channel.connect()

        while await self.play_random_mp3(voice_channel):
            pass  # ファイルがある限り再生を続ける

        # 全ての再生が終わったらボイスチャンネルから切断
        await asyncio.sleep(1)  # 必要に応じて調整
        await voice_channel.disconnect()
        await ctx.send('All MP3 files played. Bot disconnected.')


    @commands.command()
    async def stop(self, ctx):
        """
        Command to stop playing and disconnect from the voice channel.

        Args:
        - ctx (discord.ext.commands.Context): The command context.
        """
        # スキップ時に再生履歴をクリア
        self.played_history.clear()

        # ボイスチャンネルから切断
        voice_channel = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_channel:
            await voice_channel.disconnect()
            await ctx.send('Skipped. Bot disconnected.')
            
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Event listener for reacting to YouTube URLs with a thumbs-up emoji.

        Args:
        - payload (discord.RawReactionActionEvent): The raw reaction event payload.
        """
        # リアクションを追加したユーザーを取得
        user = await self.bot.fetch_user(payload.user_id)
        # ユーザーがボットかどうかを確認
        if user.bot:
            return
        # リアクションが発生したチャンネルを取得
        channel = self.bot.get_channel(payload.channel_id)
        # ペイロードからメッセージIDを使用してメッセージを取得
        message = await channel.fetch_message(payload.message_id)        
        if message.guild.id == 1130796864741064714:
            # ペイロードから絵文字を取得
            emoji = payload.emoji.name

            # 絵文字が「👍」であり、メッセージの内容に「youtube.com」が含まれているか確認
            if emoji == "👍" and ("youtube.com" in message.content or "youtu.be" in message.content):
                # 「🤔」リアクションを追加
                await message.add_reaction("🤔")
                # オーディオをダウンロード
                url = message.content
                await self.download_audio(url)
                #リアクション剥奪
                await message.clear_reactions()
                # 「✅」リアクションを追加
                await message.add_reaction("✅")


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    print("[SystemLog] youtube ")