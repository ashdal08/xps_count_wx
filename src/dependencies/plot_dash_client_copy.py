# -*- coding: utf-8 -*-

from dash import Dash, html, dcc, callback, Input, Output, State, Patch, no_update, set_props

import signal
import dash
import plotly.graph_objects as go
import plotly.io as pio

from dash_bootstrap_templates import load_figure_template

from gevent.pywsgi import WSGIServer
import gevent

from shared_memory_dict import SharedMemoryDict

load_figure_template(["bootstrap"])

BOOTSTRAP = pio.templates["bootstrap"]
"""Bootstrap theme for the plotly figure."""

CONFIG: dict = {
    "scrollZoom": True,
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "svg",
        "filename": "custom_image",
        "scale": 1,
    },
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
}
"""Dictionary containing configuration options for the plotly plots."""

LAYOUT: dict = {
    "autosize": True,
    "template": BOOTSTRAP,
    "margin": {
        "l": 80,
        "r": 5,
        "b": 40,
        "t": 5,
        "pad": 5,
    },
    "dragmode": "pan",
    "font_size": 11,
    "hovermode": "closest",
    "modebar": {"orientation": "v"},
}
"""Dictionary containing the layout options for the plotly plots."""

LEGEND: dict = {
    "yanchor": "top",
    "y": 0.99,
    "xanchor": "left",
    "x": 0.01,
    "bgcolor": "rgba(255, 255, 255, 0.63)",
}
"""Dictionary describing the formattting of the legend in the plotly plots."""


def reset_fig(batch_mode: bool = False) -> go.Figure:
    """Method to create a blank plotly Figure with the required template.

    Parameters
    ----------
    batch_mode : bool, optional
        Booleann indicating if the measurement is a batch mode one, by default False

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly Figure object that is created.
    """
    trace_name = "pass_1"
    if batch_mode:
        trace_name = "b1_pass_1"
    fig = go.Figure(
        data=[go.Scatter(x=[], y=[], mode="markers+lines", line_width=1, marker_size=4, name=trace_name)],
        layout=go.Layout(
            **LAYOUT,
            xaxis_title="Binding Energy [eV]",
            yaxis_title="Counts",
            uirevision="no_change",
            legend={
                "orientation": "h",
                "xanchor": "center",
                "x": 0.5,
            },
        ),
    )

    fig = addPlotRefLines(fig)

    return fig


def addPlotRefLines(fig: go.Figure) -> go.Figure:
    """Method to add reference photoelectron spectral lines to the plot figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The plotly Figure object on which the reference lines are to be added.

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly Figure in which the reference lines are added.
    """
    fig.add_vline(
        x=83.95,
        line=dict(
            color="#B3DF72",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{Au 4f}_\text{7/2}$",
        showlegend=True,
    )
    fig.add_vline(
        x=87.9,
        line=dict(
            color="#FD9891",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{Au 4f}_\text{5/2}$",
        showlegend=True,
    )
    fig.add_vline(
        x=284.4,
        line=dict(
            color="#FEC195",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{C 1s}$",
        showlegend=True,
    )
    fig.add_vline(
        x=72.84,
        line=dict(
            color="#F5CD47",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{Al 2p}_\text{3/2}$",
        showlegend=True,
    )
    fig.add_vline(
        x=532.70,
        line=dict(
            color="#7EE2B8",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{O 1s}$",
        showlegend=True,
    )
    fig.add_vline(
        x=118,
        line=dict(
            color="#9DD9EE",
            width=3,
            dash="dash",
        ),
        opacity=0.6,
        name=r"$\large \text{Al 2s}$",
        showlegend=True,
    )

    return fig


share_mem_plot_data = SharedMemoryDict(name="plotdata", size=3000)
"""Shared memory buffer where the plot data is saved by the main program."""

app = Dash(__name__)
"""The main Dash app."""

# Initialize figure and trace outside the callback function
fig = reset_fig()
"""Figure variable for the plot area of the dash app."""

app.layout = html.Div(
    [
        dcc.Graph(
            id="live-update-graph",
            figure=fig,
            config=CONFIG,
            style={
                "height": "97vh",
                "width": "97vw",
            },
            mathjax=True,
        ),
        dcc.Interval(
            id="interval-component",
            interval=1 * 500,  # in milliseconds
            n_intervals=0,
        ),
        dcc.Store(id="iteration-no", data=0),
    ],
    style={"height": "97vh", "width": "97vw"},
)

# Production server setup
http_server = WSGIServer(("", 8050), app.server)
"""The WSGI production server to serve the Dash app with the plot."""


@callback(
    Output("live-update-graph", "figure"),
    Output("iteration-no", "data"),
    Input("interval-component", "n_intervals"),
    State("live-update-graph", "figure"),
    State("iteration-no", "data"),
)
def update_graph_live(n: int, ex_fig: dict, local_iter: int) -> tuple[Patch | dash._callback.NoUpdate, int]:
    """Method that is called in periodic intervals.

    Parameters
    ----------
    n : int
        The number of intervals. Not used.
    ex_fig : dict
        The plotly Figure from the dash plot server.

    Returns
    -------
    dash.Patch | dash._callback.NoUpdate
        The Patch to the plotly Figure of the Dash server. no_update incase an Exception is raised or a measurement is cancelled.
    """
    fig_2 = go.Figure(ex_fig)
    patched_figure = Patch()

    try:
        # fig_2 = go.Figure(ex_fig_data, ex_fig_layout)

        running_status = share_mem_plot_data["run_status"]
        data_packet = share_mem_plot_data["fig"]
        cancel_status = share_mem_plot_data["cancelled"]
        batch_data = share_mem_plot_data["batch_details"]

        set_props("interval-component", props={"interval": int(0.5*share_mem_plot_data["interval"]*1000)})


        global_iter = share_mem_plot_data["iteration"]
        # data_packet = {
        #         "Binding Energy [eV]": [],
        #         "Pass No.": 1,
        #         "Time_per_step [s]": [],
        #         "Counts": [],
        #         "Counts_per_milli [/ms]": [],
        #         "U6_DAC0_Voltage [V]": [],
        #         "MAX5216_DAC_Voltage [V]": [],
        #     }

        new_x = data_packet["Binding Energy [eV]"]
        new_y = data_packet["Counts"]
        new_pass_no = data_packet["Pass No."]

        if running_status:
            if local_iter < global_iter:
                if not batch_data["batch_type"]:
                    return addOrUpdateTrace(fig_2, new_pass_no, f"pass_{int(new_pass_no)}", new_x, new_y), global_iter
                else:
                    return addOrUpdateTrace(
                        fig_2, batch_data["batch_pass_no"], f"b{batch_data['batch_no']}_pass_{new_pass_no}", new_x, new_y
                    ), global_iter
            elif global_iter==1:
                return no_update, 0
            else:
                return no_update, local_iter
        else:
            if not cancel_status:
                return no_update, 0

            fig_2 = reset_fig()

            patched_figure["data"] = fig_2.to_dict()["data"]

            return patched_figure, 0
    except Exception as e:
        print(e)
        return no_update, local_iter


def addOrUpdateTrace(fig_2: go.Figure, new_pass_no: int, pass_name: str, new_x: float, new_y: float) -> Patch:
    """Method called to add or update the traces in a plotly Figure.

    Parameters
    ----------
    fig_2 : plotly.graph_objects.Figure
        The plotly Figure object in which traces are to be added or updated.
    new_pass_no : int
        Integer indicating the new pass no of the measurement point.
    pass_name : str
        String with the name of the trace to be added or updated.
    new_x : float
        x coordinate of the point to be added or updated to the trace.
    new_y : float
        y coordinate of the point to be added or updated to the trace.

    Returns
    -------
    dash.Patch
        The patch to the plotly Figure object.
    """
    existing_passes = len(fig_2["data"])
    patched_figure = Patch()
    if existing_passes < new_pass_no:
        fig_2.add_trace(
            go.Scatter(
                x=[new_x],
                y=[new_y],
                mode="markers+lines",
                line_width=1,
                marker_size=4,
                name=pass_name,
            )
        )
        patched_figure["data"] = fig_2.to_dict()["data"]
        return patched_figure

    patched_figure["data"][existing_passes - 1]["x"].append(new_x)
    patched_figure["data"][existing_passes - 1]["y"].append(new_y)

    return patched_figure


def term_handler() -> None:
    r"""Method to terminate the server after receiving a SIGTERM signal."""
    print("Received SIGTERM - Gracefully shutting down...")
    share_mem_plot_data.shm.close()
    share_mem_plot_data.shm.unlink()
    http_server.stop()


if __name__ == "__main__":
    # app.run(debug=True)

    gevent.signal_handler(signal.SIGTERM, term_handler)
    http_server.serve_forever()
