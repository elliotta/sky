# vim: set fileencoding=utf-8> :

'''
This is a little library function designed for quick plotting of time sequences.
'''

# Note that ephem DOES NOT DO TIMEZONES!!!
# Nor does datetime.datetime.now include a timezone
# It is much safer to use utcnow and convert later

import datetime
import calendar

import matplotlib.pyplot as plt
import pylab
import matplotlib.dates
import matplotlib.ticker
import matplotlib.gridspec as gs
import matplotlib.dates


def make_plot(start_time, end_time, interval, function_dict_list, title=None, x_label='Time', y_label=None, localtime=True, out_file=None):
    '''Make a time plot from a dictionary.

    start_time and end_time should be datetime objects in UTC
    interval should be a datetime.timedelta object
    function_dict_list must be a list (or tuple, etc) of dictionaries
        each dictionary must contain:
            'function': a function that accepts a datetime object as arguement
        each dictionary may contain
            'name': text to display on the plot
            'color': what color to display as
    title is a string to display for the function's title
    x_lable and y_label are strings for labeling the axies
    if localtime is true, display timestamps in localtime on plot
    if out_file, write plot to file. Else show on screen
    '''

    utc_timestamps = []
    date = start_time
    while date < end_time:
        utc_timestamps.append(date)
        date = date + interval

    # Make the data
    if localtime:
        local_timestamps = []
    plot_data_lists = []
    for f in function_dict_list:
        plot_data_lists.append([])
    for t in utc_timestamps:
        for i, f in enumerate(function_dict_list):
            plot_data_lists[i].append(f['function'](t))
        if localtime:
            # Yeah, I know this is convoluted
            # Probably ought to use one of the timezone libraries
            # But at least this ought to handle local DST changes
            local_timestamps.append(datetime.datetime.fromtimestamp(calendar.timegm(t.timetuple())))

    # Plot the data
    fig = plt.figure()
    ax1 = fig.add_subplot(111) # rows, columns, n-plot
    if localtime:
        plot_timestamps = local_timestamps
    else:
        plot_timestamps = utc_timestamps

    for i, f in enumerate(function_dict_list):
        if 'name' in f and 'color' in f:
            ax1.plot(plot_timestamps, plot_data_lists[i], c=f['color'], label=f['name'])
        elif 'name' in f:
            ax1.plot(plot_timestamps, plot_data_lists[i], label=f['name'])
        elif 'color' in f:
            ax1.plot(plot_timestamps, plot_data_lists[i], c=f['color'])
        else:
            ax1.plot(plot_timestamps, plot_data_lists[i])

    # Configure time axis sensibly
    #time_covered = end_time - start_time
    #if time_covered < datetime.timedelta(days=5):
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M\n%m/%d'))
    #if time_covered < datetime.timedelta(days=10):
    #    ax1.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%H:%M'))

    # Add optional lables
    if title:
        ax1.set_title(title)
    if y_label:
        ax1.set_ylabel(y_label)
    if x_label:
        ax1.set_xlabel(x_label)

    if len(f) > 1:
        ax1.legend()

    # Output the plot
    plt.tight_layout()
    if out_file:
        pylab.savefig(args.out_file)
    else:
        plt.show()
