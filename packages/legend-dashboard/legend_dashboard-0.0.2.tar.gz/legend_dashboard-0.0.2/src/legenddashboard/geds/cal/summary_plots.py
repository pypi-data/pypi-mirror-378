# ruff: noqa: ARG001
from __future__ import annotations

import copy
import logging
from datetime import datetime, timedelta
from pathlib import Path

import bokeh.palettes as pal
import colorcet as cc
import numexpr as ne
import numpy as np
import pandas as pd
from bokeh.models import (
    CustomJSTickFormatter,
    FixedTicker,
    Label,
    Span,
    ZoomInTool,
    ZoomOutTool,
)
from bokeh.plotting import figure
from dbetto import Props
from legendmeta import LegendMetadata

from legenddashboard.geds.string_visulization import create_detector_plot
from legenddashboard.util import sorter

log = logging.getLogger(__name__)


def build_string_array(chan_map):
    dets = []
    strings = []
    positions = []
    for key, entry in chan_map.items():
        if entry.system == "geds":
            string = entry.location.string
            pos = entry.location.position
            dets.append(key)
            strings.append(string)
            positions.append(int(pos))

    return dets, strings, positions


def build_status_map(chan_map, data):
    dets, strings, positions = build_string_array(chan_map)

    string_nos = np.array(sorted(np.unique(strings)))
    pos_nos = np.array(sorted(np.unique(positions)))
    n_strings = len(string_nos)
    max_pos = np.max(positions)

    data_array = np.full((max_pos * 2 + 1, n_strings * 2 + 1), np.nan)
    annot_array = np.empty((max_pos * 2 + 1, n_strings * 2 + 1), dtype="object")

    for i, det in enumerate(dets):
        index = (
            2 * positions[i] - 1,
            2 * (np.where(strings[i] == string_nos)[0] + 1) - 1,
        )
        annot_array[index] = det
        proc_status = None
        use_status = None
        proc_status = data[det]["processable"]
        use_status = data[det]["usability"]
        if proc_status:
            if use_status == "On":
                data_array[index] = 2.0
            else:
                data_array[index] = 1.0
        else:
            data_array[index] = 0.0

    x_axes = np.full(n_strings * 2 + 1, " ", dtype=object)
    for i, s in enumerate(string_nos):
        x_axes[2 * (i + 1) - 1] = f"Str {s}"

    y_axes = np.full(max_pos * 2 + 1, " ", dtype=object)
    for i, n in enumerate(pos_nos):
        y_axes[2 * (i + 1) - 1] = f"Pos {n}"

    return data_array, x_axes, y_axes, annot_array


def plot_status(
    prod_config,
    run,
    run_dict,
    path,
    source,
    xlabels,
    period,
    key=None,
    sort_dets_obj=None,
    cache_data=None,
):
    if sort_dets_obj is not None:
        statuses = sort_dets_obj.statuses.valid_for(run_dict["timestamp"])
        cmap = sort_dets_obj.chmaps.valid_for(run_dict["timestamp"])
    else:
        chmap = LegendMetadata(path=prod_config["paths"]["chan_map"])
        cmap = chmap.channelmap(run_dict["timestamp"])
        status_map = LegendMetadata(
            path=prod_config["paths"]["detector_status"], lazy=True
        ).statuses
        statuses = status_map.on(run_dict["timestamp"])

    dets, strings, positions = build_string_array(cmap)

    color_dict = {"on": 2, "off": 0, "ac": 1}
    display_dict = {i: color_dict[statuses[i]["usability"]] for i in dets}

    # display_dict = {cmap[i]['daq']['rawid'] : 1 if status_map[i]["processable"] == True and status_map[i]["usability"] == 'on' else 0
    #     for i in dets}
    palette = ("red", "orange", "green")
    ctitle = "Detector Status"
    ticker = FixedTicker(ticks=[0.3, 1.0, 1.7], tags=["red", "orange", "green"])
    formatter = CustomJSTickFormatter(
        code="""
        var mapping = {0.3: "off", 1.0: "ac", 1.7: "on"};
        return mapping[tick];
    """
    )
    return create_detector_plot(
        source,
        display_dict,
        xlabels,
        ctitle=ctitle,
        palette=palette,
        ticker=ticker,
        formatter=formatter,
        plot_title=f"{run_dict['experiment']}-{period}-{run} | Cal. | Detector Status",
        boolean_scale=True,
    )


def build_counts_map(chan_map, data):
    dets, strings, positions = build_string_array(chan_map)

    string_nos = np.array(sorted(np.unique(strings)))
    pos_nos = np.array(sorted(np.unique(positions)))
    n_strings = len(string_nos)
    max_pos = np.max(positions)

    data_array = np.full((max_pos * 2 + 1, n_strings * 2 + 1), np.nan)
    annot_array = np.empty((max_pos * 2 + 1, n_strings * 2 + 1), dtype="object")

    for i, det in enumerate(dets):
        index = (
            2 * positions[i] - 1,
            2 * (np.where(strings[i] == string_nos)[0] + 1) - 1,
        )
        annot_array[index] = data[det]
        data_array[index] = data[det]

    x_axes = np.full(n_strings * 2 + 1, " ", dtype=object)
    for i, s in enumerate(string_nos):
        x_axes[2 * (i + 1) - 1] = f"Str {s}"

    y_axes = np.full(max_pos * 2 + 1, " ", dtype=object)
    for i, n in enumerate(pos_nos):
        y_axes[2 * (i + 1) - 1] = f"Pos {n}"

    return data_array, x_axes, y_axes, annot_array


def plot_counts(
    prod_config,
    run,
    run_dict,
    path,
    source,
    xlabels,
    period,
    key=None,
    sort_dets_obj=None,
    cache_data=None,
):  # FEP counts plot
    if sort_dets_obj is not None:
        cmap = sort_dets_obj.chmaps.valid_for(run_dict["timestamp"])
    else:
        chmap = LegendMetadata(path=prod_config["paths"]["metadata"])
        cmap = chmap.channelmap(run_dict["timestamp"])

    if cache_data is not None and run in cache_data["hit"]:
        all_res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )
        all_res = Props.read_from(path)
        cache_data["hit"][run] = all_res

    res = {}
    for det in cmap:
        if cmap[det].system == "geds":
            try:
                fep_counts = all_res[det]["results"]["ecal"]["cuspEmax_ctc_cal"][
                    "total_fep"
                ]
                mass = cmap[det]["production"]["mass_in_g"]
                mass_in_kg = mass * 0.001
                counts_per_kg = fep_counts / mass_in_kg  # calculate counts per kg
                round_counts = round(counts_per_kg, 0)
                res[det] = round_counts
            except KeyError:
                res[det] = 0

    display_dict = res
    ctitle = "FEP Counts per kg"
    palette = pal.plasma(256)  # alternatively use viridis palette = viridis(256)
    return create_detector_plot(
        source,
        display_dict,
        xlabels,
        ctitle=ctitle,
        palette=palette,
        plot_title=f"{run_dict['experiment']}-{period}-{run} | Cal. | FEP Counts per kg",
        colour_max=10000,
        colour_min=1000,
    )


def plot_energy_resolutions(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    at="Qbb",
    download=False,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["hit"]:
        all_res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        all_res = Props.read_from(path)
        cache_data["hit"][run] = all_res

    default = {
        "cuspEmax_ctc_cal": {
            "Qbb_fwhm": np.nan,
            "Qbb_fwhm_err": np.nan,
            "2.6_fwhm": np.nan,
            "2.6_fwhm_err": np.nan,
            "m0": np.nan,
            "m1": np.nan,
        },
        "zacEmax_ctc_cal": {
            "Qbb_fwhm": np.nan,
            "Qbb_fwhm_err": np.nan,
            "2.6_fwhm": np.nan,
            "2.6_fwhm_err": np.nan,
            "m0": np.nan,
            "m1": np.nan,
        },
        "trapEmax_ctc_cal": {
            "Qbb_fwhm": np.nan,
            "Qbb_fwhm_err": np.nan,
            "2.6_fwhm": np.nan,
            "2.6_fwhm_err": np.nan,
            "m0": np.nan,
            "m1": np.nan,
        },
    }
    res = {}
    for stri in strings:
        res[stri] = default
        for channel in strings[stri]:
            detector = channel_map[channel]["name"]
            try:
                det_dict = all_res[detector]["results"]["ecal"]
                res[detector] = {
                    "cuspEmax_ctc_cal": {
                        "Qbb_fwhm": det_dict["cuspEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_in_kev"
                        ],
                        "Qbb_fwhm_err": det_dict["cuspEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_err_in_kev"
                        ],
                        "2.6_fwhm": det_dict["cuspEmax_ctc_cal"]["pk_fits"][2614.511][
                            "fwhm_in_kev"
                        ],
                        "2.6_fwhm_err": det_dict["cuspEmax_ctc_cal"]["pk_fits"][
                            2614.511
                        ]["fwhm_err_in_kev"],
                        "m0": det_dict["cuspEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "a"
                        ],
                        "m1": det_dict["cuspEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "b"
                        ],
                    },
                    "zacEmax_ctc_cal": {
                        "Qbb_fwhm": det_dict["zacEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_in_kev"
                        ],
                        "Qbb_fwhm_err": det_dict["zacEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_err_in_kev"
                        ],
                        "2.6_fwhm": det_dict["zacEmax_ctc_cal"]["pk_fits"][2614.511][
                            "fwhm_in_kev"
                        ],
                        "2.6_fwhm_err": det_dict["zacEmax_ctc_cal"]["pk_fits"][
                            2614.511
                        ]["fwhm_err_in_kev"],
                        "m0": det_dict["zacEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "a"
                        ],
                        "m1": det_dict["zacEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "b"
                        ],
                    },
                    "trapEmax_ctc_cal": {
                        "Qbb_fwhm": det_dict["trapEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_in_kev"
                        ],
                        "Qbb_fwhm_err": det_dict["trapEmax_ctc_cal"]["eres_linear"][
                            "Qbb_fwhm_err_in_kev"
                        ],
                        "2.6_fwhm": det_dict["trapEmax_ctc_cal"]["pk_fits"][2614.511][
                            "fwhm_in_kev"
                        ],
                        "2.6_fwhm_err": det_dict["trapEmax_ctc_cal"]["pk_fits"][
                            2614.511
                        ]["fwhm_err_in_kev"],
                        "m0": det_dict["trapEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "a"
                        ],
                        "m1": det_dict["trapEmax_ctc_cal"]["eres_linear"]["parameters"][
                            "b"
                        ],
                    },
                }
            except KeyError:
                res[detector] = default

    p = figure(
        width=1400,
        height=600,
        y_range=(1, 5),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | {at} Energy Resolution"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(res)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    for filter_type in ["cuspEmax_ctc_cal", "zacEmax_ctc_cal", "trapEmax_ctc_cal"]:
        x_plot, y_plot, y_plot_err = (
            np.arange(1, len(list(res)) + 1, 1),
            [res[det][filter_type][f"{at}_fwhm"] for det in res],
            [res[det][filter_type][f"{at}_fwhm_err"] for det in res],
        )

        err_xs = []
        err_ys = []

        for x, y, yerr in zip(x_plot, y_plot, y_plot_err, strict=False):
            err_xs.append((x, x))
            err_ys.append((np.nan_to_num(y - yerr), np.nan_to_num(y + yerr)))

        df_plot["x_{}".format(filter_type.split("_")[0])] = np.nan_to_num(x_plot)
        df_plot["y_{}".format(filter_type.split("_")[0])] = np.nan_to_num(y_plot)
        df_plot["y_{}_err".format(filter_type.split("_")[0])] = np.nan_to_num(
            y_plot_err
        )
        df_plot["err_xs_{}".format(filter_type.split("_")[0])] = err_xs
        df_plot["err_ys_{}".format(filter_type.split("_")[0])] = err_ys

    if download:
        if at == "Qbb":
            return (
                df_plot,
                f"{run_dict['experiment']}-{period}-{run}_Qbb_energy_resolutions.csv",
            )
        return (
            df_plot,
            f"{run_dict['experiment']}-{period}-{run}_FEP_energy_resolutions.csv",
        )

    for filter_type, filter_name, filter_plot_color in zip(
        ["cuspEmax_ctc_cal", "zacEmax_ctc_cal", "trapEmax_ctc_cal"],
        ["Cusp", "ZAC", "Trap"],
        ["blue", "green", "red"],
        strict=False,
    ):
        if filter_name == "Cusp":
            hover_renderer = p.scatter(
                x="x_{}".format(filter_type.split("_")[0]),
                y="y_{}".format(filter_type.split("_")[0]),
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
                name=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
            )
        else:
            p.scatter(
                x="x_{}".format(filter_type.split("_")[0]),
                y="y_{}".format(filter_type.split("_")[0]),
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
                name=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
            )
        p.multi_line(
            xs="err_xs_{}".format(filter_type.split("_")[0]),
            ys="err_ys_{}".format(filter_type.split("_")[0]),
            source=df_plot,
            color=filter_plot_color,
            legend_label=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
            name=f'{filter_name} Average: {np.nanmean([res[det][filter_type][f"{at}_fwhm"] for det in res]):.2f}keV',
        )

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    if at == "Qbb":
        p.yaxis.axis_label = "FWHM at Qbb (keV)"
    else:
        p.yaxis.axis_label = "FWHM of 2.6 MeV peak (keV)"
        p.title.text = (
            f"{run_dict['experiment']}-{period}-{run} | Cal. | FEP Energy Resolution"
        )
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(res)) + 1, 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(res)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=1.1, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [
        ("Detector", "@label_res"),
        ("FWHM Cusp", "@y_cuspEmax{0.00} +- @y_cuspEmax_err{0.00} keV"),
        ("FWHM ZAC ", "@y_zacEmax{0.00} +- @y_zacEmax_err{0.00} keV"),
        ("FWHM Trap", "@y_trapEmax{0.00} +- @y_trapEmax_err{0.00} keV"),
    ]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def plot_energy_resolutions_Qbb(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    download=False,
    cache_data=None,
):
    return plot_energy_resolutions(
        prod_config,
        run,
        run_dict,
        path,
        period,
        key=key,
        at="Qbb",
        sort_dets_obj=sort_dets_obj,
        download=download,
        cache_data=cache_data,
    )


def plot_energy_resolutions_2614(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    download=False,
    cache_data=None,
):
    return plot_energy_resolutions(
        prod_config,
        run,
        run_dict,
        path,
        period,
        key=key,
        sort_dets_obj=sort_dets_obj,
        at="2.6",
        download=download,
        cache_data=cache_data,
    )


def plot_energy_residuals(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    filter_param="cuspEmax_ctc_cal",
    download=False,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["hit"]:
        all_res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        all_res = Props.read_from(path)
        cache_data["hit"][run] = all_res

    peaks = [2614.511, 583.191, 2103.511]
    filters = ["cuspEmax_ctc_cal", "zacEmax_ctc_cal", "trapEmax_ctc_cal"]

    default_peaks = {f"{peak}": np.nan for peak in peaks}
    default_peaks.update({f"{peak}_err": np.nan for peak in peaks})
    default = {filt: default_peaks.copy() for filt in filters}
    res = {}
    for stri in strings:
        res[stri] = copy.deepcopy(default)
        for channel in strings[stri]:
            detector = channel_map[channel]["name"]
            res[detector] = copy.deepcopy(default)
            try:
                det_dict = all_res[detector]["results"]["ecal"]
                for filt in filters:
                    cal_dict = all_res[detector]["pars"]["operations"][filt]
                    for peak in peaks:
                        # try:
                        cal_mu = ne.evaluate(
                            f"{cal_dict['expression']}",
                            local_dict=dict(
                                {
                                    filt.replace("_cal", ""): det_dict[filt]["pk_fits"][
                                        peak
                                    ]["parameters"]["mu"]
                                },
                                **cal_dict["parameters"],
                            ),
                        )
                        cal_err = (
                            ne.evaluate(
                                f"{cal_dict['expression']}",
                                local_dict=dict(
                                    {
                                        filt.replace("_cal", ""): det_dict[filt][
                                            "pk_fits"
                                        ][peak]["uncertainties"]["mu"]
                                        + det_dict[filt]["pk_fits"][peak]["parameters"][
                                            "mu"
                                        ]
                                    },
                                    **cal_dict["parameters"],
                                ),
                            )
                            - cal_mu
                        )
                        res[detector][filt][f"{peak}"] = cal_mu - peak
                        res[detector][filt][f"{peak}_err"] = cal_err
                        # except KeyError:
                        #     pass
            except KeyError:
                pass

    p = figure(
        width=1400,
        height=600,
        tools="pan,box_zoom,ywheel_zoom,hover,reset,save",
        active_scroll="ywheel_zoom",
    )

    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | Energy Residuals"
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(res)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    for filter_type in filters:
        for peak in peaks:
            x_plot, y_plot, y_plot_err = (
                np.arange(1, len(list(res)) + 1, 1),
                [res[det][filter_type][f"{peak}"] for det in res],
                [res[det][filter_type][f"{peak}_err"] for det in res],
            )

            err_xs = []
            err_ys = []

            for x, y, yerr in zip(x_plot, y_plot, y_plot_err, strict=False):
                err_xs.append((x, x))
                err_ys.append((np.nan_to_num(y - yerr), np.nan_to_num(y + yerr)))

            df_plot[f"x_{filter_type.split('_')[0]}_{int(peak)}"] = np.nan_to_num(
                x_plot
            )
            df_plot[f"y_{filter_type.split('_')[0]}_{int(peak)}"] = np.nan_to_num(
                y_plot
            )
            df_plot[f"y_{filter_type.split('_')[0]}_{int(peak)}_err"] = np.nan_to_num(
                y_plot_err
            )
            df_plot[f"err_xs_{filter_type.split('_')[0]}_{int(peak)}"] = err_xs
            df_plot[f"err_ys_{filter_type.split('_')[0]}_{int(peak)}"] = err_ys

    if download:
        return df_plot, f"{run_dict['experiment']}-{period}-{run}_energy_residuals.csv"

    for peak, peak_color in zip(peaks, ["blue", "green", "red"], strict=False):
        if peak == peaks[0]:
            hover_renderer = p.scatter(
                x=f"x_{filter_type.split('_')[0]}_{int(peak)}",
                y=f"y_{filter_type.split('_')[0]}_{int(peak)}",
                source=df_plot,
                color=peak_color,
                size=7,
                line_alpha=0,
                legend_label=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
                name=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
            )
        else:
            p.scatter(
                x=f"x_{filter_type.split('_')[0]}_{int(peak)}",
                y=f"y_{filter_type.split('_')[0]}_{int(peak)}",
                source=df_plot,
                color=peak_color,
                size=7,
                line_alpha=0,
                legend_label=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
                name=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
            )
        p.multi_line(
            xs=f"err_xs_{filter_type.split('_')[0]}_{int(peak)}",
            ys=f"err_ys_{filter_type.split('_')[0]}_{int(peak)}",
            source=df_plot,
            color=peak_color,
            legend_label=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
            name=f'{peak} Average: {np.nanmean([res[det][filter_param][f"{peak}"] for det in res]):.2f}keV',
        )

    p.legend.location = "bottom_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "peak residuals (keV)"
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | Energy Residuals"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(res)) + 1, 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(res)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=1.1, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [
        ("Detector", "@label_res"),
        (
            "2614",
            f"@y_{filter_type.split('_')[0]}_2614{{0.00}} +- @y_{filter_type.split('_')[0]}_2614_err{{0.00}} keV",
        ),
        (
            "SEP",
            f"@y_{filter_type.split('_')[0]}_2103{{0.00}} +- @y_{filter_type.split('_')[0]}_2103_err{{0.00}} keV",
        ),
        (
            "583",
            f"@y_{filter_type.split('_')[0]}_583{{0.00}} +- @y_{filter_type.split('_')[0]}_583_err{{0.00}} keV",
        ),
    ]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def plot_no_fitted_energy_peaks(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], sort_dets_obj=sort_dets_obj
    )

    if sort_dets_obj is not None:
        chmap = sort_dets_obj.chmaps.valid_for(run_dict["timestamp"])
    else:
        cfg_file = prod_config["paths"]["chan_map"]
        configs = LegendMetadata(path=cfg_file)
        chmap = configs.channelmaps.on(run_dict["timestamp"])
    channels = [field for field in chmap if chmap[field]["system"] == "geds"]

    off_dets = [
        chmap[field] for field in soft_dict if soft_dict[field]["processable"] is False
    ]

    if cache_data is not None and run in cache_data["hit"]:
        res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        res = Props.read_from(path)
        cache_data["hit"][run] = res

    peaks = [583.191, 727.33, 860.564, 1592.511, 1620.5, 2103.511, 2614.511]
    grid = np.ones((len(peaks), len(channels)))
    for i, channel in enumerate(channels):
        idxs = np.zeros(len(peaks), dtype=bool)
        try:
            fitted_peaks = res[channel]["results"]["ecal"]["cuspEmax_ctc_cal"][
                "pk_fits"
            ]
            fitted_peaks = [pk for pk in fitted_peaks if fitted_peaks["pk"]["validity"]]
            if not isinstance(fitted_peaks, list):
                fitted_peaks = [fitted_peaks]
            for j, peak in enumerate(peaks):
                if peak in fitted_peaks:
                    idxs[j] = 1
            if len(idxs) > 0:
                grid[idxs, i] = 2

        except KeyError:
            if channel in off_dets:
                grid[:, i] = 0

    p = figure(
        width=1400,
        height=300,
        y_range=(0, 7),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | Energy fits"
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [f"{chmap[channel]['name']}" for channel in channels]
    p.image(
        image=[grid],
        x=0,
        y=0,
        dw=len(channels),
        dh=len(peaks),
        palette=["red", "orange", "green"],
        alpha=0.7,
    )

    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Peaks"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = FixedTicker(
        ticks=np.arange(0, len(channels), 1) + 0.5,
        minor_ticks=np.arange(0, len(channels), 1),
    )
    # p.xaxis.major_label_overrides = {i: label_res[i-1] for i in range(1, len(label_res)+1, 1)}
    p.xaxis.major_label_overrides = {
        i + 0.5: label_res[i] for i in range(0, len(label_res), 1)
    }
    p.xaxis.major_label_text_font_style = "bold"
    p.xgrid.grid_line_color = None
    p.xgrid.minor_grid_line_color = "black"
    p.xgrid.minor_grid_line_alpha = 0.1
    p.xaxis.minor_tick_line_color = None

    p.yaxis.ticker = FixedTicker(
        ticks=np.arange(0, len(peaks), 1) + 0.5, minor_ticks=np.arange(0, len(peaks), 1)
    )
    p.yaxis.major_label_overrides = {
        i + 0.5: f"{peaks[i]}" for i in range(0, len(peaks), 1)
    }
    p.ygrid.grid_line_color = None
    p.ygrid.minor_grid_line_color = "black"
    p.ygrid.minor_grid_line_alpha = 0.1
    p.yaxis.minor_tick_line_color = None

    return p


def plot_aoe_status(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], sort_dets_obj=sort_dets_obj
    )

    if sort_dets_obj is not None:
        chmap = sort_dets_obj.chmaps.valid_for(run_dict["timestamp"])
    else:
        cfg_file = prod_config["paths"]["chan_map"]
        configs = LegendMetadata(path=cfg_file)
        chmap = configs.channelmaps.on(run_dict["timestamp"])
    channels = [field for field in chmap if chmap[field]["system"] == "geds"]

    off_dets = [
        field for field in soft_dict if soft_dict[field]["processable"] is False
    ]

    if cache_data is not None and run in cache_data["hit"]:
        res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        res = Props.read_from(path)
        cache_data["hit"][run] = res

    checks = ["Time_corr", "Energy_corr", "Cut_det", "Low_side_sfs", "2_side_sfs"]

    grid = np.ones((len(checks), len(channels)))
    for i, channel in enumerate(channels):
        idxs = np.ones(len(checks), dtype=bool)
        try:
            aoe_dict = res[channel]["results"]["aoe"]
            if not np.isnan(aoe_dict["1000-1300keV"]["0"]["mean"]):
                idxs[0] = 1
            if not (
                np.isnan(
                    np.array(
                        [
                            value
                            for key, value in aoe_dict["correction_fit_results"][
                                "mean_fits"
                            ]["pars"].items()
                        ]
                    )
                ).all()
            ):
                idxs[1] = 1
            if not np.isnan(aoe_dict["low_cut"]):
                idxs[2] = 1
            if isinstance(aoe_dict["low_side_sfs"], float):
                pass
            else:
                sfs = [
                    float(dic["sf"]) for peak, dic in aoe_dict["low_side_sfs"].items()
                ]
                if not np.isnan(np.array(sfs)).all():
                    idxs[3] = 1
            if isinstance(aoe_dict["2_side_sfs"], float):
                pass
            else:
                sfs = [float(dic["sf"]) for peak, dic in aoe_dict["2_side_sfs"].items()]
                if not np.isnan(np.array(sfs)).all():
                    idxs[4] = 1

            if len(idxs) > 0:
                grid[idxs, i] = 2

        except KeyError:
            if channel in off_dets:
                grid[:, i] = 0

    p = figure(
        width=1400,
        height=300,
        y_range=(0, 5),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | A/E status"
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [f"{chmap[channel]['name']}" for channel in channels]
    p.image(
        image=[grid],
        x=0,
        y=0,
        dw=len(channels),
        dh=len(checks),
        palette=["red", "orange", "green"],
        alpha=0.7,
    )

    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Peaks"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = FixedTicker(
        ticks=np.arange(0, len(channels), 1) + 0.5,
        minor_ticks=np.arange(0, len(channels), 1),
    )
    # p.xaxis.major_label_overrides = {i: label_res[i-1] for i in range(1, len(label_res)+1, 1)}
    p.xaxis.major_label_overrides = {
        i + 0.5: label_res[i] for i in range(0, len(label_res), 1)
    }
    p.xaxis.major_label_text_font_style = "bold"
    p.xgrid.grid_line_color = None
    p.xgrid.minor_grid_line_color = "black"
    p.xgrid.minor_grid_line_alpha = 0.1
    p.xaxis.minor_tick_line_color = None

    p.yaxis.ticker = FixedTicker(
        ticks=np.arange(0, len(checks), 1) + 0.5,
        minor_ticks=np.arange(0, len(checks), 1),
    )
    p.yaxis.major_label_overrides = {
        i + 0.5: f"{checks[i]}" for i in range(0, len(checks), 1)
    }
    p.ygrid.grid_line_color = None
    p.ygrid.minor_grid_line_color = "black"
    p.ygrid.minor_grid_line_alpha = 0.1
    p.yaxis.minor_tick_line_color = None

    return p


def plot_no_fitted_aoe_slices(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["hit"]:
        res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        res = Props.read_from(path)
        cache_data["hit"][run] = res

    nfits = {}
    for stri in strings:
        nfits[stri] = np.nan
        for channel in strings[stri]:
            detector = channel_map[channel]["name"]
            try:
                nfits[detector] = res[channel]["results"]["aoe"][
                    "correction_fit_results"
                ]["n_of_valid_fits"]
            except KeyError:
                nfits[detector] = np.nan

    p = figure(
        width=1400,
        height=600,
        y_range=(1, 70),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | A/E fits"
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(nfits)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    df_plot["x_nfits"] = np.arange(1, len(list(nfits)) + 1, 1)
    df_plot["nfits"] = np.nan_to_num(list(nfits.values()))

    filter_types = ["nfits"]
    filter_names = ["Valid. A/E fits"]
    filter_plot_colors = ["blue"]

    for filter_type, filter_name, filter_plot_color in zip(
        filter_types, filter_names, filter_plot_colors, strict=False
    ):
        if filter_name == "Valid. A/E fits":
            hover_renderer = p.scatter(
                x=f"x_{filter_type}",
                y=filter_type,
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=filter_name,
                name=filter_name,
            )
        else:
            p.scatter(
                x=f"x_{filter_type}",
                y=filter_type,
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=filter_name,
                name=filter_name,
            )

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "# of A/E Fits"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(nfits)) + 1, 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(nfits)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=1.5, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [("Detector", "@label_res"), ("Valid. A/E fits", "@nfits")]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def get_aoe_results(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    download=False,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["hit"]:
        all_res = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_hit"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_hit.yaml'
        )

        all_res = Props.read_from(path)
        cache_data["hit"][run] = all_res

    default = {
        "A/E_Energy_param": "cuspEmax",
        "Cal_energy_param": "cuspEmax_ctc",
        "dt_param": "dt_eff",
        "rt_correction": False,
        "mean_pars": [np.nan, np.nan],
        "sigma_pars": [np.nan, np.nan],
        "low_cut": np.nan,
        "high_cut": np.nan,
        "low_side_sfs": {
            1592.5: {"sf": np.nan, "sf_err": np.nan},
            1620.5: {"sf": np.nan, "sf_err": np.nan},
            2039.0: {"sf": np.nan, "sf_err": np.nan},
            2103.53: {"sf": np.nan, "sf_err": np.nan},
            2614.5: {"sf": np.nan, "sf_err": np.nan},
        },
        "2_side_sfs": {
            1592.5: {"sf": np.nan, "sf_err": np.nan},
            1620.5: {"sf": np.nan, "sf_err": np.nan},
            2039.0: {"sf": np.nan, "sf_err": np.nan},
            2103.53: {"sf": np.nan, "sf_err": np.nan},
            2614.5: {"sf": np.nan, "sf_err": np.nan},
        },
    }

    aoe_res = {}
    for stri in strings:
        aoe_res[stri] = default
        for channel in strings[stri]:
            detector = channel_map[channel]["name"]

            try:
                aoe_res[detector] = all_res[detector]["results"]["aoe"]
                if len(aoe_res[detector]) == 0:
                    raise KeyError
            except KeyError:
                aoe_res[detector] = default.copy()

    # log.debug(aoe_res["V02160A"])
    # log.debug(aoe_res["P00698B"])

    p = figure(
        width=1400,
        height=600,
        y_range=(-5, 100),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | A/E Survival Fractions"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(aoe_res)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    peak_types = [1592.5, 1620.5, 2039.0, 2103.53, 2614.5]
    peak_names = ["Tl DEP", "Bi FEP", "CC @ Qbb", "Tl SEP", "Tl FEP"]
    peak_colors = ["blue", "orange", "green", "red", "purple"]

    for peak_type in peak_types:
        for det in aoe_res:
            log.debug(det)
            log.debug(aoe_res[det]["low_side_sfs"][peak_type]["sf"])
        # try:
        x_plot, y_plot, y_plot_err = (
            np.arange(1, len(list(aoe_res)) + 1, 1),
            [float(aoe_res[det]["low_side_sfs"][peak_type]["sf"]) for det in aoe_res],
            [
                float(aoe_res[det]["low_side_sfs"][peak_type]["sf_err"])
                for det in aoe_res
            ],
        )

        err_xs = []
        err_ys = []

        for x, y, yerr in zip(x_plot, y_plot, y_plot_err, strict=False):
            err_xs.append((x, x))
            err_ys.append((np.nan_to_num(y - yerr), np.nan_to_num(y + yerr)))

        df_plot["x_{}".format(str(peak_type).split(".")[0])] = np.nan_to_num(x_plot)
        df_plot["y_{}".format(str(peak_type).split(".")[0])] = np.nan_to_num(y_plot)
        df_plot["y_{}_err".format(str(peak_type).split(".")[0])] = np.nan_to_num(
            y_plot_err
        )
        df_plot["err_xs_{}".format(str(peak_type).split(".")[0])] = err_xs
        df_plot["err_ys_{}".format(str(peak_type).split(".")[0])] = err_ys

    if download:
        return (
            df_plot,
            f"{run_dict['experiment']}-{period}-{run}_AoE_SurvivalFractions.csv",
        )

    for peak_type, peak_name, peak_color in zip(
        peak_types, peak_names, peak_colors, strict=False
    ):
        if peak_type == 1592.5:
            hover_renderer = p.scatter(
                x="x_{}".format(str(peak_type).split(".")[0]),
                y="y_{}".format(str(peak_type).split(".")[0]),
                source=df_plot,
                color=peak_color,
                size=7,
                line_alpha=0,
                legend_label=peak_name,
                name=peak_name,
            )
        else:
            p.scatter(
                x="x_{}".format(str(peak_type).split(".")[0]),
                y="y_{}".format(str(peak_type).split(".")[0]),
                source=df_plot,
                color=peak_color,
                size=7,
                line_alpha=0,
                legend_label=peak_name,
                name=peak_name,
            )
        p.multi_line(
            xs="err_xs_{}".format(str(peak_type).split(".")[0]),
            ys="err_ys_{}".format(str(peak_type).split(".")[0]),
            source=df_plot,
            color=peak_color,
            legend_label=peak_name,
            name=peak_name,
        )

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Survival fraction (%)"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(aoe_res)), 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(aoe_res)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=-5, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [
        ("Detector", "@label_res"),
        ("SF CC @Qbb", "@y_2039{0.0} +- @y_2039_err{0.0} %"),
        ("SF Tl DEP", "@y_1592{0.0} +- @y_1592_err{0.0} %"),
        ("SF Bi FEP", "@y_1620{0.0} +- @y_1620_err{0.0} %"),
        ("SF Tl SEP", "@y_2103{0.0} +- @y_2103_err{0.0} %"),
        ("SF Tl FEP", "@y_2614{0.0} +- @y_2614_err{0.0} %"),
    ]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def plot_pz_consts(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    download=False,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["dsp"]:
        cal_dict = cache_data["hit"][run]
    else:
        file_path = Path(prod_config["paths"]["par_dsp"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_dsp.yaml'
        )

        cal_dict = Props.read_from(path)
        cache_data["dsp"][run] = cal_dict

    taus = {}

    for stri in strings:
        taus[stri] = np.nan
        for channel in strings[stri]:
            det = channel_map[channel]["name"]
            try:
                taus[det] = float(cal_dict[det]["pz"]["tau1"][:-3]) / 1000
            except KeyError:
                taus[det] = np.nan

    p = figure(
        width=1400,
        height=600,
        y_range=(350, 800),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | Pole Zero Constants"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(taus)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    pz_types = ["pz_constant"]
    pz_names = ["PZ constant"]
    pz_colors = ["blue"]

    for pz_type in pz_types:
        x_plot, y_plot, y_plot_err = (
            np.arange(1, len(list(taus)) + 1, 1),
            [taus[det] for det in taus],
            [10] * len(taus),
        )

        err_xs = []
        err_ys = []

        for x, y, yerr in zip(x_plot, y_plot, y_plot_err, strict=False):
            err_xs.append((x, x))
            err_ys.append((np.nan_to_num(y - yerr), np.nan_to_num(y + yerr)))

        df_plot["x_{}".format(pz_type.split("_")[0])] = np.nan_to_num(x_plot)
        df_plot["y_{}".format(pz_type.split("_")[0])] = np.nan_to_num(y_plot)
        df_plot["y_{}_err".format(pz_type.split("_")[0])] = np.nan_to_num(y_plot_err)
        df_plot["err_xs_{}".format(pz_type.split("_")[0])] = err_xs
        df_plot["err_ys_{}".format(pz_type.split("_")[0])] = err_ys

    if download:
        return (
            df_plot,
            f"{run_dict['experiment']}-{period}-{run}_PoleZero_Constants.csv",
        )

    # df_plot = ColumnDataSource(df_plot)
    for pz_type, pz_name, pz_color in zip(pz_types, pz_names, pz_colors, strict=False):
        if pz_type == "pz_constant":
            hover_renderer = p.scatter(
                x="x_{}".format(pz_type.split("_")[0]),
                y="y_{}".format(pz_type.split("_")[0]),
                source=df_plot,
                color=pz_color,
                size=7,
                line_alpha=0,
                legend_label=pz_name,
                name=pz_name,
            )
        else:
            p.scatter(
                x="x_{}".format(pz_type.split("_")[0]),
                y="y_{}".format(pz_type.split("_")[0]),
                source=df_plot,
                color=pz_color,
                size=7,
                line_alpha=0,
                legend_label=pz_name,
                name=pz_name,
            )
        p.multi_line(
            xs="err_xs_{}".format(pz_type.split("_")[0]),
            ys="err_ys_{}".format(pz_type.split("_")[0]),
            source=df_plot,
            color=pz_color,
            legend_label=pz_name,
            name=pz_name,
        )

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "PZ constant (µs)"
    p.yaxis.axis_label_text_font_size = "20px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(taus)), 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(taus)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=350, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [
        ("Detector", "@label_res"),
        ("PZ const.", "@y_pz{0.0} +- @y_pz_err{0.0} µs"),
    ]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def plot_alpha(
    prod_config,
    run,
    run_dict,
    path,
    period,
    key="String",
    sort_dets_obj=None,
    download=False,
    cache_data=None,
):
    strings, soft_dict, channel_map = sorter(
        path, run_dict["timestamp"], key=key, sort_dets_obj=sort_dets_obj
    )

    if cache_data is not None and run in cache_data["dsp"]:
        cal_dict = cache_data["dsp"][run]
    else:
        file_path = Path(prod_config["paths"]["par_dsp"]) / f"cal/{period}/{run}"
        path = (
            file_path
            / f'{run_dict["experiment"]}-{period}-{run}-cal-{run_dict["timestamp"]}-par_dsp.yaml'
        )

        cal_dict = Props.read_from(path)
        cache_data["dsp"][run] = cal_dict

    trap_alpha = {}
    cusp_alpha = {}
    zac_alpha = {}

    for stri in strings:
        trap_alpha[stri] = np.nan
        cusp_alpha[stri] = np.nan
        zac_alpha[stri] = np.nan
        for channel in strings[stri]:
            det = channel_map[channel]["name"]
            try:
                trap_alpha[det] = float(
                    cal_dict[det]["ctc_params"]["trapEmax_ctc"]["parameters"]["a"]
                )
                cusp_alpha[det] = float(
                    cal_dict[det]["ctc_params"]["cuspEmax_ctc"]["parameters"]["a"]
                )
                zac_alpha[det] = float(
                    cal_dict[det]["ctc_params"]["zacEmax_ctc"]["parameters"]["a"]
                )
            except KeyError:
                trap_alpha[det] = np.nan
                cusp_alpha[det] = np.nan
                zac_alpha[det] = np.nan

    p = figure(
        width=1400,
        height=600,
        y_range=(-1, 4),
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | Charge Trapping Constants"
    )
    p.title.align = "center"
    p.title.text_font_size = "25px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    label_res = [r if "String" not in r else "" for r in list(cusp_alpha)]

    df_plot = pd.DataFrame()
    df_plot["label_res"] = label_res

    df_plot["x_cuspEmax_ctc_cal"] = np.arange(1, len(list(cusp_alpha)) + 1, 1)
    df_plot["x_zacEmax_ctc_cal"] = np.arange(1, len(list(zac_alpha)) + 1, 1)
    df_plot["x_trapEmax_ctc_cal"] = np.arange(1, len(list(trap_alpha)) + 1, 1)
    df_plot["cuspEmax_ctc_cal"] = np.nan_to_num(list(cusp_alpha.values())) * 1e6
    df_plot["zacEmax_ctc_cal"] = np.nan_to_num(list(zac_alpha.values())) * 1e6
    df_plot["trapEmax_ctc_cal"] = np.nan_to_num(list(trap_alpha.values())) * 1e6

    filter_types = ["cuspEmax_ctc_cal", "zacEmax_ctc_cal", "trapEmax_ctc_cal"]
    filter_names = ["Cusp", "ZAC", "Trap"]
    filter_plot_colors = ["blue", "green", "red"]

    if download:
        return (
            df_plot,
            f"{run_dict['experiment']}-{period}-{run}_Charge_Trapping_Constants.csv",
        )

    # df_plot = ColumnDataSource(df_plot)
    for filter_type, filter_name, filter_plot_color in zip(
        filter_types, filter_names, filter_plot_colors, strict=False
    ):
        if filter_name == "Cusp":
            hover_renderer = p.scatter(
                x=f"x_{filter_type}",
                y=filter_type,
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=filter_name,
                name=filter_name,
            )
        else:
            p.scatter(
                x=f"x_{filter_type}",
                y=filter_type,
                source=df_plot,
                color=filter_plot_color,
                size=7,
                line_alpha=0,
                legend_label=filter_name,
                name=filter_name,
            )

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.xaxis.axis_label = "Detector"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = r"$$\text{Alpha Value} (\frac{10^{-6}}{\text{ns}})$$"
    p.yaxis.axis_label_text_font_size = "16px"

    p.xaxis.major_label_orientation = np.pi / 2
    p.xaxis.ticker = np.arange(1, len(list(cusp_alpha)), 1)
    p.xaxis.major_label_overrides = {
        i: label_res[i - 1] for i in range(1, len(label_res) + 1, 1)
    }
    p.xaxis.major_label_text_font_style = "bold"

    for stri in strings:
        loc = np.where(np.array(list(cusp_alpha)) == stri)[0][0]
        string_span = Span(
            location=loc + 1, dimension="height", line_color="black", line_width=3
        )
        string_span_label = Label(
            x=loc + 1.5, y=-0.95, text=stri, text_font_size="10pt", text_color="blue"
        )
        p.add_layout(string_span_label)
        p.add_layout(string_span)

    p.hover.tooltips = [
        ("Detector", "@label_res"),
        ("Alpha Cusp", "@cuspEmax_ctc_cal{0.00e}"),
        ("Alpha ZAC ", "@zacEmax_ctc_cal{0.00}"),
        ("Alpha Trap", "@trapEmax_ctc_cal{0.00}"),
    ]
    p.hover.mode = "vline"
    p.hover.renderers = [hover_renderer]

    return p


def plot_bls(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    cache_data=None,
):
    p = figure(
        width=700,
        height=600,
        y_axis_type="log",
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | Baseline | {string}"
    )
    p.title.align = "center"
    p.title.text_font_size = "15px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(channels)
    colours = cc.palette["glasbey_category10"][:len_colours]

    for i, channel in enumerate(channels):
        try:
            plot_dict_chan = plot_dict[channel]

            p.step(
                plot_dict_chan["baseline_spectrum"]["bins"],
                plot_dict_chan["baseline_spectrum"]["bl_array"],
                legend_label=f'{chan_dict[channel]["name"]}',
                mode="after",
                name=f'{chan_dict[channel]["name"]}',
                line_width=2,
                line_color=colours[i],
            )
        except KeyError:
            pass

    p.hover.tooltips = [("Detector", "$name"), ("Baseline", "$x"), ("Counts", "$y")]
    p.hover.mode = "vline"
    p.xaxis.axis_label = "Wf Baseline Mean - FC Baseline"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Counts"
    p.yaxis.axis_label_text_font_size = "16px"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


def plot_energy_spectra(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    energy_param="cuspEmax_ctc_cal",
    cache_data=None,
):
    p = figure(
        width=700,
        height=600,
        y_axis_type="log",
        x_axis_type="datetime",
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = (
        f"{run_dict['experiment']}-{period}-{run} | Cal. | Energy Spectra | {string}"
    )
    p.title.align = "center"
    p.title.text_font_size = "15px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(channels)
    colours = cc.palette["glasbey_category10"][:len_colours]

    for i, channel in enumerate(channels):
        try:
            plot_dict_chan = plot_dict[channel]
            p.step(
                plot_dict_chan[energy_param]["spectrum"]["bins"],
                plot_dict_chan[energy_param]["spectrum"]["counts"],
                legend_label=f'{chan_dict[channel]["name"]}',
                mode="after",
                name=f'{chan_dict[channel]["name"]}',
                line_width=2,
                line_color=colours[i],
            )
        except KeyError:
            pass

    p.xaxis.axis_label = "Energy (keV)"
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Counts"
    p.yaxis.axis_label_text_font_size = "16px"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p


def plot_baseline_stability(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    cache_data=None,
):
    times = None
    p = figure(
        width=700,
        height=600,
        x_axis_type="datetime",
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )
    p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | Baseline Stability | {string}"
    p.title.align = "center"
    p.title.text_font_size = "15px"

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    len_colours = len(channels)
    colours = cc.palette["glasbey_category10"][:len_colours]

    for i, channel in enumerate(channels):
        try:
            bl = plot_dict[channel]["baseline_stability"]["baseline"]
            # bl_spread = plot_dict[channel]["baseline_stability"]["spread"]
            mean = np.nanmean(bl[~np.isnan(bl)][:10])
            bl_mean = 100 * (bl - mean) / mean

            # define if condition such that timedelta only added if still in UTC
            base_time = plot_dict[channel]["baseline_stability"]["time"][0]
            dt_object_base = datetime.utcfromtimestamp(base_time)
            utc_offset_base = dt_object_base.utcoffset()

            if utc_offset_base is None:
                p.line(
                    [
                        (datetime.fromtimestamp(time) + timedelta(hours=2))
                        for time in plot_dict[channel]["baseline_stability"]["time"]
                    ],  # add two hours manually
                    bl_mean,
                    legend_label=f'{chan_dict[channel]["name"]}',
                    name=f'{chan_dict[channel]["name"]}',
                    line_width=2,
                    line_color=colours[i],
                )
                if times is None:
                    times = [
                        (datetime.fromtimestamp(t) + timedelta(hours=2))
                        for t in plot_dict[channel]["baseline_stability"]["time"]
                    ]
            if utc_offset_base is not None:
                p.line(
                    [
                        datetime.fromtimestamp(time)
                        for time in plot_dict[channel]["baseline_stability"]["time"]
                    ],
                    bl_mean,
                    legend_label=f'{chan_dict[channel]["name"]}',
                    name=f'{chan_dict[channel]["name"]}',
                    line_width=2,
                    line_color=colours[i],
                )
                if times is None:
                    times = [
                        datetime.fromtimestamp(t)
                        for t in plot_dict[f"ch{channel:03}"]["baseline_stability"][
                            "time"
                        ]
                    ]
        except KeyError:
            pass

    # revision of hover tool to display values correctly
    p.hover.formatters = {"$x": "datetime", "$y": "printf"}
    p.hover.tooltips = [
        ("Detector", "$name"),
        ("Time", "$x{%F %H:%M:%S CET}"),
        ("BL Shift (%)", "@y{0, 0.0000} %"),
    ]
    p.hover.mode = "vline"
    p.xaxis.axis_label = (
        f"Time (CET), starting: {times[0].strftime('%d/%m/%Y %H:%M:%S')}"
    )
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Shift (%)"
    p.yaxis.axis_label_text_font_size = "16px"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


def plot_stability(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    parameter,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    energy_param="cuspEmax_ctc",
    cache_data=None,
):
    times = None
    p = figure(
        width=700,
        height=600,
        x_axis_type="datetime",
        tools="pan, box_zoom, ywheel_zoom, hover,reset,save",
        active_scroll="ywheel_zoom",
    )

    level = 1
    zoom_in = ZoomInTool(
        level=level, dimensions="height", factor=0.5
    )  # set specific zoom factor
    zoom_out = ZoomOutTool(level=level, dimensions="height", factor=0.5)
    p.add_tools(zoom_in, zoom_out)
    # p.toolbar.active_drag = None      use this line to activate only hover and ywheel_zoom as active tool

    if parameter == "2614_stability":
        p.title.text = (
            f"{run_dict['experiment']}-{period}-{run} | Cal. | FEP Stability | {string}"
        )
    else:
        p.title.text = f"{run_dict['experiment']}-{period}-{run} | Cal. | Pulser Stability | {string}"
    p.title.align = "center"
    p.title.text_font_size = "15px"

    len_colours = len(channels)
    colours = cc.palette["glasbey_category10"][:len_colours]

    for i, channel in enumerate(channels):
        try:
            plot_dict_chan = plot_dict[channel]

            en = plot_dict_chan[energy_param][parameter]["energy"]
            # en_spread = plot_dict_chan[energy_param][parameter]["spread"]
            mean = np.nanmean(en[~np.isnan(en)][:10])
            en_mean = en - mean  # /mean

            # define if condition such that timedelta only added if still in UTC
            plot_time = plot_dict_chan[energy_param][parameter]["time"][0]
            dt_object_plot = datetime.utcfromtimestamp(plot_time)
            utc_offset = dt_object_plot.utcoffset()

            if utc_offset is None:
                p.line(
                    [
                        (datetime.fromtimestamp(time) + timedelta(hours=2))
                        for time in plot_dict_chan[energy_param][parameter]["time"]
                    ],  # add two hours manually
                    en_mean,
                    legend_label=f'{chan_dict[channel]["name"]}',
                    name=f'{chan_dict[channel]["name"]}',
                    line_width=2,
                    line_color=colours[i],
                )
                if times is None:
                    times = [
                        (datetime.fromtimestamp(t) + timedelta(hours=2))
                        for t in plot_dict_chan[energy_param][parameter]["time"]
                    ]
            if utc_offset is not None:
                p.line(
                    [
                        (datetime.fromtimestamp(time))
                        for time in plot_dict_chan[energy_param][parameter]["time"]
                    ],
                    en_mean,
                    legend_label=f'{chan_dict[channel]["name"]}',
                    name=f'{chan_dict[channel]["name"]}',
                    line_width=2,
                    line_color=colours[i],
                )
                if times is None:
                    times = [
                        datetime.fromtimestamp(t)
                        for t in plot_dict_chan[energy_param][parameter]["time"]
                    ]
        except KeyError:
            pass

    # revision of hover tool to display detector name and values correctly
    p.hover.formatters = {"$x": "datetime", "$y": "printf"}
    p.hover.tooltips = [
        ("Detector", "$name"),
        ("Time", "$x{%F %H:%M:%S CET}"),
        ("Energy Shift (%)", "@y{0, 0.0000} %"),
    ]
    p.hover.mode = "vline"
    p.xaxis.axis_label = (
        f"Time (CET), starting: {times[0].strftime('%d/%m/%Y %H:%M:%S')}"
    )
    p.xaxis.axis_label_text_font_size = "20px"
    p.yaxis.axis_label = "Energy Shift (keV)"
    p.yaxis.axis_label_text_font_size = "16px"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


def plot_fep_stability_channels2d(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    energy_param="cuspEmax_ctc_cal",
    cache_data=None,
):
    return plot_stability(
        prod_config,
        plot_dict,
        chan_dict,
        channels,
        string,
        "2614_stability",
        run,
        period,
        run_dict,
        key=key,
        sort_dets_obj=sort_dets_obj,
        energy_param=energy_param,
        cache_data=cache_data,
    )


def plot_pulser_stability_channels2d(
    prod_config,
    plot_dict,
    chan_dict,
    channels,
    string,
    run,
    period,
    run_dict,
    key="String",
    sort_dets_obj=None,
    energy_param="cuspEmax_ctc_cal",
    cache_data=None,
):
    return plot_stability(
        prod_config,
        plot_dict,
        chan_dict,
        channels,
        string,
        "pulser_stability",
        run,
        period,
        run_dict,
        key=key,
        sort_dets_obj=sort_dets_obj,
        energy_param=energy_param,
        cache_data=cache_data,
    )
