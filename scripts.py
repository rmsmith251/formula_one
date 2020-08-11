from matplotlib import pyplot as plt
import numpy as np
from matplotlib import ticker
import pandas as pd
import seaborn as sns
import sqlite3


def db_pull(sql):
    """
    :param sql: SQL statement for desired data
    :return: DataFrame of desired data
    """
    conn = None
    try:
        conn = sqlite3.connect('f1.db')
        cur = conn.cursor()
        data = pd.read_sql_query(sql, conn)
        cur.close()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return data


def heatmap(data, row_labels, col_labels, ax=None, cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.
    Copied from matplotlib heatmap documentation.
    https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """
    if not ax:
        ax = plt.gca()

    # plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a 'Text' for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def ridge_plot(x, g, title, style="white", label_x_adj=0, label_y_adj=.3):
    """
    A ridge plot is a series of distributions of inputted data.

    :param x: Numpy array of values to be used on the y axis (i.e. Years)
    :param g: Numpy array of values to be used for generating the curves (i.e. Lap Time)
    :param style: Optional string to change the style of the plot (default is white)
    :param title: Optional string to set the title of the chart (default is blank)
    :return: Ridge plot of given arrays
    """

    sns.set(style=style, rc={"axes.facecolor": (0, 0, 0, 0)})
    length = len(x.unique())

    df = pd.DataFrame(dict(x=x, y=g))

    pal = sns.cubehelix_palette(length, rot=-.25, light=.7)
    g = sns.FacetGrid(df, row="x", hue="x", aspect=20, height=0.75, palette=pal)

    g.map(sns.kdeplot, "y", clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
    g.map(sns.kdeplot, "y", clip_on=False, color="w", lw=2, bw=.2)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)

    def label(x, color, label):
        ax = plt.gca()
        ax.text(label_x_adj, label_y_adj, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, x="x")

    g.fig.subplots_adjust(hspace=-.25)

    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)
    plt.suptitle(title)

    plt.get_current_fig_manager().window.state('zoomed')

    plt.show()


def bar(x_data, y_data, title="", x_label="", y_label=""):
    """
    :param x_data: Array of data for the x axis
    :param y_data: Array of data for the bars/y axis
    :param title: Optional string to set the title of the chart (default is blank)
    :param x_label: Optional string to set the x axis label (default is blank)
    :param y_label: Optional string to set the y axis label (default is blank)
    :return: Bar chart of x_data and y_data
    """
    fig, ax = plt.subplots(constrained_layout=True)
    plt.title(title)
    rectangles = ax.bar(x_data, y_data)
    plt.xticks(rotation=45, ha="right")
    ax.set_ylabel(ylabel=y_label)
    ax.set_xlabel(xlabel=x_label)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rectangles)

    plt.get_current_fig_manager().window.state('zoomed')

    plt.show()


def pie(data, labels):

    fig, ax = plt.subplots(constrained_layout=True)
    plt.title("")
    ax.pie(data, labels=labels, autopct='%1.1f%%',
           shadow=False, startangle=90)
    ax.axis('equal')

    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()


def nested_pie(data_outer, data_inner, labels_outer=None, labels_inner=None,
               inner_label_distance=0.7, rotate_inner_labels=40, title=""):
    """
    Important: Be sure that both arrays are sorted in the same manner\n
    (i.e. outer = [3, 4, 5, 6] and inner = [1, 2, 2, 2, 1, 4, 2, 3, 1] where:
    outer[0] = inner[0:2],\n
    outer[1] = inner[2:4],\n
    outer[2] = inner[4:6],\n
    outer[3] = inner[6:], etc)\n
    :param data_outer: Array of data to be displayed on outer chart, sorted
    :param data_inner: Array of data to be displayed on inner chart, sorted
    :param labels_outer: Labels to display for outer donut (default is None)
    :param labels_inner: Labels to display for inner donut (default is None)
    :param inner_label_distance: Moves the labels in case of a clash (default is 0.7)
    :param rotate_inner_labels: Rotates the labels if desired (default is 40)
    :param title: Title to display above nested pie chart
    """

    plt.pie(data_outer, labels=labels_outer, autopct='%1.1f%%',
            pctdistance=0.86, startangle=90, frame=True)
    plt.pie(data_inner, labels=labels_inner, labeldistance=inner_label_distance,
            rotatelabels=rotate_inner_labels, radius=0.75, startangle=90)
    center_circle = plt.Circle((0, 0), 0.5, color='black',
                               fc='white', linewidth=0)

    plt.title(title)

    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    plt.tight_layout()
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()


if __name__ == '__main__':
    # app.individual_circuit_lap_times('Michael Schumacher', 'Circuit de Spa-Francorchamps')
    labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    data = [3, 4, 5, 6]
    data2 = [1, 2, 2, 2, 1, 4, 2, 3, 1]
    nested_pie(data, data2)

