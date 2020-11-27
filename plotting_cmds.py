
from datetime import datetime
import logging

from discord.ext.commands import BadArgument
import matplotlib.pyplot as plt
from humanize import naturaltime

logger = logging.getLogger(__name__)

class PltCmd(object):
    
    @staticmethod
    def _arg_validator(count_data, plot_type, amount):
        """ Checks the plotting command arguments for type and such.
        """
        plot_type = plot_type.lower()
        if plot_type == 'all':
            amount=len(count_data.data)
        elif plot_type == 'top' or plot_type == 'bottom':
            if amount > len(count_data.data) or amount<=0:
                raise BadArgument("Not a valid plot range!")
        else:
            raise BadArgument("Not a valid plot type! (all, top, or bottom)")
        return plot_type, amount
        
    @staticmethod
    def _make_plot(x_data, y_data, title, y_label, color):
        """ The function that does the actual MATPLOTLIB stuff.
        """
        FILENAME = "some_hardcoded_filename_for_now.png"
        plt.bar(x_data, y_data, color=color)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(FILENAME)
        plt.close()
        return FILENAME
        
    @staticmethod
    def _prep_data(count_data, plot_type, amount):
        """ Method preparing the x and y data.
        TO BE FILLED IN BY SUBCLASSES.
        """
        pass
     
    @staticmethod
    def _config_plot_options(plot_type, amount):
        """ Method preparing all of the other plotting options.
        TO BE FILLED IN BY SUBCLASSES.
        """
        pass
        
    def plot(self, count_data, plot_type, amount):
        """ Main workhorse. Calls the other functions to produce plot.
        """
        plot_type, amount = self._arg_validator(count_data, plot_type, amount)
        x_data, y_data = self._prep_data(count_data, plot_type, amount)
        plotting_kwargs = self._config_plot_options(plot_type, amount)
        count_info = ' '.join([f"\nEmoji count: {count_data.sample_size} messages.",
                               f" Data taken: {naturaltime(count_data.timestamp)}"])
        plotting_kwargs['title'] += count_info
        plot_filename = self._make_plot(x_data, y_data, **plotting_kwargs)
        return plot_filename
     
class CountPlot(PltCmd):

    @staticmethod
    def _prep_data(count_data, plot_type, amount):
        data = sorted(count_data.data.items(), key=lambda x: x[1], reverse=True)
        if plot_type == 'bottom':
            data.reverse()
        x_data = [x.name for x, _ in data[0:amount]]
        y_data = [y for _, y in data[0:amount]]
        logger.debug("x_data:", x_data)
        logger.debug("y_data:", y_data)
        return x_data, y_data
        
    @staticmethod
    def _config_plot_options(plot_type, amount):
        plotting_kwargs = {
            'color' : "tab:blue",
            'y_label' : "Use count (#)",
            'title' : f"{plot_type.capitalize()} {amount} emoji count."
        }
        return plotting_kwargs
          
class FreqPlot(PltCmd):

    @staticmethod
    def _prep_data(count_data, plot_type, amount):
        # Calculate the frequencies
        frequencies = {}
        for emote, count in count_data.data.items():
            elapsed = (datetime.utcnow() - emote.created_at).total_seconds()
            if elapsed == 0 or elapsed < 86400: #86400 s/day. 1 day min to prevent scale blowout.
                pass
            else:
                frequencies[emote] = (count/elapsed)*1000000
        # Sort n' slice
        data = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)	
        if plot_type == 'bottom':
            data.reverse()
        x_data = [x.name for x, _ in data[0:amount]]
        y_data = [y for _, y in data[0:amount]]
        logger.debug("x_data:", x_data)
        logger.debug("y_data:", y_data)
        return x_data, y_data
      
    @staticmethod
    def _config_plot_options(plot_type, amount):
        plotting_kwargs = {
            'color' : "tab:orange",
            'y_label' : "Lifetime average use frequency (μHz)",
            'title' : f"{plot_type.capitalize()} {amount} emoji frequency."
        }
        return plotting_kwargs
