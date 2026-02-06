import discord

import asyncio

import re

from discord.ext import commands

from discord.ui import View, Button, Select

from config import TOKEN, PREFIX, BOT_STATUS, EMBED_COLOR
import time

import discord


bot_start_time = time.time()

# ---------- INTENTS ----------

intents = discord.Intents.all()

bot = commands.Bot(

    command_prefix=PREFIX,

    intents=intents,

    help_command=None

)

# ---------- TEMP DATA ----------

afk_users = {}

auto_responses = {}

# ---------- READY ----------

@bot.event

async def on_ready():

    await bot.change_presence(

        activity=discord.Activity(

            type=discord.ActivityType.watching,

            name=BOT_STATUS

        )

    )

    print(f"✅ Logged in as {bot.user}")

# ---------- MESSAGE HANDLER ----------

@bot.event

async def on_message(message):

    if message.author.bot:

        return

    # AFK remove

    if message.author.id in afk_users:

        del afk_users[message.author.id]

        await message.channel.send(f"<a:519686excitedklee:1459170374502715586> Welcome back {message.author.mention}, AFK removed!")

    # Auto response

    for trigger, reply in auto_responses.items():

        if trigger.lower() in message.content.lower():

            await message.channel.send(reply)

    # Bot mention invite

    if bot.user in message.mentions:

        embed = discord.Embed(

            title=" <a:519686excitedklee:1459170374502715586> Hi! I'm Robin™",

            description="Click below to invite me to your server",

            color=EMBED_COLOR

        )

        view = View()

        view.add_item(Button(

            label="➕ Add Robin",

            url=f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"

        ))

        await message.channel.send(embed=embed, view=view)

    await bot.process_commands(message)

# ---------- PING ----------

@bot.command()

async def ping(ctx):

    await ctx.send(embed=discord.Embed(

        title="🏓 Pong",

        description=f"Latency: `{round(bot.latency*1000)}ms`",

        color=EMBED_COLOR

    ))

# ---------- AFK ----------

@bot.command()

async def afk(ctx, *, reason="AFK"):

    afk_users[ctx.author.id] = reason

    embed = discord.Embed(

        title="<:113449afk:1458356837819613277> AFK Enabled",

        description=f"Reason: **{reason}**",

        color=EMBED_COLOR

    )

    embed.set_thumbnail(url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# ---------- AUTO RESPONSE ----------

@bot.command()

@commands.has_permissions(administrator=True)

async def ar(ctx, action, trigger=None, *, response=None):

    if action == "add" and trigger and response:

        auto_responses[trigger] = response

        await ctx.send("✅ Auto response added")

    elif action == "remove" and trigger:

        auto_responses.pop(trigger, None)

        await ctx.send("🗑 Auto response removed")

    elif action == "list":

        await ctx.send(", ".join(auto_responses.keys()) or "No auto responses")

    else:

        await ctx.send("❌ Usage: !ar add/remove/list")

# ---------- ROLE ----------

@bot.command()

@commands.has_permissions(administrator=True)

async def role(ctx, role: discord.Role, member: discord.Member):

    if role.position >= ctx.guild.me.top_role.position:

        return await ctx.send("❌ My role must be higher.")

    await member.add_roles(role)

    await ctx.send(f"✅ {role.mention} given to {member.mention}")

# ---------- KICK ----------

@bot.command()

@commands.has_permissions(kick_members=True)

async def kick(ctx, member: discord.Member, *, reason="No reason"):

    await member.kick(reason=reason)

    await ctx.send(f"👢 {member} kicked")

# ---------- BAN ----------

@bot.command()

@commands.has_permissions(ban_members=True)

async def ban(ctx, member: discord.Member, *, reason="No reason"):

    await member.ban(reason=reason)

    await ctx.send(f"🔨 {member} banned")

# ---------- TIMEOUT ----------

@bot.command()

@commands.has_permissions(moderate_members=True)

async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason"):

    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)

    await ctx.send(f"⏳ {member} timed out for {minutes} minutes")

# ---------- LOCK / UNLOCK ----------

@bot.command()

@commands.has_permissions(manage_channels=True)

async def lock(ctx):

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

    await ctx.send("🔒 Channel locked")

@bot.command()

@commands.has_permissions(manage_channels=True)

async def unlock(ctx):

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

    await ctx.send("🔓 Channel unlocked")

# ---------- HIDE / UNHIDE ----------

@bot.command()

@commands.has_permissions(manage_channels=True)

async def hide(ctx):

    await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)

    await ctx.send("🙈 Channel hidden")

@bot.command()

@commands.has_permissions(manage_channels=True)

async def unhide(ctx):

    await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)

    await ctx.send("👁 Channel visible")

# ---------- DELETE CHANNEL ----------

@bot.command(name="del")

@commands.has_permissions(administrator=True)

async def delete_channel(ctx):

    await ctx.send("🗑 Deleting channel...")

    await ctx.channel.delete()

# ---------- HELP ----------

class HelpView(View):

    @discord.ui.select(

        placeholder="Select category",

        options=[

            discord.SelectOption(label="Utility"),

            discord.SelectOption(label="Moderation"),

            discord.SelectOption(label="Roles"),

            discord.SelectOption(label="Automation"),

        ]

    )

    async def select_callback(self, interaction, select):

        await interaction.response.edit_message(

            embed=discord.Embed(

                title=select.values[0],

                description="Commands listed here",

                color=EMBED_COLOR

            )

        )

@bot.command()

async def help(ctx):

    embed = discord.Embed(

        title="📜 Robin™ Help Menu",

        description="Use the dropdown below",

        color=EMBED_COLOR

    )

    await ctx.send(embed=embed, view=HelpView())

# --------dm 

@bot.command()

@commands.has_permissions(administrator=True)

async def dm(ctx, member: discord.Member, *, message):

    embed = discord.Embed(

        title="📩 You have a new message",

        description=message,

        color=EMBED_COLOR

    )

    embed.set_footer(text=f"Sent from {ctx.guild.name}")

    embed.set_thumbnail(

        url=ctx.guild.icon.url if ctx.guild.icon else bot.user.display_avatar.url

    )

    try:

        await member.send(embed=embed)

        await ctx.send(f"✅ DM sent to {member.mention}")

    except discord.Forbidden:

        await ctx.send("❌ I can't DM this user (DMs closed).")

    except Exception:

        await ctx.send("❌ Failed to send DM.")
# ---------- TICKET CONFIG ----------

ticket_title = "🎫 Support Ticket"

ticket_image = None

# ---------- TICKET VIEW ----------

class TicketView(View):

    def __init__(self):

        super().__init__(timeout=None)

    @discord.ui.button(label="🎟 Create Ticket", style=discord.ButtonStyle.green)

    async def create_ticket(self, interaction: discord.Interaction, button: Button):

        guild = interaction.guild

        user = interaction.user

        category = discord.utils.get(guild.categories, name="TICKETS")

        if not category:

            category = await guild.create_category("TICKETS")

        overwrites = {

            guild.default_role: discord.PermissionOverwrite(view_channel=False),

            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),

            guild.me: discord.PermissionOverwrite(view_channel=True),

        }

        channel = await guild.create_text_channel(

            name=f"ticket-{user.name}",

            overwrites=overwrites,

            category=category

        )

        embed = discord.Embed(

            title="🎫 Ticket Created",

            description=f"{user.mention}, please describe your issue.",

            color=EMBED_COLOR

        )

        await channel.send(embed=embed, view=TicketControlView())

        await interaction.response.send_message(

            f"✅ Ticket created: {channel.mention}",

            ephemeral=True

        )

class TicketControlView(View):

    def __init__(self):

        super().__init__(timeout=None)

    @discord.ui.button(label="🧑‍💼 Claim", style=discord.ButtonStyle.blurple)

    async def claim(self, interaction: discord.Interaction, button: Button):

        await interaction.channel.send(

            f"🧑‍💼 Ticket claimed by {interaction.user.mention}"

        )

        await interaction.response.defer()

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)

    async def close(self, interaction: discord.Interaction, button: Button):

        await interaction.channel.send("🔒 Closing ticket...")

        await interaction.channel.delete()

# ---------- TICKET COMMAND ----------

@bot.command()

@commands.has_permissions(administrator=True)

async def ticket(ctx, option=None, *, value=None):

    global ticket_title, ticket_image

    if option == "title" and value:

        ticket_title = value

        await ctx.send("✅ Ticket title updated")

        return

    if option == "img" and value:

        ticket_image = value

        await ctx.send("🖼 Ticket image updated")

        return

    embed = discord.Embed(

        title=ticket_title,

        description="Click the button below to open a ticket.",

        color=EMBED_COLOR

    )

    if ticket_image:

        embed.set_image(url=ticket_image)

    await ctx.send(embed=embed, view=TicketView())

# ---------- UPDATE PANEL ----------

@bot.command()

@commands.has_permissions(administrator=True)

async def update(ctx):

    embed = discord.Embed(

        title=ticket_title,

        description="Click the button below to open a ticket.",

        color=EMBED_COLOR

    )

    if ticket_image:

        embed.set_image(url=ticket_image)

    await ctx.send("🔄 Ticket panel updated:", embed=embed, view=TicketView())
#---------
@bot.command()

async def mc(ctx):

    guild = ctx.guild

    total_members = guild.member_count

    bots = len([m for m in guild.members if m.bot])

    humans = total_members - bots

    online = len([m for m in guild.members if m.status != discord.Status.offline])

    embed = discord.Embed(

        title="👥 Server Member Count",

        color=discord.Color.blurple()

    )

    embed.add_field(name="👥 Total Members", value=total_members, inline=False)

    embed.add_field(name="🟢 Online", value=online, inline=True)

    embed.add_field(name="👤 Humans", value=humans, inline=True)

    embed.add_field(name="🤖 Bots", value=bots, inline=True)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)
    
#------------ari
@bot.command()

@commands.has_permissions(administrator=True)

async def ari(ctx, action=None, trigger=None, url=None):

    if ctx.guild.id not in ari_data:

        ari_data[ctx.guild.id] = {}

    if action == "add":

        if not trigger or not url:

            return await ctx.send("❌ Usage: `!ari add <trigger> <image_url>`")

        ari_data[ctx.guild.id][trigger.lower()] = url

        await ctx.send(f"✅ Image auto-response added for **{trigger}**")

    elif action == "remove":

        if trigger.lower() in ari_data[ctx.guild.id]:

            del ari_data[ctx.guild.id][trigger.lower()]

            await ctx.send(f"🗑️ Removed image auto-response for **{trigger}**")

        else:

            await ctx.send("❌ Trigger not found")

    else:

        await ctx.send("❌ Use `!ari add` or `!ari remove`")
#----------- reminder ---------


@bot.command(name="rem")

async def reminder(ctx, *, args: str):

    try:

        parts = args.split()

        if len(parts) < 3:

            return await ctx.send("❌ Use: `!rem <text> <time> <dm/srv>`")

        where = parts[-1].lower()

        time_part = parts[-2]

        message = " ".join(parts[:-2])

        if where not in ["dm", "srv"]:

            return await ctx.send("❌ Last argument must be `dm` or `srv`")

        match = re.match(r"(\d+)([smh])", time_part)

        if not match:

            return await ctx.send("❌ Time format: `10s`, `5m`, `2h`")

        value = int(match.group(1))

        unit = match.group(2)

        seconds = value

        if unit == "m":

            seconds *= 60

        elif unit == "h":

            seconds *= 3600

        await ctx.send(f"⏰ Reminder set for **{value}{unit}**")

        await asyncio.sleep(seconds)

        embed = discord.Embed(

            title="⏰ Reminder",

            description=message,

            color=discord.Color.yellow()

        )

        embed.set_footer(text=f"Requested by {ctx.author}")

        if where == "dm":

            try:

                await ctx.author.send(embed=embed)

            except:

                await ctx.send("❌ I can't DM you. Enable DMs.")

        else:

            await ctx.send(embed=embed)

    except Exception as e:

        await ctx.send("❌ Error while setting reminder")

        print(e)
 #------------rename---------
@bot.command(name="rename")

@commands.has_permissions(manage_channels=True)

async def rename_channel(ctx, *, new_name: str):

    try:

        old_name = ctx.channel.name

        await ctx.channel.edit(name=new_name)

        embed = discord.Embed(

            title="✏️ Channel Renamed",

            description=f"**{old_name}** ➜ **{new_name}**",

            color=discord.Color.yellow()

        )

        embed.set_footer(text=f"Renamed by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        await ctx.send(embed=embed)

    except discord.Forbidden:

        await ctx.send("❌ I don't have permission to rename this channel.")

    except Exception as e:

        await ctx.send("❌ Failed to rename channel.")

        print(e)
#-----------calculator---------
@bot.command(name="cal")

async def calculate(ctx, *, expression: str):

    try:

        # Allow only safe characters

        allowed = "0123456789+-*/(). "

        for char in expression:

            if char not in allowed:

                return await ctx.send("❌ Invalid characters in expression")

        # Calculate result

        result = eval(expression)

        embed = discord.Embed(

            title="🧮 Calculator",

            color=discord.Color.green()

        )

        embed.add_field(name="📥 Expression", value=f"`{expression}`", inline=False)

        embed.add_field(name="📤 Result", value=f"`{result}`", inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    except ZeroDivisionError:

        await ctx.send("❌ Cannot divide by zero")

    except Exception as e:

        await ctx.send("❌ Invalid calculation")

        print(e)
#-----------------roboin information --
@bot.command(name="ri")

async def robin_info(ctx):

    uptime_seconds = int(time.time() - bot_start_time)

    hours, remainder = divmod(uptime_seconds, 3600)

    minutes, seconds = divmod(remainder, 60)

    uptime = f"{hours}h {minutes}m {seconds}s"

    embed = discord.Embed(

        title="🤖 Robin Bot Info",

        color=discord.Color.blurple()

    )

    embed.add_field(name="👨‍💻 Developer", value="Shubh Srivastav", inline=False)

    embed.add_field(name="⏱️ Uptime", value=uptime, inline=False)

    embed.add_field(name="👤 Requested By", value=ctx.author.mention, inline=False)

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.set_footer(

        text=f"Robin • Requested by {ctx.author}",

        icon_url=ctx.author.display_avatar.url

    )

    await ctx.send(embed=embed)
#-----------yt------------
@bot.command(name="sh")

async def yt_search(ctx, *, topic: str):

    try:

        query = urllib.parse.quote(topic)

        url = f"https://www.youtube.com/results?search_query={query}"

        embed = discord.Embed(

            title="🔎 YouTube Search",

            description=f"**Search:** {topic}",

            color=discord.Color.red()

        )

        embed.add_field(

            name="🎥 Watch on YouTube",

            value=f"[Click here to open results]({url})",

            inline=False

        )

        embed.set_footer(

            text=f"Requested by {ctx.author}",

            icon_url=ctx.author.avatar.url if ctx.author.avatar else None

        )

        await ctx.send(embed=embed)

    except Exception as e:

        await ctx.send("❌ Error while searching YouTube.")

        print(e)
#------------clock------
@bot.command(name="clock")

async def live_clock(ctx):

    embed = discord.Embed(

        title="🕒 Live Digital Clock",

        description="Starting clock...",

        color=discord.Color.blue()

    )

    embed.set_footer(

        text=f"Requested by {ctx.author}",

        icon_url=ctx.author.avatar.url if ctx.author.avatar else None

    )

    msg = await ctx.send(embed=embed)

    while True:

        now = datetime.datetime.now()

        time_str = now.strftime("%H:%M:%S")

        date_str = now.strftime("%d %B %Y")

        embed.description = (

            f"```\n"

            f"{time_str}\n"

            f"{date_str}\n"

            f"```"

        )

        try:

            await msg.edit(embed=embed)

            await asyncio.sleep(1)

        except discord.NotFound:

            break

        except discord.Forbidden:

            break

        except Exception as e:

            print(e)

            break
#---------- RUN ----------

bot.run(TOKEN)