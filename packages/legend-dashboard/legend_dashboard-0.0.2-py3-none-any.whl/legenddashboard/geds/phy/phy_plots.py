from __future__ import annotations

import numpy as np
import pandas as pd
from bokeh.models import (
    DatetimeTickFormatter,
    LinearAxis,
    Range1d,
    ZoomInTool,
    ZoomOutTool,
)
from bokeh.palettes import Category20, Turbo256
from bokeh.plotting import figure
from seaborn import color_palette

# physics plots
phy_plots_types_dict = {
    "Pulser Events": "IsPulser",
    "Baseline Events": "IsBsln",
}
phy_plots_vals_dict = {
    "Baseline FPGA": "Baseline",
    "Baseline Mean": "BlMean",
    "Noise": "BlStd",
    "Gain": "Cuspemax",
    "Cal. Gain": "CuspemaxCtcCal",
    "Gain to Pulser Ratio": "Cuspemax_pulser01anaRatio",
    "Gain to Pulser Diff.": "Cuspemax_pulser01anaDiff",
    "Rate": "EventRate",
    "PSD Classifier": "AoeCustom",
}
phy_resampled_vals = [0, 5, 10, 30, 60]
phy_unit_vals = ["Relative", "Absolute"]
phy_plots_sc_vals_dict = {
    "None": False,
    "DAQ Temp. Left 1": "DaqLeft_Temp1",
    "DAQ Temp. Left 2": "DaqLeft_Temp2",
    "DAQ Temp. Right 1": "DaqRight_Temp1",
    "DAQ Temp. Right 2": "DaqRight_Temp2",
    "RREiT": "RREiT",
    "RRNTe": "RRNTe",
    "RRSTe": "RRSTe",
    "ZUL_T_RR": "ZUL_T_RR",
}


def phy_plot_vsTime(
    data_string,
    data_string_mean,
    plot_info,
    plot_type,
    plot_name,
    resample_unit,
    string,
    run,
    period,
    run_dict,
    channel_map,
    abs_unit,
    data_sc,
    sc_param,
):
    # change column names to detector names
    data_string.columns = [
        "{}_val".format(channel_map[ch]["name"]) for ch in data_string.columns
    ]

    # create plot colours
    len_colours = len(data_string.columns)
    colours = color_palette("hls", len_colours).as_hex()

    # add mean values for hover feature
    data_string_mean.columns = [
        channel_map[ch]["name"] for ch in data_string_mean.columns
    ]
    for col in data_string_mean.columns:
        data_string[col] = data_string_mean[col][0]

    # add two hours to x values with if condition
    if data_string.index[0].utcoffset() != pd.Timedelta(
        hours=2
    ):  # only add timedelta if still in UTC
        data_string.index += pd.Timedelta(hours=2)

    p = figure(
        width=1000,
        height=600,
        x_axis_type="datetime",
        tools="pan,box_zoom,ywheel_zoom,hover,reset,save",
        output_backend="webgl",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Phy. {plot_type} | {plot_name} | {string}"
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.hover.formatters = {"$x": "datetime", "$snap_y": "printf", "@$name": "printf"}
    p.hover.tooltips = [
        (
            "Time",
            "$x{%F %H:%M:%S CET}",
        ),  # Use the formatted CET time from the DataFrame
        (f"{plot_info.loc['label'][0]} ({plot_info.loc['unit'][0]})", "$snap_y{%0.2f}"),
        (f"Mean {plot_info.loc['label'][0]} ({abs_unit})", "@$name{0.2f}"),
        ("Detector", "$name"),
    ]
    p.hover.mode = "vline"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    # plot data
    hover_renderers = []
    if resample_unit == "0min":
        for i, det in enumerate(data_string_mean):
            if "mean" in det:
                continue
            line = p.line(
                "datetime",
                f"{det}_val",
                source=data_string,
                color=colours[i],
                legend_label=det,
                name=det,
                line_width=2.5,
            )
            hover_renderers.append(line)
    else:
        data_string_resampled = data_string.resample(
            resample_unit, origin="start"
        ).mean()

        for i, det in enumerate(data_string_mean):
            if "mean" in det:
                continue
            line = p.line(
                "datetime",
                f"{det}_val",
                source=data_string_resampled,
                color=colours[i],
                legend_label=det,
                name=det,
                line_width=2.5,
            )
            p.line(
                "datetime",
                f"{det}_val",
                source=data_string,
                color=colours[i],
                legend_label=det,
                name=det,
                line_width=2.5,
                alpha=0.2,
            )
            hover_renderers.append(line)

    # draw horizontal line at thresholds from plot info if available
    #     if plot_info.loc["lower_lim_var"][0] != 'None' and plot_info.loc["unit"][0] == "%":
    #         lower_lim_var = Slope(gradient=0, y_intercept=float(plot_info.loc["lower_lim_var"][0]),
    #                 line_color='black', line_dash='dashed', line_width=4)
    #         upper_lim_var = Slope(gradient=0, y_intercept=float(plot_info.loc["upper_lim_var"][0]),
    #                 line_color='black', line_dash='dashed', line_width=4)

    #         p.add_layout(lower_lim_var)
    #         p.add_layout(upper_lim_var)

    # legend setups etc...
    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = f"Time (CET), starting: {data_string.index[0].strftime('%d/%m/%Y %H:%M:%S')}"  # change of string
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = f"{plot_info.loc['label'][0]} [{plot_info.loc['unit'][0]}]"
    p.yaxis.axis_label_text_font_size = "20px"
    p.xaxis.formatter = DatetimeTickFormatter(days="%Y/%m/%d")
    p.hover.renderers = hover_renderers

    if plot_info.loc["unit"][0] == "%":
        if plot_info.loc["label"][0] == "Noise":
            p.y_range = Range1d(-150, 150)
        elif (
            plot_info.loc["label"][0] == "FPGA baseline"
            or plot_info.loc["label"][0] == "Mean Baseline"
        ):
            p.y_range = Range1d(-10, 10)
        elif plot_info.loc["label"][0] == "Gain to Pulser Difference":
            p.y_range = Range1d(-4, 4)
        elif plot_info.loc["label"][0] == "Event Rate":
            p.y_range = Range1d(-150, 50)
        elif plot_info.loc["label"][0] == "Custom A/E (A_max / cuspEmax)":
            p.y_range = Range1d(-10, 10)
        else:
            p.y_range = Range1d(-1, 1)
    elif plot_info.loc["label"][0] == "Noise":
        p.y_range = Range1d(-150, 150)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # SLOW CONTROL DATA
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if not data_sc.empty:
        y_column2_range = f"{sc_param}_range"
        y_min = float(data_sc.copy()["value"].min()) * (1 - 0.01)
        y_max = float(data_sc.copy()["value"].max()) * (1 + 0.01)
        p.extra_y_ranges = {y_column2_range: Range1d(start=y_min, end=y_max)}

        unit = data_sc["unit"][0]
        p.add_layout(
            LinearAxis(
                y_range_name=y_column2_range,
                axis_label=f"{sc_param} [{unit}]",
                axis_label_text_font_size="20px",
            ),
            "right",
        )

        time = data_sc["tstamp"]
        time = pd.to_datetime(time, origin="unix", utc=True)
        values = data_sc["value"]
        values = pd.to_numeric(values)
        values.index = time

        # we use the same resampling of geds data
        # (use black line to distinguish from geds data)
        if resample_unit == "0min":
            p.line(
                time,
                values,
                legend_label=sc_param,
                y_range_name=y_column2_range,
                color="black",
                line_width=2,
            )
        else:
            binned_data = values.resample(resample_unit).mean()
            p.line(
                time,
                values,
                color="black",
                legend_label=sc_param,
                y_range_name=y_column2_range,
                line_width=2,
                alpha=0.2,
            )
            p.line(
                binned_data.index,
                binned_data.values,
                color="black",
                legend_label=sc_param,
                y_range_name=y_column2_range,
                line_width=2,
            )

    return p


def phy_plot_histogram(
    data_string,
    plot_info,
    plot_type,
    resample_unit,
    string,
    run,
    period,
    run_dict,
    channels,
    channel_map,
):
    p = figure(
        width=1000,
        height=600,
        x_axis_type="datetime",
        tools="pan,box_zoom,ywheel_zoom,hover,reset,save",
        output_backend="webgl",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Phy. {plot_type} | {plot_info.loc['label'][0]} | {string}"
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.hover.formatters = {"$x": "printf", "$snap_y": "printf"}
    p.hover.tooltips = [
        (f"{plot_info.loc['label'][0]} ({plot_info.loc['unit'][0]}", "$x{%0.2f}"),
        ("Counts", "$snap_y"),
        ("Detector", "$name"),
    ]

    p.hover.mode = "vline"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(data_string.columns)
    colours = Turbo256[len_colours] if len_colours > 19 else Category20[len_colours]

    for position, data_channel in data_string.groupby("position"):
        # generate histogram
        # needed for cuspEmax because with geant outliers not possible to view normal histo
        hrange = {"keV": [0, 2500]}
        # take full range if not specified
        x_min = (
            hrange[plot_info["unit"]][0]
            if plot_info["unit"] in hrange
            else data_channel[plot_info["parameter"]].min()
        )
        x_max = (
            hrange[plot_info["unit"]][1]
            if plot_info["unit"] in hrange
            else data_channel[plot_info["parameter"]].max()
        )

        # --- bin width
        # bwidth = {"keV": 2.5}  # what to do with binning???
        # bin_width = bwidth[plot_info["unit"]] if plot_info["unit"] in bwidth else None
        # no_bins = int((x_max - x_min) / bin_width) if bin_width else 50
        # counts_ch, bins_ch = np.histogram(data_channel[plot_info["parameter"]], bins=no_bins, range=(x_min, x_max))
        # bins_ch = (bins_ch[:-1] + bins_ch[1:]) / 2

        # --- bin width
        bwidth = {"keV": 2.5}
        bin_width = bwidth.get(plot_info["unit"], 1)

        # Compute number of bins
        if bin_width:
            bin_no = (
                bin_width / 5 if "AoE" not in plot_info["parameter"] else bin_width / 50
            )
            bin_no = bin_no / 2 if "Corrected" in plot_info["parameter"] else bin_no
            bin_no = bin_width if "AoE" not in plot_info["parameter"] else bin_no

            bin_edges = (
                np.arange(x_min, x_max + bin_width, bin_no)
                if plot_info["unit_label"] == "%"
                else np.arange(x_min, x_max + bin_width, bin_no)
            )
        else:
            bin_edges = 50
        counts_ch, bins_ch = np.histogram(
            data_channel[plot_info["parameter"]], bins=bin_edges, range=(x_min, x_max)
        )
        bins_ch = (bins_ch[:-1] + bins_ch[1:]) / 2
        # create plot histo
        histo_df = pd.DataFrame(
            {
                "counts": counts_ch,
                "bins": bins_ch,
                "position": position,
                "cc4_id": data_channel["cc4_id"].unique()[0],
            }
        )
        # plot
        p.line(
            "bins",
            "counts",
            source=histo_df,
            color=colours[position - 1],
            legend_label=f"{data_channel['name'].unique()[0]}",
            name=f"ch {data_channel['channel'].unique()[0]}",
            line_width=2,
        )

    p.legend.location = "bottom_left"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = f"{plot_info['label']} [{plot_info['unit_label']}]"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Counts"
    p.yaxis.axis_label_text_font_size = "20px"

    return p
