import asyncio
import base64
import math
import random
from io import BytesIO
from pyrogram.enums import ChatType
import functools
import multiprocessing
import os
import shlex
import textwrap
import traceback
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont
from pymediainfo import MediaInfo


max_workers = multiprocessing.cpu_count() * 5
exc_ = ThreadPoolExecutor(max_workers=max_workers)


class Media_Info:
    def data(media):
        found = False
        media_info = MediaInfo.parse(media)
        for track in media_info.tracks:
            if track.track_type == "Video":
                found = True
                type_ = track.track_type
                format_ = track.format
                duration_1 = track.duration
                other_duration_ = track.other_duration
                duration_2 = (
                    f"{other_duration_[0]} - ({other_duration_[3]})"
                    if other_duration_
                    else None
                )
                pixel_ratio_ = [track.width, track.height]
                aspect_ratio_1 = track.display_aspect_ratio
                other_aspect_ratio_ = track.other_display_aspect_ratio
                aspect_ratio_2 = other_aspect_ratio_[0] if other_aspect_ratio_ else None
                fps_ = track.frame_rate
                fc_ = track.frame_count
                media_size_1 = track.stream_size
                other_media_size_ = track.other_stream_size
                media_size_2 = (
                    [
                        other_media_size_[1],
                        other_media_size_[2],
                        other_media_size_[3],
                        other_media_size_[4],
                    ]
                    if other_media_size_
                    else None
                )

        dict_ = (
            {
                "media_type": type_,
                "format": format_,
                "duration_in_ms": duration_1,
                "duration": duration_2,
                "pixel_sizes": pixel_ratio_,
                "aspect_ratio_in_fraction": aspect_ratio_1,
                "aspect_ratio": aspect_ratio_2,
                "frame_rate": fps_,
                "frame_count": fc_,
                "file_size_in_bytes": media_size_1,
                "file_size": media_size_2,
            }
            if found
            else None
        )
        return dict_


def get_arg(message):
    if message.reply_to_message and len(message.command) < 2:
        msg = message.reply_to_message.text or message.reply_to_message.caption
        if not msg:
            return ""
        msg = msg.encode().decode("UTF-8")
        msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
        return msg
    elif len(message.command) > 1:
        return " ".join(message.command[1:])
    else:
        return ""

def get_message(message):
    msg = (
        message.reply_to_message
        if message.reply_to_message
        else ""
        if len(message.command) < 2
        else message.text.split(None, 1)[1]
    )
    return msg

async def get_global_id(client, query):
    chats = []
    chat_types = {
        "global": [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP],
        "group": [ChatType.GROUP, ChatType.SUPERGROUP],
        "users": [ChatType.PRIVATE],
    }
    async for dialog in client.get_dialogs():
        if dialog.chat.type in chat_types[query]:
            chats.append(dialog.chat.id)

    return chats
    

def get_text(message):
    if message.reply_to_message:
        if len(message.command) < 2:
            text = message.reply_to_message.text or message.reply_to_message.caption
        else:
            text = (
                (message.reply_to_message.text or message.reply_to_message.caption)
                + "\n\n"
                + message.text.split(None, 1)[1]
            )
    else:
        if len(message.command) < 2:
            text = ""
        else:
            text = message.text.split(None, 1)[1]
    return text


async def resize_media(media, video, fast_forward):
    if video:
        info_ = Media_Info.data(media)
        width = info_["pixel_sizes"][0]
        height = info_["pixel_sizes"][1]
        sec = info_["duration_in_ms"]
        s = round(float(sec)) / 1000

        if height == width:
            height, width = 512, 512
        elif height > width:
            height, width = 512, -1
        elif width > height:
            height, width = -1, 512

        resized_video = f"{media}.webm"
        if fast_forward:
            if s > 3:
                fract_ = 3 / s
                ff_f = round(fract_, 2)
                set_pts_ = ff_f - 0.01 if ff_f > fract_ else ff_f
                cmd_f = f"-filter:v 'setpts={set_pts_}*PTS',scale={width}:{height}"
            else:
                cmd_f = f"-filter:v scale={width}:{height}"
        else:
            cmd_f = f"-filter:v scale={width}:{height}"
        fps_ = float(info_["frame_rate"])
        fps_cmd = "-r 30 " if fps_ > 30 else ""
        cmd = f"ffmpeg -i {media} {cmd_f} -ss 00:00:00 -to 00:00:03 -an -c:v libvpx-vp9 {fps_cmd}-fs 256K {resized_video}"
        _, error, __, ___ = await run_cmd(cmd)
        os.remove(media)
        return resized_video

    image = Image.open(media)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = "sticker.png"
    image.save(resized_photo)
    os.remove(media)
    return resized_photo


def generate_random_emoji():
    categories = [
        (0x1F600, 0x1F64F),  # Wajah
        (0x1F300, 0x1F5FF),  # Simbol & Pictographs
        (0x1F680, 0x1F6FF),  # Transportasi & Simbol Transportasi
        (0x1F700, 0x1F77F),  # Alat & Simbol Teknikal
        (0x1F900, 0x1F9FF),  # Simbol Keagamaan & Rohani
        (0x1F4F0, 0x1F4FF),  # Simbol Kantor
        (0x1F320, 0x1F32F),  # Simbol Meteorologi
        (0x1F3E0, 0x1F3EF),  # Simbol Olahraga
        (0x1F600, 0x1F64F),  # Simbol Cinta & Perasaan
        (0x1F340, 0x1F35F),  # Simbol Makanan & Minuman
        (0x1F400, 0x1F4D3),  # Simbol Pustaka
        (0x1F4E0, 0x1F4E9),  # Simbol Media
        (0x1F500, 0x1F53D),  # Simbol Matematika & Ilmiah
        (0x1F550, 0x1F567),  # Simbol Jam & Waktu
        (0x1F600, 0x1F636),  # Simbol Hewan
        (0x1F700, 0x1F773),  # Simbol Alam
        (0x1F600, 0x1F636),  # Simbol Transportasi Darat
        (0x1F680, 0x1F6C5),  # Simbol Pesawat & Transportasi Udara
        (0x1F774, 0x1F77F),  # Simbol Kapal & Transportasi Air
        (0x1F780, 0x1F7FF),  # Simbol Olahraga Ekstrem
        (0x1F900, 0x1F94F),  # Simbol Musik & Alat Musik
        (0x1F600, 0x1F64F),  # Simbol Profesi
        (0x1F980, 0x1F981),  # Simbol Benda
        (0x1F985, 0x1F991),  # Simbol Buah & Sayuran
        (0x1F992, 0x1F997),  # Simbol Makanan & Minuman
        (0x1F6A0, 0x1F6A3),  # Simbol Transportasi Laut
        (0x1F6F0, 0x1F6F3),  # Simbol Transportasi Udara
        (0x1F600, 0x1F636),  # Simbol Kegiatan Luar Ruangan
        (0x1F300, 0x1F320),  # Simbol Alat Musik
        (0x1F200, 0x1F251),  # Simbol Kepemimpinan & Otoritas
        (0x1F6B4, 0x1F6B6),  # Simbol Transportasi Publik
        (0x1F30D, 0x1F30F),  # Simbol Planet
        (0x1F31D, 0x1F31F),  # Simbol Bulan
        (0x1F320, 0x1F32F),  # Simbol Teleskop
        (0x1F400, 0x1F407),  # Simbol Binatang Air
        (0x1F408, 0x1F40F),  # Simbol Binatang Tanah
        (0x1F410, 0x1F417),  # Simbol Binatang Udara
        (0x1F910, 0x1F918),  # Simbol Aktivitas Manusia
        (0x1F919, 0x1F91F),  # Simbol Tangan & Jari
        (0x1F920, 0x1F927),  # Simbol Orang
    ]

    category = random.choice(categories)
    unique_code = random.randint(category[0], category[1])
    return chr(unique_code)


async def add_text_img(image_path, text):
    font_size = 12
    stroke_width = 1

    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""

    img = Image.open(image_path).convert("RGBA")
    img_info = img.info
    image_width, image_height = img.size
    font = ImageFont.truetype(
        font="storage/default.ttf",
        size=int(image_height * font_size) // 100,
    )
    draw = ImageDraw.Draw(img)

    char_width, char_height = font.getsize("A")
    chars_per_line = image_width // char_width
    top_lines = textwrap.wrap(upper_text, width=chars_per_line)
    bottom_lines = textwrap.wrap(lower_text, width=chars_per_line)

    if top_lines:
        y = 10
        for line in top_lines:
            line_width, line_height = font.getsize(line)
            x = (image_width - line_width) / 2
            draw.text(
                (x, y),
                line,
                fill="white",
                font=font,
                stroke_width=stroke_width,
                stroke_fill="black",
            )
            y += line_height

    if bottom_lines:
        y = image_height - char_height * len(bottom_lines) - 15
        for line in bottom_lines:
            line_width, line_height = font.getsize(line)
            x = (image_width - line_width) / 2
            draw.text(
                (x, y),
                line,
                fill="white",
                font=font,
                stroke_width=stroke_width,
                stroke_fill="black",
            )
            y += line_height

    final_image = os.path.join("memify.webp")
    img.save(final_image, **img_info)
    return final_image


async def aexec(code, user, mes):
    message = event = mes
    p = lambda _x: print(_format.yaml_format(_x))
    reply = message.reply_to_message
    exec(
        (
            "async def __aexec(message, event , reply, client, p, chat): "
            + "".join(f"\n {l}" for l in code.split("\n"))
        )
    )

    return await locals()["__aexec"](
        message, event, reply, user, p, message.chat.id
    )




async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def run_cmd(cmd):
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def dl_pic(client, download):
    path = await client.download_media(download)
    with open(path, "rb") as f:
        content = f.read()
    os.remove(path)
    get_photo = BytesIO(content)
    return get_photo

async def edit_or_reply(message, text):
    msg = (
        message.edit_text
        if bool(message.from_user and message.from_user.is_self or message.outgoing)
        else (message.reply_to_message or message).reply_text
    )
    return await msg(text)

eor = edit_or_reply
