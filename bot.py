
import asyncio
from collections import namedtuple
from datetime import datetime
import logging
import time

import discord
from discord.ext import commands
import humanize
import matplotlib.pyplot as plt

import logging_config
import plotting_cmds

### Parameters and initialization ###

logger = logging.getLogger(__name__)

with open('token.txt') as f:
    TOKEN = f.read()

count_data = namedtuple('CountData', ['timestamp', 'sample_size', 'data'])
DATA_REPO = {}
"""
DATA_REPO is structured as:
	{guild_id : (timestamp, 
				sample_size (int or 'all'), 
				{emote : count, emote : count, ...}
				)
	} 
"""

bot = commands.Bot(command_prefix='!', case_insensitive=True)
freq_plotter = plotting_cmds.FreqPlot()
count_plotter = plotting_cmds.CountPlot()

### Bot events ###

@bot.event
async def on_command_error(ctx, e):
	if isinstance(e, commands.BadArgument):
		await ctx.send(e)
	else:
		logger.error(e)

@bot.event
async def on_ready():
	logger.info("~~~ EMOJIBOT5000 online ~~~")
	for guild in bot.guilds:
		logger.info(f"Connected to {guild.name} server!")

### Actual bot commands ###

@bot.command()
async def count(ctx, limit:int=None):
	""" Counts custom emoji usages and stores for later.
	Takes optional limit #, for how may msgs to look back.
	"""
	logger.info(f"{ctx.command} command received")
	logger.verbose(f"User: {ctx.author}, Args: {ctx.args}")
	# Send intro message
	if type(limit) is int:
		post_msg = f"Counting reactions from last {limit} posts..."
		pass
	elif limit is None:
		post_msg = f"Counting all reactions. This'll take a bit..."
		pass
	post = await ctx.send(post_msg)
	await ctx.message.delete()

	# Do the actual count
	emo_count = {emote:0 for emote in ctx.guild.emojis}
	for channel in ctx.guild.text_channels:
		start = time.time()
		channel_total = 0
		await post.edit(content= post.content + 
			f"\nOn channel: {channel.name}")
		msg_list = channel.history(limit=limit)
		async for msg in msg_list:
			for react in msg.reactions:
				if react.emoji in emo_count:
					emo_count[react.emoji] += react.count
					channel_total += react.count
		await post.edit(content = post.content +
			f"\nCount time: {humanize.naturaldelta(time.time() - start)}" +
			f", Total counted: {channel_total}")

	# Store data and clean-up
	if limit is None:
		sample_size = 'all'
	else:
		sample_size = limit
	DATA_REPO[ctx.guild.id] = count_data(datetime.now(), sample_size, emo_count)
	await post.edit(content = post.content + "\nDone!")
	await post.delete(delay=60)

@bot.command()
async def plot(ctx, plot_type:str="all", amount:int=0):
	""" Generates plots from already counted data.
	Plots total uses for each emoji, in the counted interval.
	Plot types are "top x", "bottom x", and "all".
	"""
	logger.info(f"{ctx.command} command received")
	logger.verbose(f"User: {ctx.author}, Args: {ctx.args}")
	count_data = DATA_REPO[ctx.guild.id] 
	plot_filename = count_plotter.plot(count_data, plot_type, amount)
	await ctx.message.delete()
	await ctx.send(file=discord.File(plot_filename))

@bot.command()
async def freq(ctx, plot_type:str="all", amount:int=0):
	""" Generates plots from already counted data.
	Plots uses/day for each emoji, in the counted interval.
	Plot types are "top x", "bottom x", and "all".
	"""
	logger.info(f"{ctx.command} command received")
	logger.verbose(f"User: {ctx.author}, Args: {ctx.args}")
	count_data = DATA_REPO[ctx.guild.id] 
	plot_filename = freq_plotter.plot(count_data, plot_type, amount)
	await ctx.message.delete()
	await ctx.send(file=discord.File(plot_filename))

### Run that bot! ###

bot.run(TOKEN)
