from dotenv import load_dotenv
import os
import discord
import proxmoxer
import sqlite3
from discord.ext import commands
from backend import *

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

load_dotenv()

CONTROLLERADDR = os.getenv("CONTROLLERADDR")
ROOTPASS = os.getenv("ROOTPASS")
TOKEN = os.getenv("DISCORDTOKEN")
SERVER = os.getenv("DISCORDSERVER")
CHANNELID = os.getenv("CHANNELID")
ADMIN = os.getenv("ADMIN")

treknet = proxmoxer.ProxmoxAPI(CONTROLLERADDR, user="root@pam", password=ROOTPASS, verify_ssl=False)

intents = discord.Intents.default()
intents.presences = False
intents.typing = False
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == SERVER, bot.guilds)
    print(f"{bot.user} is connected to {guild.name} ({guild.id})")

async def on_message(message):
    if message.channel.id != int(CHANNELID):
        return
    await bot.process_commands(message)

@bot.command(brief="Tests to see if bot is online and working")
async def test(ctx):
    await ctx.send("Testing... I think it works")

@bot.command(brief="Creates VM")
async def create(ctx, arg1: str = commands.parameter(description="  |   OS for VM (win10, win11, winserv-19, winserv-22, ubuntu, mint)")):
    oses = ["win10", "win11", "winserv-19", "winserv-22", "ubuntu", "mint"]
    if not (arg1 in oses):
        await ctx.send("Invalid OS type. Use the '/help create' command to see the options")
        return
    newVM = cloneVM(cursor, treknet, arg1, ctx.author)
    if newVM == False:
        await ctx.send(f"You already have a vm, use the /status command to see details")
    else:
        if newVM[1] < 10:
            await ctx.send(f"New VM: (id: {newVM[0]}, vncport: 590{newVM[1]}, node: {newVM[2]})")
        else:
            await ctx.send(f"New VM: (id: {newVM[0]}, vncport: 59{newVM[1]}, node: {newVM[2]})")

@bot.command()
async def acreate(ctx, arg1, arg2):
    if ctx.author != ADMIN:
        ctx.send("You do not have permission to run this command")
        return
    oses = ["win10", "win11", "winserv-19", "winserv-22", "ubuntu", "mint"]
    if not (arg1 in oses):
        await ctx.send("Invalid OS type. Use the '/help create' command to see the options")
        return
    newVM = cloneVM(cursor, treknet, arg1, arg2)
    if newVM == False:
        await ctx.send("This user already has a vm, use the /status command to see details")
    else:
        if newVM[1] < 10:
            await ctx.send(f"New VM: (id: {newVM[0]}, vncport: 590{newVM[1]}, node: {newVM[2]})")
        else:
            await ctx.send(f"New VM: (id: {newVM[0]}, vncport: 59{newVM[1]}, node: {newVM[2]})")

@bot.command(brief="Shuts down VM")
async def shutdown(ctx):
    stat = powerVM(cursor, treknet, ctx.author, "shutdown")
    if stat == False:
        await ctx.send("You do not have a VM yet! Use the /create command to make one")
    else:
        await ctx.send(f"Shutting down VM... (this may take up to a minute, and it may time out, so be prepared to try a shutdown again)")

@bot.command()
async def ashutdown(ctx, arg1):
    if ctx.author != ADMIN:
        ctx.send("You do not have permission to run this command")
        return
    stat = powerVM(cursor, treknet, arg1, "shutdown")
    if stat == False:
        await ctx.send("This person does not have a vm yet")
    else:
        await ctx.send("Shutting down VM...")

@bot.command(brief="Starts VM")
async def start(ctx):
    stat = powerVM(cursor, treknet, ctx.author, "start")
    if stat == False:
        await ctx.send("You do not have a VM yet! Use the /create command to make one")
    else:
        await ctx.send(f"Started VM")

@bot.command()
async def start(ctx, arg1):
    if ctx.author != ADMIN:
        ctx.send("You do not have permission to run this command")
        return
    stat = powerVM(cursor, treknet, arg1, "start")
    if stat == False:
        await ctx.send("This person does not have a VM yet")
    else:
        await ctx.send("Started VM")

@bot.command(brief="Deletes VM")
async def delete(ctx, arg1: str = commands.parameter(default="Do not delete me", description="  |   Confirmation for deletion, must be set to \"I want to delete it\"")):
    if arg1 == "I want to delete it":
        stat = delVM(cursor, treknet, ctx.author)
        if stat == False:
            await ctx.send("You do not have a VM yet! Use the /create command to make one")
        elif stat == 10:
            await ctx.send("Your VM is still running, you can't delete it unless it is powered down")
        else:
            await ctx.send("Deleted VM")
    else:
        await ctx.send("""The first argument needs to be \"I want to delete it\" exactly, for accidental deletion protection
(e.g. `/delete \"I want to delete it\"`""")

@bot.command()
async def adelete(ctx, arg1, arg2):
    if ctx.author != ADMIN:
        ctx.send("You do not have permission to run this command")
        return
    if arg1 == "I want to delete it":
        stat = delVM(cursor, treknet, arg2)
        if stat == False:
            await ctx.send("This user does not have a VM yet")
        elif stat == 10:
            await ctx.send("The VM is still running")
        else:
            await ctx.send("Deleted VM")
    else:
        await ctx.send("Needs verification")

@bot.command(brief="Hard stops VM")
async def stop(ctx):
    stat = powerVM(cursor, treknet, ctx.author, "stop")
    if stat == False:
        await ctx.send("You do not have a VM yet! Use the /create command to make one")
    else:
        await ctx.send("Stopping VM... (this may take up to 10 seconds)")

@bot.command()
async def astop(ctx, arg1):
    if ctx.author != ADMIN:
        await ctx.send("You do not have permission to run this command")
        return
    stat = powerVM(cursor, treknet, arg2, "stop")
    if stat == False:
        await ctx.send("This user does not have a VM yet")
    else:
        await ctx.send("Stopped VM")

@bot.command(brief="Hard resets VM")
async def reset(ctx):
    stat = powerVM(cursor, treknet, ctx.author, "reset")
    if stat == False:
        await ctx.send("You do not have a VM yet! Use the /create command to make one")
    else:
        await ctx.send("Resetting VM... (this may take up to 10 seconds)")

@bot.command()
async def areset(ctx, arg1):
    if ctx.author != ADMIN:
        await ctx.send("You do not have permission to run this command")
        return
    stat = powerVM(cursor, treknet, arg1, "reset")
    if stat == False:
        await ctx.send("This user does not have a VM yet")
    else:
        await ctx.send("Reset VM")

@bot.command(brief="Shows information about VM")
async def status(ctx):
    vm = vmstat(cursor, treknet, ctx.author)
    if vm == False:
        await ctx.send("You do not have a VM yet! Use the /create command to make one")
        return
    if vm[1] < 10:
        await ctx.send(f"""ID: {vm[0]}, VNC Port: 590{vm[1]}, Node: {vm[2]}
Connection URI: `vnc://{vm[2]}.trek.net:590{vm[1]}`
Status: {vm[3]}""")
    else:
        await ctx.send(f"""ID: {vm[0]}, VNC Port: 59{vm[1]}, Node: {vm[2]}
Connection URI: `vnc://{vm[2]}.trek.net:59{vm[1]}`
Status: {vm[3]}""")

@bot.command()
async dev astatus(ctx, arg1):
    if ctx.author != ADMIN:
        await ctx.send("You do not have permission to run this command")
        return
    vm = vmstat(cursor, treknet, arg1)
    if vm == False:
        await ctx.send("This user does not have a VM yet")
        return
    if vm[1] < 10:
        await ctx.send(f"""ID: {vm[0]}, VNC Port: 590{vm[1]}, Node: {vm[2]}
Connection URI: `vnc://{vm[2].trek.net:590{vm[1]}`
Status: {vm[3]}""")
    else:
        await ctx.send(f"""ID: {vm[0]}, VNC Port: 59{vm[1]}, Node: {vm[2]}
Connection URI: `vnc://{vm[2].trek.net:59{vm[1]}`
Status: {vm[3]}""")

bot.on_message = on_message
bot.run(TOKEN)

conn.commit()
conn.close():wq

