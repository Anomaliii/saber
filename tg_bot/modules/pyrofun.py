import speedtest
import re
import html
import regex
import os
from pytube import YouTube
from youtubesearchpython import VideosSearch
from tg_bot.utils.ut import get_arg
from tg_bot import pbot, LOGGER
from pyrogram import Client, filters
from pyrogram.types import Messages
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tg_bot import OWNER_ID, pbot



DART_E_MOJI = "🎯"
FOOTBALL_E_MOJI="⚽"

def yt_search(song):
    videosSearch = VideosSearch(song, limit=1)
    result = videosSearch.result()
    if not result:
        return False
    else:
        video_id = result["result"][0]["id"]
        url = f"https://youtu.be/{video_id}"
        return url


def convert(speed):
    return round(int(speed) / 1048576, 2)


async def speedtestxyz(client, message):
    buttons = [[InlineKeyboardButton("Image",
                                    callback_data="speedtest_image"),
                InlineKeyboardButton("Text",
                                    callback_data="speedtest_text")]]
    await message.reply_text(
        "Select SpeedTest Mode",
        reply_markup=InlineKeyboardMarkup(buttons))


def speed_convert(size):
    """Hi human, you can't read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: '', 1: 'Kb/s', 2: 'Mb/s', 3: 'Gb/s', 4: 'Tb/s'}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


def speedtest_callback(_, __, query):
    if re.match("speedtest", query.data):
        return True


speedtest_create = filters.create(speedtest_callback)


@pbot.on_callback_query(speedtest_create)
async def speedtestxyz_callback(client, query):
    if query.from_user.id in OWNER_ID:
        await query.message.edit_text('Runing a speedtest....')
        speed = speedtest.Speedtest()
        speed.get_best_server()
        speed.download()
        speed.upload()
        replymsg = 'SpeedTest Results:'

        if query.data == 'speedtest_image':
            speedtest_image = speed.results.share()
            replym = f"**[SpeedTest Results:]({speedtest_image})**"
            await query.message.edit_text(replym, parse_mode="markdown")

        elif query.data == 'speedtest_text':
            result = speed.results.dict()
            replymsg += f"\n - **ISP:** `{result['client']['isp']}`"
            replymsg += f"\n - **Download:** `{speed_convert(result['download'])}`"
            replymsg += f"\n - **Upload:** `{speed_convert(result['upload'])}`"
            replymsg += f"\n - **Ping:** `{result['ping']}`"
            await query.message.edit_text(replymsg, parse_mode="markdown")
    else:
        await client.answer_callback_query(query.id, "No, you are not allowed to do this", show_alert=False)

@pbot.on_message(filters.command("song"))
async def song(client, message):
    chat_id = message.chat.id
    user_id = message.from_user["id"]
    args = get_arg(message) + " " + "song"
    if args.startswith(" "):
        await message.reply("Enter a song name. Check /help")
        return ""
    status = await message.reply("Processing...")
    video_link = yt_search(args)
    if not video_link:
        await status.edit("Song not found.")
        return ""
    yt = YouTube(video_link)
    audio = yt.streams.filter(only_audio=True).first()
    try:
        download = audio.download(filename=f"{str(user_id)}")
    except Exception as ex:
        await status.edit("Failed to download song")
        LOGGER.error(ex)
        return ""
    rename = os.rename(download, f"{str(user_id)}.mp3")
    await pbot.send_chat_action(message.chat.id, "upload_audio")
    await pbot.send_audio(
        chat_id=message.chat.id,
        audio=f"{str(user_id)}.mp3",
        duration=int(yt.length),
        title=str(yt.title),
        performer=str(yt.author),
        reply_to_message_id=message.message_id,
    )
    await status.delete()
    os.remove(f"{str(user_id)}.mp3")



@pbot.on_message(filters.command('basket'))
async def basket(c: Client, m: Message):
    await c.send_dice(m.chat.id, reply_to_message_id=m.message_id, emoji="🏀")

@pbot.on_message(filters.command('dice'))
async def dice(c: Client, m: Message):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.message_id)
    await dicen.reply_text(f"The dice stopped at the number {dicen.dice.value}", quote=True)

@pbot.on_message(
    filters.command("dart")
)
async def throw_dart(client, message):
    """ /dart an @AnimatedDart """
    rep_mesg_id = message.message_id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.message_id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=DART_E_MOJI,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )

@pbot.on_message(
    filters.command("football")
)
async def throw_football(client, message):
    """ /football an @Animatedfootball """
    rep_mesg_id = message.message_id
    if message.reply_to_message:
        rep_mesg_id = message.reply_to_message.message_id
    await client.send_dice(
        chat_id=message.chat.id,
        emoji=FOOTBALL_E_MOJI,
        disable_notification=True,
        reply_to_message_id=rep_mesg_id
    )


@pbot.on_message(filters.command("dinfo") & filters.private)
async def ids_private(c: Client, m: Message):
    await m.reply_text("<b>Info:</b>\n\n"
                       "<b>Name:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>User ID:</b> <code>{user_id}</code>\n"
                       "<b>Language:</b> {lang}\n"
                       "<b>Chat type:</b> {chat_type}".format(
                           first_name=m.from_user.first_name,
                           last_name=m.from_user.last_name or "",
                           username=m.from_user.username,
                           user_id=m.from_user.id,
                           lang=m.from_user.language_code,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")


@pbot.on_message(filters.command("dinfo") & filters.group)
async def ids(c: Client, m: Message):
    data = m.reply_to_message or m
    await m.reply_text("<b>Info:</b>\n\n"
                       "<b>Name:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>User ID:</b> <code>{user_id}</code>\n"
                       "<b>Datacenter:</b> {user_dc}\n"
                       "<b>Language:</b> {lang}\n\n"
                       "<b>Chat name:</b> <code>{chat_title}</code>\n"
                       "<b>Chat username:</b> @{chat_username}\n"
                       "<b>Chat ID:</b> <code>{chat_id}</code>\n"
                       "<b>Chat type:</b> {chat_type}".format(
                           first_name=html.escape(data.from_user.first_name),
                           last_name=html.escape(data.from_user.last_name or ""),
                           username=data.from_user.username,
                           user_id=data.from_user.id,
                           user_dc=data.from_user.dc_id,
                           lang=data.from_user.language_code or "-",
                           chat_title=m.chat.title,
                           chat_username=m.chat.username,
                           chat_id=m.chat.id,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")


@pbot.on_message(filters.regex(r'^s/(.+)?/(.+)?(/.+)?') & filters.reply)
async def sed(c: Client, m: Message):
    exp = regex.split(r'(?<![^\\]\\)/', m.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r'\/', '/')
    flags = exp[3] if len(exp) > 3 else ''

    count = 1
    rflags = 0

    if 'g' in flags:
        count = 0
    if 'i' in flags and 's' in flags:
        rflags = regex.I | regex.S
    elif 'i' in flags:
        rflags = regex.I
    elif 's' in flags:
        rflags = regex.S

    text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return

    try:
        res = regex.sub(
            pattern,
            replace_with,
            text,
            count=count,
            flags=rflags,
            timeout=1)
    except TimeoutError:
        await m.reply_text("Oops, your regex pattern ran for too long.")
    except regex.error as e:
        await m.reply_text(str(e))
    else:
        await c.send_message(m.chat.id, f'<pre>{html.escape(res)}</pre>',
                             reply_to_message_id=m.reply_to_message.message_id)


