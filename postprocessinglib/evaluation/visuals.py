"""
The visual module contains different plotting functions for time series visualization.
It allows users to plot hydrographs per station for each stations to allow us visualize
the time-series data

Some of them also allow the addition of metruics to be placed beside the plots

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import postprocessinglib.evaluation.metrics as metr

# path = "MESH_output_streamflow.csv"
# df = pd.read_csv(path, skipinitialspace = True)
# df.drop(columns=df.columns[-1], inplace = True)
# predicted = df.iloc[:, [1, 3, 5]]
# actual = df.iloc[:, [1, 2, 4]]
# station_1 = df.iloc[:, [1, 2, 3]]

def plot(dataframe: pd.DataFrame, legend: tuple[str, str] = ('Simulated Data', 'Observed Data'), 
         metrics: list[str] = None, num_min: int = 0, grid: bool = False, title: str = None, 
         labels: tuple[str, str] = None, linestyles: tuple[str, str] = ('r-', 'b-'), padding: bool = False ,
         fig_size: tuple[float, float] = (10,6), metrics_adjust: tuple[float, float] = (-0.35, 0.75),
         plot_adjust: float = 0.15):
    """ Create a compsriosn time series line plot of simulated and observed time series data

    Parameters
    ----------
    dataframe : pd.DataFrame
        the dataframe containing the series of observed and simulated values

     legend: tuple[str, str]
        Adds a Legend in the 'best' location determined by matplotlib.

    metrics: list[str]
        Adds Metrics to the left side of the plot. Any metric from the postprocessing.metrics library
        can be added to the plot as the abbreviation of the function. The entries must be in a list.
        (e.g. ['PBIAS', 'MSE', 'KGE']).

    num_min: int 
        number of days required to "warm up" the system. Its only important when wanting to display
        the metrics on the plot 

    grid: bool
        If True, adds a grid to the plot.

    title: str
        If given, adds a title to the plot.

    labels: tuple[str, str]
        List of two str type inputs specifying x-axis labels and y-axis labels, respectively.

    linestyles: tuple[str, str]
        List of two string type inputs thet will change the linestyle of the simulated and
        recorded data, respectively.

    padding: bool
        If true, will set the padding to zero for the lines in the line plot.

    fig_size: tuple[float, float]
        Tuple of length two that specifies the horizontal and vertical lengths of the plot in
        inches, respectively.

    metrics_adjust: tuple[float, float]
        Tuple of length two with float type inputs indicating the relative position of the text
        (x-coordinate, y-coordinate) when adding metrics to the plot.

    plot_adjust: float
        Specifies the relative position to shift the plot the the right when adding metrics to the
        plot.

    Returns
    -------
    fig : Matplotlib figure instance
        A matplotlib figure handle is returned, which can be viewed with the matplotlib.pyplot.show() command.
         
    """
    fig = plt.figure(figsize=fig_size, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    # Setting Variable for the simulated data, observed data, and time stamps
    obs = dataframe.iloc[:, 1].values
    sim = dataframe.iloc[:, 2].values
    time = dataframe.index.values

    # Plotting the Data
    plt.plot(time, obs, linestyles[1], label=legend[1], linewidth = 1.25)
    plt.plot(time, sim, linestyles[0], label=legend[0], linewidth = 0.5)
    plt.legend(fontsize=10)

    # Adjusting the plot if user wants tight x axis limits
    if padding:
        plt.xlim(time[0], time[-1])

    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)

    # Placing Labels if requested
    if labels:
        # Plotting Labels
        plt.xlabel(labels[0], fontsize=14)
        plt.ylabel(labels[1], fontsize=14)
    if title:
        title_dict = {'family': 'sans-serif',
                      'color': 'black',
                      'weight': 'normal',
                      'size': 18,
                      }
        ax.set_title(label=title, fontdict=title_dict, pad=25)

    # Placing a grid if requested
    if grid:
        plt.grid(True)

    # Fixes issues with parts of plot being cut off
    plt.tight_layout()

    # Placing Metrics on the Plot if requested
    if metrics:

        obs_metric = dataframe.iloc[:, [0, 1]]
        sim_metric = dataframe.iloc[:, [0, 2]]


        formatted_selected_metrics = 'Metrics for this station: \n'
        if metrics == 'all':
            for key, value in metr.calculate_all_metrics(observed=obs_metric, simulated=sim_metric, 
                                                         num_stations=1, num_min=num_min).items():
                formatted_selected_metrics += key + ' : ' + str(value[0]) + '\n'
        else: 
            assert isinstance(metrics, list)
            for metric in metrics:
                assert metric.upper() in metr.available_metrics
            for key, value in metr.calculate_metrics(observed=obs_metric, simulated=sim_metric, metrices=metrics,
                                   num_stations=1, num_min=num_min).items():
                formatted_selected_metrics += key + ' : ' + str(value[0]) + '\n'

        font = {'family': 'sans-serif',
                'weight': 'normal',
                'size': 12}
        plt.text(metrics_adjust[0], metrics_adjust[1], formatted_selected_metrics, ha='left', va='center',
                 transform=ax.transAxes, fontdict=font)

        plt.subplots_adjust(left=plot_adjust)

    return fig

def histogram():
    return

def scatter():
    return

# plot(dataframe=station_1, 
#      title='Hydrograph of Entire Time Series of Station 1',
#      linestyles=['r-', 'k-'],
#      labels=['Datetime', 'Streamflow'],
#     #  metrics=['RMSE', 'NSE', 'KGE'],
#      # metrics = 'all',
#      plot_adjust = 0.15,
#      grid=True)
# plt.show()