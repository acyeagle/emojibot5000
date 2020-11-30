
"""
Classes describing the plotting commands.
Individual, specifc commands are defined elsewhere.

	PltCmd
	  |
	  |- BarGraphCmd
	  |
	  |- TimeSeriesCmd
"""

import logging

from discord.ext.commands import BadArgument
import matplotlib.pyplot as plt
from humanize import naturaltime
import pandas as pd

logger = logging.getLogger(__name__)

class PlotCmd(object):

	"""
	def _arg_validator(*args):
		pass

	def _prep_data(*args):
		pass

	def _config_plotting_options(*args):
		pass

	def _make_plot(*args):
		pass
	"""

	def plot(self, count_data, count_metadata, **kwargs):
		""" Main workhorse. Calls the other functions to produce plot.
		"""
		kwargs = self._arg_validator(count_data, **kwargs)
		data = count_data.copy()
		data = self._prep_data(data, **kwargs)

		plotting_kwargs = self._config_plot_options(**kwargs)
		count_info = ' '.join([f"\nSample size: {count_metadata['msg_sample_size']} messages.",
							   f" Data taken: {naturaltime(count_metadata['timestamp'])}"])
		plotting_kwargs['title'] += count_info
		plot_filename = self._make_plot(data, **plotting_kwargs)
		return plot_filename

class BarGraphCmd(PlotCmd):

	@staticmethod
	def _arg_validator(count_data, plot_type, amount, **kwargs):
		""" Checks the plotting command arguments for type and such.
		"""
		plot_type = plot_type.lower()
		if plot_type == 'all':
			amount = len(pd.unique(count_data['name']))
		elif plot_type == 'top' or plot_type == 'bottom':
			if amount > len(count_data) or amount<=0:
				raise BadArgument("Not a valid plot range!")
		else:
			raise BadArgument("Not a valid plot type! (all, top, or bottom)")
		kwargs['plot_type'] = plot_type
		kwargs['amount'] = amount
		return kwargs

	@staticmethod
	def _make_plot(data, title, y_label, color):
		""" The function that does the actual MATPLOTLIB stuff.
		"""
		FILENAME = "some_hardcoded_filename_for_now.png"
		data.plot(kind='bar', color=color)
		plt.ylabel(y_label)
		plt.xlabel(None)
		plt.title(title)
		plt.tight_layout()
		plt.savefig(FILENAME)
		plt.close()
		return FILENAME

class TimeSeriesCmd(PlotCmd):

	@staticmethod
	def _arg_validator(count_data, **kwargs):
		""" Checks the plotting command arguments for type and such.
		"""
		if kwargs['emoji'] not in kwargs['server_emojis']:
			raise BadArgument("Must be a custom emoji")
		return kwargs

	@staticmethod
	def _make_plot(data, title, y_label, color):
		""" The function that does the actual MATPLOTLIB stuff.
		"""
		FILENAME = "some_hardcoded_filename_for_now.png"
		data.plot(color=color)
		plt.ylabel(y_label)
		plt.xlabel(None)
		plt.title(title)
		plt.savefig(FILENAME)
		plt.close()
		return FILENAME
