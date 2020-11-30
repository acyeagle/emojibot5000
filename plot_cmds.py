
from datetime import datetime

import pandas as pd

from plotting import BarGraphCmd, TimeSeriesCmd

class CountPlot(BarGraphCmd):

	@staticmethod
	def _prep_data(data, plot_type, amount, **kwargs):
		""" Extracts the needed data from the DataFrame.
		"""
		data = data.groupby('name')
		data = data['count'].sum().sort_values()
		if plot_type == 'top':
			data = data[::-1]
		return data[:amount]

	@staticmethod
	def _config_plot_options(plot_type, amount, **kwargs):
		plotting_kwargs = {
			'color' : "tab:blue",
			'y_label' : "Use count (#)",
			'title' : f"{plot_type.capitalize()} {amount} emoji count."
		}
		return plotting_kwargs

class FreqPlot(BarGraphCmd):

	@staticmethod
	def _prep_data(data, plot_type, amount, age_info):
		data = data.groupby('name')['count'].sum()
		frequencies = pd.Series(index=data.index)
		for name, count in data.iteritems():
			elapsed = (datetime.utcnow() - age_info[name]).total_seconds()
			frequencies[name] = count/elapsed * 86400
		frequencies = frequencies.sort_values()
		if plot_type == 'top':
			frequencies = frequencies[::-1]
		return frequencies[:amount]

	@staticmethod
	def _config_plot_options(plot_type, amount, **kwargs):
		plotting_kwargs = {
			'color' : "tab:orange",
			'y_label' : "Lifetime average use frequency (#/day)",
			'title' : f"{plot_type.capitalize()} {amount} emoji frequency."
		}
		return plotting_kwargs

class TimePlot(TimeSeriesCmd):

	@staticmethod
	def _prep_data(data, emoji, **kwargs):
		data = data.loc[data['name'] == emoji.name]
		data = data.sort_values(by='time', ignore_index=True)
		final = data['count'].cumsum()
		final.index = data['time']
		return final

	@staticmethod
	def _config_plot_options(emoji, **kwargs):
		plotting_kwargs = {
			'color' : "tab:blue",
			'y_label' : "Count (#)",
			'title' : f"{emoji.name} count history."
		}
		return plotting_kwargs
