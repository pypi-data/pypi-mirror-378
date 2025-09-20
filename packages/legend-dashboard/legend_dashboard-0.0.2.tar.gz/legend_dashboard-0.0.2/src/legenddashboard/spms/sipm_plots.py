from __future__ import annotations

import colorcet as cc
import numpy as np
import pandas as pd
from bokeh.models import DatetimeTickFormatter, ZoomInTool, ZoomOutTool
from bokeh.plotting import figure


def sipm_plot_vsTime(
    data_barrel, barrel, resample_unit, name_dict, run, period, run_dict
):
    # add two hours to the x values with if condition
    if data_barrel.index[0].utcoffset() != pd.Timedelta(hours=2):
        data_barrel.index += pd.Timedelta(hours=2)

    p = figure(
        width=1000,
        height=600,
        x_axis_type="datetime",
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | SiPM | Light Intensity | {barrel}"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.hover.formatters = {"$x": "datetime", "$y": "printf"}
    p.hover.tooltips = [
        ("Time", "$x{%F %H:%M:%S CET}"),
        ("Light Intensity Rate (PE/s)", "$y"),
        ("Channel", "$name"),
    ]

    p.hover.mode = "vline"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(data_barrel.columns)
    colours = cc.palette["glasbey_category10"][:len_colours]

    if resample_unit == "1min":
        for i, col in enumerate(data_barrel):
            p.line(
                "time",
                col,
                source=data_barrel,
                color=colours[i],
                line_width=2.5,
                legend_label=name_dict[int(col[2:])],
                name=col,
            )
    else:
        data_barrel_resampled = data_barrel.resample(
            resample_unit, origin="start"
        ).mean()
        for i, col in enumerate(data_barrel_resampled):
            p.line(
                "time",
                col,
                source=data_barrel_resampled,
                color=colours[i],
                line_width=2.5,
                legend_label=name_dict[int(col[2:])],
                name=col,
            )

    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = (
        f"Time (CET), starting: {data_barrel.index[0].strftime('%d/%m/%Y %H:%M:%S')}"
    )
    p.xaxis.axis_label_text_font_size = "20px"
    p.xaxis.formatter = DatetimeTickFormatter(days="%Y/%m/%d")
    p.yaxis.axis_label = "Light Intensity Rate (PE/s)"
    p.yaxis.axis_label_text_font_size = "20px"

    return p


def sipm_plot_histogram(
    data_barrel, barrel, resample_unit, name_dict, run, period, run_dict
):
    p = figure(
        width=1000,
        height=600,
        y_axis_type="log",
        x_range=(0, 3),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | SiPM | Light Intensity | {barrel}"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.hover.tooltips = [
        ("Light Intensity Rate (PE/s)", "$x"),
        ("Counts", "$y"),
        ("Channel", "$name"),
    ]

    p.hover.mode = "vline"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(data_barrel.columns)
    colours = cc.palette["glasbey_category10"][:len_colours]

    for i, col in enumerate(data_barrel):
        data_channel = data_barrel[col]
        counts_ch, bins_ch = np.histogram(
            data_channel, bins=300, range=(data_channel.min(), 3)
        )
        bins_ch = (bins_ch[:-1] + bins_ch[1:]) / 2
        p.line(
            bins_ch,
            counts_ch,
            color=colours[i],
            line_width=2.5,
            legend_label=name_dict[int(col[2:])],
            name=col,
        )

    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Light Intensity Rate (PE/s)"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Counts"
    p.yaxis.axis_label_text_font_size = "20px"

    return p
