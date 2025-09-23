import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.axes import Axes
from typing import Optional


def style(
    ax: Axes,
    x_fmt: Optional[str] = None,
    y_fmt: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    title: Optional[str] = None,
    font_size: int = 10,
    legend: bool = True,
) -> Axes:
    """
    Style a matplotlib axes with proper formatting for different data types.

    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to style
    x_fmt, y_fmt : str, optional
        Format strings: '%' for percentage, '$' for currency, 'mon' for month names, 'date' for year-month
    x_label, y_label : str, optional
        Axis labels
    title : str, optional
        Plot title
    font_size : int, default 10
        Font size for labels and title
    legend : bool, default True
        Whether to show legend

    Returns:
    --------
    matplotlib.axes.Axes
        The styled axes

    Examples:
    ---------
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [0.1, 0.2, 0.3])
    >>> style(ax, y_fmt='%', y_label='Conversion Rate', title='Test')
    """

    # Handle Y-axis formatting
    if y_fmt is not None:
        if y_fmt == "%":
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.0%}"))
        elif y_fmt == "$":
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
        else:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.2f}"))

    if x_fmt is not None:
        if x_fmt == "%":
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.0%}"))
        elif x_fmt == "$":
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
        elif x_fmt == "mon":
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        elif x_fmt == "date":
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%y'%b"))
        else:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x:.2f}"))

    # rotate x-axis labels
    ax.tick_params(axis="x", labelrotation=90)
    # Set labels and title
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=font_size)
    if title is not None:
        ax.set_title(title, fontsize=font_size * 1.5)
    ax.set_ylim(0, ax.get_ylim()[1])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(True, alpha=0.3)
    # Handle legend
    if legend:
        ax.legend(fontsize=font_size, frameon=False)

    fig = ax.get_figure()
    fig.tight_layout()

    return ax
