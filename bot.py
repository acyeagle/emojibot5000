
from datetime import datetime
import logging
from time import time as get_time
from typing import List

import discord
from discord.ext import commands
import humanize
import pandas as pd

import logging_config
from plot_cmds import FreqPlot, CountPlot, TimePlot

### Parameters and initialization ###

logger = logging.getLogger(__name__)

with open('token.txt') as f:
	TOKEN = f.read()

DATA_REPO = {}	# {guild_id : latest count DataFrame}

bot = commands.Bot(command_prefix='!', case_insensitive=True)
freq_plotter = FreqPlot()
count_plotter = CountPlot()
time_plotter = TimePlot()

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
		logger.info('Connected to %s server!', guild.name)

### Actual bot commands ###

@bot.command()
async def count(ctx, limit:int=None):
	""" Counts custom emoji usages and stores for later.
	Takes optional limit #, for how may msgs to look back.
	"""
	logger.info("%s command received", ctx.command)
	logger.verbose("User: %s, Args: %s", ctx.author, ctx.args)
	logger.info('Connected to %s server!', ctx.guild.name)
	# Send intro message
	if isinstance(limit, int):
		post_msg = f"Counting reactions from last {limit} posts..."
	elif limit is None:
		post_msg = "Counting all reactions. This'll take a bit..."
	post = await ctx.send(post_msg)
	await ctx.message.delete()

	# DataFrame and metadata
	count_data = pd.DataFrame()
	count_metadata = {"timestamp" : datetime.now()}
	if limit is None:
		count_metadata['msg_sample_size'] = 'all'
	else:
		count_metadata['msg_sample_size'] = limit

	# Count
	for channel in ctx.guild.text_channels:
		start = get_time()
		channel_total = 0

		await post.edit(content= post.content +
			f"\nOn channel: {channel.name}")

		msg_list = channel.history(limit=limit)
		async for msg in msg_list:
			for react in msg.reactions:
				if react.emoji in ctx.guild.emojis:
					row = {"name" : react.emoji.name,
						   "id": react.emoji.id,
						   "time" : msg.created_at,
						   "count" : react.count,
						  }
					channel_total += react.count
					count_data = count_data.append(row, ignore_index=True)

		await post.edit(content = post.content +
			f"\nCount time: {humanize.naturaldelta(get_time() - start)}" +
			f", Total counted: {channel_total}")

	# Store data and clean-up
	DATA_REPO[ctx.guild.id] = {"data" : count_data, "metadata" : count_metadata}
	count_data.to_csv("testing_data.csv")
	await post.edit(content = post.content + "\nDone!")
	await post.delete(delay=60)

@bot.command()
async def plot(ctx, plot_type:str="all", amount:int=0):
	""" Generates plots from already counted data.
	Plots total uses for each emoji, in the counted interval.
	Plot types are "top x", "bottom x", and "all".
	"""
	logger.info("%s command received", ctx.command)
	logger.verbose("User: %s, Args: %s", ctx.author, ctx.args)
	count_data = DATA_REPO[ctx.guild.id]['data']
	count_metadata = DATA_REPO[ctx.guild.id]['metadata']
	plot_filename = count_plotter.plot(count_data=count_data,
									   count_metadata=count_metadata,
									   plot_type=plot_type,
									   amount=amount)
	await ctx.message.delete()
	await ctx.send(file=discord.File(plot_filename))

@bot.command()
async def freq(ctx, plot_type:str="all", amount:int=0):
	""" Generates plots from already counted data.
	Plots uses/day for each emoji, in the counted interval.
	Plot types are "top x", "bottom x", and "all".
	"""
	logger.info("%s command received", ctx.command)
	logger.verbose("User: %s, Args: %s", ctx.author, ctx.args)
	count_data = DATA_REPO[ctx.guild.id]['data']
	count_metadata = DATA_REPO[ctx.guild.id]['metadata']
	age_info = {emo.name : emo.created_at for emo in ctx.guild.emojis}
	plot_filename = freq_plotter.plot(count_data=count_data,
									  count_metadata=count_metadata,
									  plot_type=plot_type,
									  amount=amount,
									  age_info=age_info)
	await ctx.message.delete()
	await ctx.send(file=discord.File(plot_filename))

@bot.command()
async def history(ctx, *args: discord.emoji.Emoji):
	""" Generates plots from already counted data.
	Produces time series plots of the suppliied emoji(s).
	"""
	logger.info("%s command received", ctx.command)
	logger.verbose("User: %s, Args: %s", ctx.author, ctx.args)
	count_data = DATA_REPO[ctx.guild.id]['data']
	count_metadata = DATA_REPO[ctx.guild.id]['metadata']
	plot_filename = time_plotter.plot(count_data=count_data,
									  count_metadata=count_metadata,
									  server_emojis=ctx.guild.emojis,
									  emoji=args)
	await ctx.message.delete()
	await ctx.send(file=discord.File(plot_filename))

### Run that bot! ###

bot.run(TOKEN)
