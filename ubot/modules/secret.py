from ubot import *

__MODULE__ = "secret"
__HELP__ = """
<b>『 ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ sᴇᴄʀᴇᴛ 』</b>

  <b>• ᴘᴇʀɪɴᴛᴀʜ:</b> <code>{0}msg [ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ - ᴛᴇxᴛ]</code>
  <b>• ᴘᴇɴᴊᴇʟᴀsᴀɴ:</b> ᴜɴᴛᴜᴋ ᴍᴇɴɢɪʀɪᴍ ᴘᴇsᴀɴ sᴇᴄᴀʀᴀ ʀᴀʜᴀsɪᴀ.
"""


@PY.UBOT("msg", SUDO=True)
async def _(client, message):
    await msg_cmd(client, message)


@PY.INLINE("^secret")
@INLINE.QUERY
async def _(client, inline_query):
    await secret_inline(client, inline_query)
