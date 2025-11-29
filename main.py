import discord
from discord.ext import commands
from always_on import keep_alive
import asyncio
from discord.ext.tasks import loop
import datetime
import random
from discord.utils import get
import json
import os
try:
    from discord_components import Button, ButtonStyle
except ImportError:
    # Fallback for when discord-components is not available
    Button = None
    ButtonStyle = None

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configData = {
        "Prefix": "!"
    }
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configData, f)

prefix = configData["Prefix"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)

color = 0xc935e1


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd,activity=discord.Activity(
        type=discord.ActivityType.watching, name="Ivory Project"))
    print("Bot Is Online")


#Member Commands
@bot.command(name="invites", description="See Your Invites")
async def invites(ctx):
    mention = ctx.author.mention
    totalInvites = 0
    for i in await ctx.guild.invites():
        if i.inviter == ctx.author:
            totalInvites += i.uses
    embed = discord.Embed(
        title="",
        description=
        f"Βρεθηκαν ``{totalInvites}`` invite(s) για τον {mention}",
        color=color)
    embed.set_author(name=ctx.author.display_name,
                     icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="leaderboard", description="See invite leaderboard", aliases=["lb"])
async def leaderboard(ctx, limit: int = 10):
    """Shows the invite leaderboard for the server"""
    if limit > 25:
        limit = 25
    if limit < 1:
        limit = 10
    
    invite_counts = {}
    
    for invite in await ctx.guild.invites():
        if invite.inviter:
            if invite.inviter.id not in invite_counts:
                invite_counts[invite.inviter.id] = {"user": invite.inviter, "count": 0}
            invite_counts[invite.inviter.id]["count"] += invite.uses
    
    sorted_invites = sorted(invite_counts.values(), key=lambda x: x["count"], reverse=True)
    
    if not sorted_invites:
        embed = discord.Embed(
            description="No invites found in this server.",
            color=color
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        return
    
    leaderboard_text = ""
    medals = ["🥇", "🥈", "🥉"]
    
    for i, data in enumerate(sorted_invites[:limit]):
        user = data["user"]
        count = data["count"]
        
        if i < 3:
            position = medals[i]
        else:
            position = f"**{i + 1}.**"
        
        leaderboard_text += f"{position} {user.mention} — ``{count}`` invite(s)\n"
    
    embed = discord.Embed(
        description=leaderboard_text,
        color=color
    )
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
    embed.set_thumbnail(url=ctx.guild.icon.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):

    if member == None:
        embed = discord.Embed(title="Avatar", description=f" ", color=color)
        embed.set_image(url=ctx.author.avatar.url)
        embed.set_footer(text="", icon_url=bot.user.avatar.url)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="Avatar", description=f" ", color=color)
        embed.set_image(url=member.avatar.url)
        embed.set_footer(text="", icon_url=bot.user.avatar.url)
        await ctx.send(embed=embed)


@bot.command(name="serverinfo",
             description="Shows info about the current server.",
             aliases=["server"])
async def serverinfo(ctx):
    embed = discord.Embed(
        title=f"Serverinfo",
        description="***Shows info about the current server***",
        color=color)
    roleCount = len(ctx.guild.roles)

    embed.set_thumbnail(url=str(ctx.guild.icon.url))

    embed.add_field(name="Verification Level",
                    value=str(ctx.guild.verification_level).capitalize(),
                    inline=False)
    embed.add_field(name="Region",
                    value=str(ctx.guild.region).capitalize(),
                    inline=False)
    embed.add_field(name="Server Owner",
                    value=str(ctx.guild.owner.mention),
                    inline=False)
    embed.add_field(
        name="Created On",
        value=ctx.guild.created_at.strftime("``%a, %#d %B %Y, %I:%M %p UTC``"),
        inline=False)
    embed.add_field(name=f"Roles:",
                    value=f"``{len(ctx.guild.roles)}``",
                    inline=False)
    embed.set_footer(icon_url=str(ctx.author.avatar.url),
                     text=f"Requested by {ctx.author.name}")
    embed.set_author(name=f'{ctx.guild.name}',
                     icon_url=f'{ctx.guild.icon.url}')
    embed.set_thumbnail(url=f'{ctx.guild.icon.url}')

    await ctx.send(embed=embed)


#Administrator Commands
@bot.command()
@commands.has_permissions(manage_channels=True)
async def say(ctx, *, message = None):
    if message == None:
        return
    else:
        embed = discord.Embed(title = '', description = message, color=color)
        embed.set_author(name=f'{ctx.guild.name}',icon_url=f'{ctx.guild.icon.url}')
        embed.set_thumbnail(url=f'{ctx.guild.icon.url}')
        await ctx.send(embed = embed)
        await ctx.message.delete() 

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    f = discord.Embed(
        color=color,
        description="The channel has been locked by the Server Management Team!"
    )
    await ctx.channel.send(embed=f)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    f = discord.Embed(
        color=color,
        description=
        "The channel has been unlocked by the Server Management Team!")
    await ctx.channel.send(embed=f)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"`{amount}` Messages has been cleared!", delete_after=2)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(
        f"They just entered {seconds} Slowdown seconds on this Channel!")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, reason=None):
    guild = ctx.guild
    await member.ban(reason=reason)

    embed = discord.Embed(
        title="Member Banned",
        description=f"**Member: {member.mention}** Reason: - **{reason}**",
        color=color)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.set_author(name=f'{ctx.guild.name}',
                     icon_url=f'{ctx.guild.icon.url}')
    embed.set_thumbnail(url=f'{ctx.guild.icon.url}')
    await ctx.send(embed=embed)

@bot.command()
async def unban(ctx, user_id: int):
    user_to_unban = await bot.fetch_user(user_id)
    await ctx.guild.unban(user_to_unban)
    unban_embed = discord.Embed(description=f'{user_id} unbanned!')


@bot.command()
@commands.has_permissions(manage_channels=True)
async def pptbc(ctx):
    embed = discord.Embed(
        title="",
        description=
        f"<:1141711451116032010:1161746809983619172> ttimpandis@gmail.com \n <a:alert:1284835178874929192> Friends & Family \n <a:alert:1284835178874929192> No Notes",
        color=color)
    embed.set_author(name=f'{ctx.guild.name}',icon_url=f'{ctx.guild.icon.url}')
    embed.set_thumbnail(url=f'{ctx.guild.icon.url}')
    await ctx.send(embed=embed)


#Logs
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name= '👥Members')
    await member.add_roles(role)

    mention = member.mention
    guild = member.guild

    embed = discord.Embed(
        title=str(""),
        color=color,
        description=str(f"{mention} joined to {guild}").format(mention=mention,
                                                               guild=guild))
    embed.set_thumbnail(url=f"{member.avatar.url}")
    embed.set_author(name=f"{member.name}", icon_url=f"{member.avatar.url}")
    embed.set_footer(text=f"{member.guild}",
                     icon_url=f"{member.guild.icon.url}")
    embed.add_field(name="User ID :", value=member.id)
    embed.add_field(name="User Name :", value=member.display_name)
    embed.add_field(
        name="Created at :",
        value=member.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))
    embed.add_field(
        name="Joined at :",
        value=member.joined_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))

    channel = discord.utils.get(member.guild.channels,
                                id=int("1421295359409258501"))
    await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):

    mention = member.mention
    guild = member.guild

    embed = discord.Embed(
        title=str(""),
        color=color,
        description=str(f"{mention} left from {guild}").format(mention=mention,
                                                               guild=guild))
    embed.set_thumbnail(url=f"{member.avatar.url}")
    embed.set_author(name=f"{member.name}", icon_url=f"{member.avatar.url}")
    embed.set_footer(text=f"{member.guild}",
                     icon_url=f"{member.guild.icon.url}")
    embed.add_field(name="User ID :", value=member.id)
    embed.add_field(name="User Name :", value=member.display_name)
    embed.add_field(
        name="Created at :",
        value=member.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))
    embed.add_field(
        name="Leaved at :",
        value=member.joined_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))

    channel = discord.utils.get(member.guild.channels,
                                id=int("1421295359409258501"))
    await channel.send(embed=embed)


@bot.event
async def on_message_delete(message):
    dChannel = bot.get_channel(1421295359409258505)
    
    # Only log if the channel exists and the message has content
    if dChannel and message.content:
        e = discord.Embed(title="Delete Chat Logs", color=color)
        e.add_field(name="Message: ", value=f"{message.content}", inline=False)
        e.add_field(name="Channel: ", value=message.channel.name, inline=False)
        e.add_field(name="Deleted By: ",
                    value=message.author.mention,
                    inline=False)
        await dChannel.send(embed=e)


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        dChannel = bot.get_channel(1421295359409258504)

        e = discord.Embed(title="Voice Logs | Connect", color=color)
        e.add_field(name="Channel: ", value=after.channel, inline=False)
        e.add_field(name="Member: ", value=member.mention, inline=False)
        await dChannel.send(embed=e)

    if before.channel and after.channel:
        dChannel = bot.get_channel(1421295359409258504)

        e = discord.Embed(title="Voice Logs | Move", color=color)
        e.add_field(name="Before Channel: ",
                    value=before.channel,
                    inline=False)
        e.add_field(name="After Channel: ", value=after.channel, inline=False)
        e.add_field(name="Member: ", value=member.mention, inline=False)
        await dChannel.send(embed=e)

    if before.channel and not after.channel:
        dChannel = bot.get_channel(1421295359409258504)
        e = discord.Embed(title="Voice Logs | Disconnect", color=color)
        e.add_field(name="Channel: ", value=before.channel, inline=False)
        e.add_field(name="Member: ", value=member.mention, inline=False)
        await dChannel.send(embed=e) 


@bot.event
async def on_member_ban(guild, member):
    logs = await guild.audit_logs(limit=1,
                                  action=discord.AuditLogAction.ban).flatten()
    channel = guild.get_channel(1421295359640211589)
    logs = logs[0]
    if logs.target == member:
        embed = discord.Embed(
            title="Member Banned",
            description=
            f"**{logs.user} has just banned {logs.target}. (The time is {logs.created_at})**",
            color=color)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="User ID :", value=member.id)
    await channel.send(embed=embed)


@bot.event
async def on_member_unban(guild, member):
    logs = await guild.audit_logs(
        limit=1, action=discord.AuditLogAction.unban).flatten()
    channel = guild.get_channel(1421295359640211589)
    logs = logs[0]
    if logs.target == member:
        embed = discord.Embed(
            title="Member Unbanned",
            description=
            f"**{logs.user} has just unbanned {logs.target}. (The time is {logs.created_at})**",
            color=color)
    embed.add_field(name="Name", value=member.name, inline=True)
    await channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        channel = bot.get_channel(1421295359409258502)

        def predicate(log):
            return log.target == after

        log = await before.guild.audit_logs(
            action=discord.AuditLogAction.member_role_update).find(predicate)
        e = discord.Embed(
            description=
            f'**Ενημέρωση ρόλων χρηστών - {before.mention} {f"από τον/ην {log.user.mention}" if log else ""}** ',
            color=color)
        e.add_field(name='**Ρόλοι πριν**',
                    value=[r.mention for r in before.roles])
        e.add_field(name='**Ρόλοι μετά**',
                    value=[r.mention for r in after.roles])
        await channel.send(embed=e)


# Ticket System - Modern implementation using discord.py 2.0 Views
class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose a Ticket Type",
        options=[
            discord.SelectOption(label="Collab", value="collab", emoji="🤝", description="Partnership inquiries"),
            discord.SelectOption(label="Purchase", value="buy", emoji="💸", description="Purchase inquiries and transactions"),
            discord.SelectOption(label="Report", value="report", emoji="🚫", description="Report issues or violations"),
            discord.SelectOption(label="Other", value="other", emoji="❓", description="Other inquiries and general support")
        ]
    )
    async def select_ticket_type(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        staff_role = discord.utils.get(guild.roles, id=1421295358520066144)
        management_role = discord.utils.get(guild.roles, id=1421295358553882666)

        # Find the ticket category
        category = discord.utils.get(guild.categories, id=1421295360747245654)
        if not category:
            await interaction.response.send_message("❌ Ticket category not found. Please contact an administrator.", ephemeral=True)
            return

        # Set up channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, attach_files=True, read_message_history=True
            )
        }
        
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, attach_files=True, 
                read_message_history=True, manage_messages=True, manage_channels=True
            )
        
        if management_role:
            overwrites[management_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, attach_files=True,
                read_message_history=True, manage_messages=True, manage_channels=True
            )

        # Create ticket channel based on type
        ticket_type = select.values[0]
        channel_names = {
            "collab": f"🤝collab-{interaction.user.name}",
            "buy": f"💸buy-{interaction.user.name}",
            "report": f"🚫report-{interaction.user.name}",
            "other": f"❓other-{interaction.user.name}"
        }

        try:
            channel = await category.create_text_channel(
                channel_names[ticket_type],
                overwrites=overwrites
            )

            # Send confirmation to user
            embed = discord.Embed(
                description=f'**Το Ticket δημιουργήθηκε {channel.mention}!**',
                color=color
            )
            embed.set_author(
                name=f'{interaction.user.name}#{interaction.user.discriminator}',
                url=f'https://discord.com/users/{interaction.user.id}',
                icon_url=interaction.user.avatar.url
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Send welcome message in ticket channel
            welcome_embed = discord.Embed(
                title='',
                description='```Please wait, the Ownership Team will serve you soon!```',
                color=color
            )
            welcome_embed.set_author(
                name=f'{interaction.user.name}#{interaction.user.discriminator} - {channel_names[ticket_type].split("-")[0]}',
                url=f"https://discord.com/users/{interaction.user.id}",
                icon_url=interaction.user.avatar.url
            )

            # Add close button to ticket
            close_view = TicketCloseView()
            await channel.send(f"{interaction.user.mention}", embed=welcome_embed, view=close_view)

            # Log ticket creation
            log_channel = bot.get_channel(1421295359640211588)
            if log_channel:
                log_embed = discord.Embed(
                    description=f"**Status:** `🟢`\n**{ticket_type.title()} Ticket Opened By:** {interaction.user.mention}",
                    color=discord.Color.green()
                )
                log_embed.set_author(name=f'{interaction.user}', icon_url=interaction.user.avatar.url)
                log_embed.set_footer(text=f'{guild.name}', icon_url=guild.icon.url)
                await log_channel.send(embed=log_embed)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create channels in this category.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating ticket: {str(e)}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        if not channel.name.startswith(('🤝collab-', '💸buy-', '🚫report-', '❓other-')):
            await interaction.response.send_message("❌ This command can only be used in ticket channels.", ephemeral=True)
            return

        # Check permissions
        member = interaction.guild.get_member(interaction.user.id)
        staff_role = discord.utils.get(interaction.guild.roles, id=1421295358520066144)
        management_role = discord.utils.get(interaction.guild.roles, id=1421295358553882666)
        
        is_ticket_owner = channel.name.endswith(f"-{interaction.user.name}")
        is_staff = staff_role in member.roles if staff_role else False
        is_management = management_role in member.roles if management_role else False
        
        if not (is_ticket_owner or is_staff or is_management):
            await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

        # Log ticket closure
        log_channel = bot.get_channel(1421295359640211588)
        if log_channel:
            log_embed = discord.Embed(
                description=f"**Status:** `🔴`\n**Ticket Closed By:** {interaction.user.mention}",
                color=discord.Color.red()
            )
            log_embed.set_author(name=f'{interaction.user}', icon_url=interaction.user.avatar.url)
            log_embed.set_footer(text=f'{interaction.guild.name}', icon_url=interaction.guild.icon.url)
            await log_channel.send(embed=log_embed)

        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        await channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx, channel: discord.TextChannel = None):
    """Create a ticket system panel"""
    embed = discord.Embed(
        title="",
        description="```For best service, you can select the type of ticket you want and we will assist you.```",
        color=color
    )
    embed.set_author(name=f'{ctx.guild.name}',icon_url=f'{ctx.guild.icon.url}')
    embed.set_thumbnail(url=f'{ctx.guild.icon.url}')
    
    view = TicketSelectView()
    target_channel = channel or ctx.channel
    await target_channel.send(embed=embed, view=view)
    
    if channel:
        await ctx.send(f"✅ Το Ticket δημιουργήθηκε {channel.mention}")
    else:
        await ctx.message.delete()

# Application System
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Submit Application", style=discord.ButtonStyle.green, emoji="📝")
    async def submit_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal())

class ApplicationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Staff Application Form")

    name = discord.ui.TextInput(
        label="Full Name",
        placeholder="Enter your full name...",
        required=True,
        max_length=100
    )
    
    age = discord.ui.TextInput(
        label="Age",
        placeholder="Enter your age...",
        required=True,
        max_length=3
    )
    
    experience = discord.ui.TextInput(
        label="Previous Experience",
        placeholder="Describe your previous moderation/staff experience...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    timezone = discord.ui.TextInput(
        label="Timezone",
        placeholder="Enter your timezone (e.g., EST, PST, GMT+2)...",
        required=True,
        max_length=50
    )
    
    why_staff = discord.ui.TextInput(
        label="Why do you want to be staff?",
        placeholder="Explain why you want to join our staff team...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Create application embed
        embed = discord.Embed(
            title="📝 New Staff Application",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(
            name=f"{interaction.user.name}#{interaction.user.discriminator}",
            icon_url=interaction.user.avatar.url
        )
        embed.add_field(name="👤 Full Name", value=self.name.value, inline=True)
        embed.add_field(name="🎂 Age", value=self.age.value, inline=True)
        embed.add_field(name="🌍 Timezone", value=self.timezone.value, inline=True)
        embed.add_field(name="💼 Previous Experience", value=self.experience.value, inline=False)
        embed.add_field(name="❓ Why Staff?", value=self.why_staff.value, inline=False)
        embed.add_field(name="📊 User ID", value=interaction.user.id, inline=True)
        embed.add_field(name="📅 Account Created", value=interaction.user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="📅 Joined Server", value=interaction.user.joined_at.strftime("%Y-%m-%d"), inline=True)

        # Send to application review channel (using log channel for now)
        review_channel = bot.get_channel(1421302158111801405)
        if review_channel:
            review_view = ApplicationReviewView(interaction.user.id)
            await review_channel.send(embed=embed, view=review_view)

        # Confirm to user
        await interaction.response.send_message(
            "✅ **Application Submitted Successfully!**\n"
            "Thank you for your interest in joining our staff team. "
            "Your application has been submitted and will be reviewed by our management team. "
            "You will be contacted if your application is approved.",
            ephemeral=True
        )

class ApplicationReviewView(discord.ui.View):
    def __init__(self, applicant_id):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has permission
        management_role = discord.utils.get(interaction.guild.roles, id=1421295358553882666)
        if management_role not in interaction.user.roles:
            await interaction.response.send_message("❌ You don't have permission to review applications.", ephemeral=True)
            return

        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            embed = discord.Embed(
                title="✅ Application Accepted",
                description=f"Application for {applicant.mention} has been **ACCEPTED** by {interaction.user.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            
            # Try to DM the applicant
            try:
                dm_embed = discord.Embed(
                    title="🎉 Application Accepted!",
                    description=f"Congratulations! Your staff application for **{interaction.guild.name}** has been accepted!",
                    color=discord.Color.green()
                )
                await applicant.send(embed=dm_embed)
            except:
                pass
        else:
            await interaction.response.send_message("❌ Applicant not found.", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="❌")
    async def reject_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has permission
        management_role = discord.utils.get(interaction.guild.roles, id=1421295358553882666)
        if management_role not in interaction.user.roles:
            await interaction.response.send_message("❌ You don't have permission to review applications.", ephemeral=True)
            return

        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            embed = discord.Embed(
                title="❌ Application Rejected",
                description=f"Application for {applicant.mention} has been **REJECTED** by {interaction.user.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            
            # Try to DM the applicant
            try:
                dm_embed = discord.Embed(
                    title="📋 Application Update",
                    description=f"Thank you for your interest in **{interaction.guild.name}**. Unfortunately, your staff application was not successful at this time.",
                    color=discord.Color.red()
                )
                await applicant.send(embed=dm_embed)
            except:
                pass
        else:
            await interaction.response.send_message("❌ Applicant not found.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def app(ctx, channel: discord.TextChannel = None):
    """Create an application system panel"""
    embed = discord.Embed(
        title="📝 Staff Application System",
        description="Interested in joining our staff team? Click the button below to submit your application!",
        color=color
    )
    embed.add_field(
        name="📋 Requirements",
        value="• Must be at least 16 years old\n• Previous moderation experience preferred\n• Active and mature\n• Good understanding of Discord",
        inline=False
    )
    embed.add_field(
        name="🔍 What we're looking for",
        value="• Responsible and trustworthy individuals\n• Good communication skills\n• Available for regular activity\n• Team-oriented mindset",
        inline=False
    )
    embed.set_footer(text="Click the button below to start your application")
    
    view = ApplicationView()
    target_channel = channel or ctx.channel
    await target_channel.send(embed=embed, view=view)
    
    if channel:
        await ctx.send(f"✅ Application system created in {channel.mention}")
    else:
        await ctx.message.delete()

# Bot startup
    guild = interaction.guild
    staff_role = discord.utils.get(interaction.guild.roles,
                                    id=1421295358520066144)
    management_role = discord.utils.get(interaction.guild.roles,
                                    id=1421295358553882666)

    overwrites = {
        guild.default_role:
        discord.PermissionOverwrite(view_channel=False),
        interaction.author:
        discord.PermissionOverwrite(view_channel=True,
                                    send_messages=False,
                                    attach_files=True,
                                    read_message_history=True),
        staff_role:
        discord.PermissionOverwrite(view_channel=True,
                                    send_messages=True,
                                    attach_files=True,
                                    read_message_history=True,
                                    manage_messages=True,
                                    manage_channels=True),
        management_role:
        discord.PermissionOverwrite(view_channel=True,
                                    send_messages=True,
                                    attach_files=True,
                                    read_message_history=True,
                                    manage_messages=True,
                                    manage_channels=True)
    }

    if interaction.values[0] == "collab":
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break

    if interaction.values[0] == "buy":
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break  

    if interaction.values[0] == "report":
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break  

    if interaction.values[0] == "other":
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break
  
    if interaction.values[0] == "collab":
        channel = await category.create_text_channel(
            f"🤝collab-{interaction.author.name}", overwrites=overwrites)

    if interaction.values[0] == "buy":
        channel = await category.create_text_channel(
            f"💸buy-{interaction.author.name}", overwrites=overwrites)  

    if interaction.values[0] == "report":
        channel = await category.create_text_channel(
            f"🚫report-{interaction.author.name}", overwrites=overwrites) 

    if interaction.values[0] == "other":
        channel = await category.create_text_channel(
            f"❓other-{interaction.author.name}", overwrites=overwrites)
  

    if interaction.values[0] == "collab":
      embed = discord.Embed(
        description=f'**Your Ticket has just been created {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)

    if interaction.values[0] == "buy":
      embed = discord.Embed(
        description=f'**Your Ticket has just been created {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)

    if interaction.values[0] == "report":
      embed = discord.Embed(
        description=f'**Your Ticket has just been created {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)
  
    if interaction.values[0] == "other":
      embed = discord.Embed(
        description=f'**Your Ticket has just been created {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)


    if interaction.values[0] == "collab":      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Collab Ticket Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421295359640211588)
        await channel2.send(embed=log)

    if interaction.values[0] == "buy":      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Buy Ticket Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421295359640211588)
        await channel2.send(embed=log)
  
    if interaction.values[0] == "report":      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Report Ticket Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421295359640211588)
        await channel2.send(embed=log)


    if interaction.values[0] == "other":      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Other Ticket Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421295359640211588    )
        await channel2.send(embed=log)
  
  
    if interaction.values[0] == "collab":
        embed = discord.Embed(
            title='',
            description=
            '```Please wait, the Ownership Team will serve you soon!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - 🤝Collab',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.set_permissions(management_role,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])

    if interaction.values[0] == "buy":
        embed = discord.Embed(
            title='',
            description=
            '```Please wait, the Ownership Team will serve you soon!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - 💸Buy',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.set_permissions(management_role,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])

    if interaction.values[0] == "report":
        embed = discord.Embed(
            title='',
            description=
            '```Please wait, the Ownership Team will serve you soon!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - 🚫Staff Report',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.set_permissions(management_role,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])

    if interaction.values[0] == "other":
        embed = discord.Embed(
            title='',
            description=
            '```Please wait, the Ownership Team will serve you soon!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - ❓Other',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(management_role,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])

@bot.event
async def on_button_click(interaction):

    if interaction.custom_id == "del":
        channel = bot.get_channel(interaction.custom_id)
        await interaction.channel.delete()

        log = discord.Embed(
            description=f"**Status:** `🔴`\n**Ticket Closed By:** {interaction.author.mention}",
            color=discord.Color.red())
        log.set_author(name=f'{interaction.author}', icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}', icon_url=interaction.guild.icon.url)
        log_channel = bot.get_channel(1421295359640211588)
        await log_channel.send(embed=log)
  
    guild = interaction.guild
    staff_role = discord.utils.get(interaction.guild.roles,
                                    id=1421295358520066144)
    management_role = discord.utils.get(interaction.guild.roles,
                                    id=1421295358553882666)
    overwrites = {
        guild.default_role:
        discord.PermissionOverwrite(view_channel=False),
        interaction.author:
        discord.PermissionOverwrite(view_channel=True,
                                    send_messages=False,
                                    attach_files=True,
                                    read_message_history=True),
        staff_role:
        discord.PermissionOverwrite(view_channel=False,
                                    send_messages=False,
                                    attach_files=False,
                                    read_message_history=False,
                                    manage_messages=False,
                                    manage_channels=False),
        management_role:
        discord.PermissionOverwrite(view_channel=False,
                                    send_messages=False,
                                    attach_files=False,
                                    read_message_history=False,
                                    manage_messages=False,
                                    manage_channels=False)
    }

    if interaction.component.id == 'staff':
        guild = guild = interaction.guild
    if interaction.component.id == 'manager':
        guild = guild = interaction.guild
  
    if interaction.component.id == 'staff':
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break
    if interaction.component.id == 'manager':
        for category in guild.categories:
            if category.id == 1421295360747245654:
                break
  
    if interaction.component.id == 'staff':
        channel = await category.create_text_channel(
          f"💼staff-{interaction.author.name}", overwrites=overwrites)
    if interaction.component.id == 'manager':
        channel = await category.create_text_channel(
          f"💼manager-{interaction.author.name}", overwrites=overwrites)



    if interaction.component.id == 'staff':
      embed = discord.Embed(
        description=f'**Το Staff Application σου μόλις δημιουργήθηκε {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)

    if interaction.component.id == 'manager':
      embed = discord.Embed(
        description=f'**Το Manager Application σου μόλις δημιουργήθηκε {channel.mention}!**',color=color)
      embed.set_author(name=f'{interaction.author.name}#{interaction.author.discriminator}',url='https://discord.com/users/{interaction.author.id}',icon_url=f'{interaction.author.avatar.url}')
      await interaction.respond(embed=embed)

    if interaction.component.id == 'staff':
        embed = discord.Embed(
            title='',
            description=
            '```Παρακαλω περιμενετε, το Ownership Team θα σας εξυπηρετησει συντομα!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - 💼Staff Application',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.set_permissions(management_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])
    if interaction.component.id == 'manager':
        embed = discord.Embed(
            title='',
            description=
            '```Παρακαλω περιμενετε, το Ownership Team θα σας εξυπηρετησει συντομα!```',
            color=color)
        embed.set_author(
            name=
            f'{interaction.author.name}#{interaction.author.discriminator} - 💼Manager Application',
            url=f"https://discord.com/users/{interaction.author.id}",
            icon_url=f'{interaction.author.avatar.url}')
        embed.set_footer(text="Click on 🔒 to delete the following ticket.")
        await channel.set_permissions(interaction.author,
                                                  view_channel=True,
                                                  send_messages=True)
        await channel.set_permissions(staff_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.set_permissions(management_role,
                                                  view_channel=False,
                                                  send_messages=False)
        await channel.send(embed=embed,
                                       components=[
                                           Button(custom_id='del',
                                                  style=ButtonStyle.red,
                                                  emoji='🔒')
                                       ])


    if interaction.component.id == 'staff':      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Staff Application Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421302158111801405)
        await channel2.send(embed=log)    

    if interaction.component.id == 'manager':      
        log = discord.Embed(
            description=
            f"**Status:** `🟢`   \n **Manager Application Opened By:** {interaction.author.mention}",
            color=discord.Color.green())
        log.set_author(name=f'{interaction.author._user}',
                       icon_url=f'{interaction.author.avatar.url}')
        log.set_footer(text=interaction.author.id)
        log.set_footer(text=f'{interaction.guild.name}',
                       icon_url=interaction.guild.icon.url)
        channel2 = bot.get_channel(1421302158111801405)
        await channel2.send(embed=log)

keep_alive()
try:
    bot.run(os.environ["token"])
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")
