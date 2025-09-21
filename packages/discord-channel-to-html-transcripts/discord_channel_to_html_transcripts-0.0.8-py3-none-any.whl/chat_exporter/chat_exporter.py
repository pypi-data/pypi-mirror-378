import datetime
import io
from typing import List, Optional, TYPE_CHECKING

from chat_exporter.construct.transcript import Transcript
from chat_exporter.ext.discord_import import discord
from chat_exporter.construct.attachment_handler import AttachmentHandler, AttachmentToLocalFileHostHandler, AttachmentToDiscordChannelHandler

if TYPE_CHECKING:
    import discord as discord_typings

async def quick_export(
    channel: "discord_typings.TextChannel",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
):
    """
    Create a quick export of your Discord channel.
    This function will produce the transcript and post it back in to your channel.
    :param channel: discord.TextChannel
    :param guild: (optional) discord.Guild
    :param bot: (optional) discord.Client
    :return: discord.Message (posted transcript)
    """

    if guild:
        channel.guild = guild

    transcript = (
        await Transcript(
            channel=channel,
            limit=None,
            messages=None,
            pytz_timezone="UTC",
            military_time=True,
            fancy_times=True,
            before=None,
            after=None,
            bot=bot,
            attachment_handler=None
            ).export()
        ).html

    if not transcript:
        return

    transcript_embed = discord.Embed(
        description=f"**Transcript Name:** transcript-{channel.name}\n\n",
        colour=discord.Colour.blurple()
    )

    transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html")
    return await channel.send(embed=transcript_embed, file=transcript_file)

async def export(
    channel: "discord_typings.TextChannel",
    limit: Optional[int] = None,
    tz_info="UTC",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
    military_time: Optional[bool] = True,
    fancy_times: Optional[bool] = True,
    before: Optional[datetime.datetime] = None,
    after: Optional[datetime.datetime] = None,
    attachment_handler: Optional[AttachmentHandler] = None,
):
    """
    Create a customised transcript of your Discord channel.
    This function will return the transcript which you can then turn in to a file to post wherever.
    :param channel: discord.TextChannel - channel to Export
    :param limit: (optional) integer - limit of messages to capture
    :param tz_info: (optional) TZ Database Name - set the timezone of your transcript
    :param guild: (optional) discord.Guild - solution for edpy
    :param bot: (optional) discord.Client - set getting member role colour
    :param military_time: (optional) boolean - set military time (24hour clock)
    :param fancy_times: (optional) boolean - set javascript around time display
    :param before: (optional) datetime.datetime - allows before time for history
    :param after: (optional) datetime.datetime - allows after time for history
    :param attachment_handler: (optional) attachment_handler.AttachmentHandler - allows custom asset handling
    :return: string - transcript file make up
    """
    if guild:
        channel.guild = guild

    return (
        await Transcript(
            channel=channel,
            limit=limit,
            messages=None,
            pytz_timezone=tz_info,
            military_time=military_time,
            fancy_times=fancy_times,
            before=before,
            after=after,
            bot=bot,
            attachment_handler=attachment_handler,
        ).export()
    ).html

async def raw_export(
    channel: "discord_typings.TextChannel",
    messages: List["discord_typings.Message"],
    tz_info="UTC",
    guild: Optional["discord_typings.Guild"] = None,
    bot: Optional["discord_typings.Client"] = None,
    military_time: Optional[bool] = False,
    fancy_times: Optional[bool] = True,
    attachment_handler: Optional[AttachmentHandler] = None,
):
    """
    Create a customised transcript with your own captured Discord messages
    This function will return the transcript which you can then turn in to a file to post wherever.
    :param channel: discord.TextChannel - channel to Export
    :param messages: List[discord.Message] - list of Discord messages to export
    :param tz_info: (optional) TZ Database Name - set the timezone of your transcript
    :param guild: (optional) discord.Guild - solution for edpy
    :param bot: (optional) discord.Client - set getting member role colour
    :param military_time: (optional) boolean - set military time (24hour clock)
    :param fancy_times: (optional) boolean - set javascript around time display
    :param attachment_handler: (optional) AttachmentHandler - allows custom asset handling
    :return: string - transcript file make up
    """
    if guild:
        channel.guild = guild

    return (
        await Transcript(
            channel=channel,
            limit=None,
            messages=messages,
            pytz_timezone=tz_info,
            military_time=military_time,
            fancy_times=fancy_times,
            before=None,
            after=None,
            bot=bot,
            attachment_handler=attachment_handler
        ).export()
    ).html