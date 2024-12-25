from enum import IntEnum, unique


@unique
class Types(IntEnum):
    TEXT = 1
    DOCUMENT = 2
    PHOTO = 3
    VIDEO = 4
    STICKER = 5
    AUDIO = 6
    VOICE = 7
    VIDEO_NOTE = 8
    ANIMATION = 9
    ANIMATED_STICKER = 10
    CONTACT = 11


def get_message_type(msg):
    if msg.text or msg.caption:
        return None, Types.TEXT
    
    if msg.sticker:
        return msg.sticker.file_id, Types.STICKER

    if msg.document:
        if msg.document.mime_type == "application/x-bad-tgsticker":
            return msg.document.file_id, Types.ANIMATED_STICKER
        return msg.document.file_id, Types.DOCUMENT

    if msg.photo:
        return msg.photo[-1].file_id, Types.PHOTO

    if msg.audio:
        return msg.audio.file_id, Types.AUDIO

    if msg.voice:
        return msg.voice.file_id, Types.VOICE

    if msg.video:
        return msg.video.file_id, Types.VIDEO

    if msg.video_note:
        return msg.video_note.file_id, Types.VIDEO_NOTE

    if msg.animation:
        return msg.animation.file_id, Types.ANIMATION

    return None, None



def get_note_type(msg):
    if len(msg.text.split()) <= 1:
        return None, None, None, None
    data_type = None
    content = None
    if msg.text:
        raw_text = msg.text.markdown
    else:
        raw_text = msg.caption.markdown
    args = raw_text.split(None, 2)  # use python's maxsplit to separate cmd and args
    note_name = args[1]

    # determine what the contents of the filter are - text, image, sticker, etc
    if len(args) >= 3:
        text = args[2]
        data_type = Types.TEXT

    elif msg.reply_to_message:
        if msg.reply_to_message.text:
            text = msg.reply_to_message.text.markdown
        elif msg.reply_to_message.caption:
            text = msg.reply_to_message.caption.markdown
        else:
            text = ""
        if len(args) >= 2 and msg.reply_to_message.text:  # not caption, text
            data_type = Types.TEXT

        elif msg.reply_to_message.sticker:
            content = msg.reply_to_message.sticker.file_id
            data_type = Types.STICKER

        elif msg.reply_to_message.document:
            if msg.reply_to_message.document.mime_type == "application/x-bad-tgsticker":
                data_type = Types.ANIMATED_STICKER
            else:
                data_type = Types.DOCUMENT
            content = msg.reply_to_message.document.file_id

        elif msg.reply_to_message.photo:
            content = msg.reply_to_message.photo.file_id  # last elem = best quality
            data_type = Types.PHOTO

        elif msg.reply_to_message.audio:
            content = msg.reply_to_message.audio.file_id
            data_type = Types.AUDIO

        elif msg.reply_to_message.voice:
            content = msg.reply_to_message.voice.file_id
            data_type = Types.VOICE

        elif msg.reply_to_message.video:
            content = msg.reply_to_message.video.file_id
            data_type = Types.VIDEO

        elif msg.reply_to_message.video_note:
            content = msg.reply_to_message.video_note.file_id
            data_type = Types.VIDEO_NOTE

        elif msg.reply_to_message.animation:
            content = msg.reply_to_message.animation.file_id
            # text = None
            data_type = Types.ANIMATION

    # TODO
    # elif msg.reply_to_message.contact:
    # 	content = msg.reply_to_message.contact.phone_number
    # 	# text = None
    # 	data_type = Types.CONTACT

    # TODO
    # elif msg.reply_to_message.animated_sticker:
    #	content = msg.reply_to_message.animation.file_id
    #	text = None
    #	data_type = Types.ANIMATED_STICKER

    else:
        return None, None, None, None

    return note_name, text, data_type, content


def get_welcome_type(msg):
    data_type = None
    content = None

    if msg.reply_to_message:
        if msg.reply_to_message.text:
            text = msg.reply_to_message.text.markdown
        elif msg.reply_to_message.caption:
            text = msg.reply_to_message.caption.markdown
        else:
            text = None
    else:
        text = msg.text.split(None, 1)

    if msg.reply_to_message:
        if msg.reply_to_message.text:
            text = msg.reply_to_message.text.markdown
            data_type = Types.TEXT

        elif msg.reply_to_message.sticker:
            if msg.reply_to_message.document.mime_type == "application/x-tgsticker":
                data_type = Types.ANIMATED_STICKER
            else:
                data_type = Types.STICKER
            content = msg.reply_to_message.sticker.file_id
            text = None

        elif msg.reply_to_message.document:
            if msg.reply_to_message.document.mime_type == "application/x-bad-tgsticker":
                data_type = Types.ANIMATED_STICKER
            else:
                data_type = Types.DOCUMENT
            content = msg.reply_to_message.document.file_id
        # text = msg.reply_to_message.caption

        elif msg.reply_to_message.photo:
            content = msg.reply_to_message.photo[-1].file_id  # last elem = best quality
            # text = msg.reply_to_message.caption
            data_type = Types.PHOTO

        elif msg.reply_to_message.audio:
            content = msg.reply_to_message.audio.file_id
            # text = msg.reply_to_message.caption
            data_type = Types.AUDIO

        elif msg.reply_to_message.voice:
            content = msg.reply_to_message.voice.file_id
            text = None
            data_type = Types.VOICE

        elif msg.reply_to_message.video:
            content = msg.reply_to_message.video.file_id
            # text = msg.reply_to_message.caption
            data_type = Types.VIDEO

        elif msg.reply_to_message.video_note:
            content = msg.reply_to_message.video_note.file_id
            text = None
            data_type = Types.VIDEO_NOTE

        elif msg.reply_to_message.animation:
            content = msg.reply_to_message.animation.file_id
            # text = None
            data_type = Types.ANIMATION

    # TODO
    # elif msg.reply_to_message.animated_sticker:
    #	content = msg.reply_to_message.animation.file_id
    #	text = None
    #	data_type = Types.ANIMATED_STICKER

    else:
        if msg.caption:
            text = msg.caption.split(None, 1)
            if len(text) >= 2:
                text = msg.caption.markdown.split(None, 1)[1]
        elif msg.text:
            text = msg.text.split(None, 1)
            if len(text) >= 2:
                text = msg.text.markdown.split(None, 1)[1]
        data_type = Types.TEXT

    return text, data_type, content
