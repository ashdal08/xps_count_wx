# -*- coding: utf-8 -*-
import os
import subprocess
import time
from dependencies import mainframe
import wx
import pywinstyles

import u6
# from dependencies import dummy_labjack_u6 as u6
import threading

# import LabJackPython as ljud
import polars as pl

# Library to plot the data, during (live) and after measurement
import plotly.graph_objects as go
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template

from shared_memory_dict import SharedMemoryDict

# **************************************************************************

load_figure_template(["bootstrap"])

BOOTSTRAP = pio.templates["bootstrap"]
"""Bootstrap template for the plotly figure."""

CONFIG = dict({
    "scrollZoom": True,
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "svg",  # one of png, svg, jpeg, webp
        "filename": "custom_image",
        "height": None,
        "width": None,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
})
"""Dictionary containing configuration options for the plotly plots."""
LAYOUT = dict(
    autosize=True,
    template=BOOTSTRAP,
    margin=dict(l=70, r=50, b=50, t=50, pad=4),
    dragmode="pan",
    font_size=11,
    hovermode="closest",
    modebar={"orientation": "v"},
)
"""Dictionary containing the layout options for the plotly plots."""


def reset_fig(batch_mode: bool = False) -> go.Figure:
    """Method to create blank plot figure.

    Parameters
    ----------
    batch_mode : bool, optional
        Boolean indicating if the measurement is a batch mode measurement, by default False

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly Figure object created.
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
        The pltoly graph objects in which the reference lines are to be added.

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly Figure object with the added reference lines.
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


def addOrUpdatePlotTraceData(
    fig: go.Figure, pass_index: int, x_data: pl.Series, y_data: pl.Series, trace_name: str
) -> go.Figure:
    """Method to add or update the trace in the plotly Figure object.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The plotly Figure object in which the trace dat is to be added or updated.
    pass_index : int
        The integer indicating the pass no. of the new data to be updated.
    x_data : pl.Series
        The x coordinates for the trace to be added or updated.
    y_data : pl.Series
        The y coordinates for the trace data to be added or updated.
    trace_name : str
        The trace name that is to be added or updated.

    Returns
    -------
    plotly.graph_objects.Figure
        The plotly Figure object after adding or updating the traces.
    """
    existing_passes = len(fig["data"])
    if existing_passes < pass_index:
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                mode="markers+lines",
                line_width=1,
                marker_size=4,
                name=trace_name,
            )
        )
    fig.update_traces(
        overwrite=False,
        x=x_data,
        y=y_data,
        selector=dict(name=trace_name),
    )

    return fig


app = wx.App(False)
"""The wxApp for the GUI frontend."""


class MainWindow(mainframe.mainFrame):
    """Class for the GUI backend.

    Methods
    -------
    connectLabJack:
        Connect to the Labjack U6 device.
    bindingEnergyToVolt:
        Convert the binding energy to voltage for the MAX5216 DAC.
    setSpiVoltage:
        Set the voltage at the MAX5216 DAC.
    startMeasurement:
        Start the measurement process.
    runSingleMeasurement:
        Run a single measurement.
    runBatchMeasurement:
        Run a batch measurement.
    saveMeasurementData:
        Save the measurement data to a CSV file.
    sendSharedData:
        Method to save data to the Shared Memory which is also accessed by the plot server for plotting.
    startPlotServer:
        Code to execute when the Restart Plot Server button is clicked.
    enableControls:
        Enable the controls in the UI.
    disableControls:
        Disable the controls in the UI.
    interruptionClicked:
        Handle the interruption of the measurement.
    onClose:
        Method fired when the close button is clicked.
    """

    BATCH_START_EV = 0
    """Index of the start energy value in the batch input table."""
    BATCH_END_EV = 1
    """Index of the end energy value in the batch input table."""
    BATCH_STEP_EV = 2
    """Index of the step energy value in the batch input table."""
    BATCH_TIME_PER_STEP = 3
    """Index of the time per step value in the batch input table."""
    BATCH_PASSES = 4
    """Index of the number of passes value in the batch input table."""
    EXCITATION_AL = 1486.6
    """The excitation energy for Aluminium cathode."""
    EXCITATION_MG = 1253.6
    """The excitation energy for Magnesium cathode."""
    U6_MOSI_PIN_NUM = 2
    """The MOSI pin number for the Labjack U6."""
    U6_MISO_PIN_NUM = 4
    """The MISO pin number for the Labjack U6."""
    U6_CLK_PIN_NUM = 1
    """The CLK pin number for the Labjack U6."""
    U6_CS_PIN_NUM = 3
    """The CS pin number for the Labjack U6."""
    DEP_PATH = ".\\src\\dependencies\\"
    """Path for all the files that the program requires to function."""
    # These variables contain settings for the plotly plots / live plot seen in the UI
    CONFIG = dict({
        "scrollZoom": True,
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "svg",  # one of png, svg, jpeg, webp
            "filename": "custom_image",
            "height": None,
            "width": None,
            "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
        },
        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    })
    """Dictionary containing configuration options for the plotly plots."""
    LAYOUT = dict(
        autosize=True,
        template=BOOTSTRAP,
        margin=dict(l=70, r=50, b=50, t=50, pad=4),
        dragmode="pan",
        font_size=11,
        hovermode="closest",
        modebar={"orientation": "v"},
    )
    """Dictionary containing the layout options for the plotly plots."""

    start_ev: float
    """The starting energy value for the measurement."""
    end_ev: float
    """The ending energy value for the measurement."""
    step_ev: float
    """The step width for the measurement."""
    setpoint_ev: float
    """The current energy value for the measurement."""
    time_per_step: float
    """The time per step for the measurement."""
    pass_no: int
    """The number of passes for the measurement."""
    u6_labjack: u6.U6
    """Lajack U6 object for the measurement."""
    labjack_connect: bool
    """Boolean to check if the Labjack is connected."""
    data_table: pl.DataFrame
    """Polars DataFrame to store the measurement data."""
    pass_row_indexes: list
    """List of row indices indicating start of new passes."""
    typ_schema: dict
    """Dictionary with the type schema for the polars Dataframe."""
    measurement_thread: threading.Thread
    """Thread object to run the measurement."""
    excitation_voltage: float
    """Selected excitation voltage for the measurement."""
    plot_fig: go.Figure
    """Plotly figure object to plot the measurement data."""
    share_mem_plot_data: SharedMemoryDict
    """Shared memory buffer to store the plot data."""
    plot_server_process: subprocess.Popen
    """Plot server process to display the plot in the UI."""
    plot_file_name: str
    """HTML plot file name."""
    meas_interrupted: bool = False
    """Boolean to check if the measurement was interrupted."""
    meas_interrupt_id: int
    """ID of the button that was clicked to interrupt the measurement."""
    meas_running: bool = False
    """Boolean to check if the measurement is running."""
    total_batch_passes: int = 0
    """Integer holding the total batch passes during the batch mode measurement."""
    batch_pass_no: int = 1
    """Integer holding the current batch pass no. during a batch measurement."""
    batch_step_no: int = 1
    """Integer holding the current step no. during a batch mode measuremeet."""
    plot_iter:int = 1
    """Integer holding the plot iteration of the measurement. Reset to 1 after every measurement."""

    def __init__(self, parent) -> None:
        """
        Initialize the main window of the program.

        Parameters
        ----------
        parent : wx.Window
            The parent window of the main window.

        """
        mainframe.mainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.connectLabjack()

        # Disable history in for the plot window (browser based).
        self.plotView.EnableHistory(False)

        # Disable plot window DevTools access.
        self.plotView.EnableAccessToDevTools(True)

        # Disable plot window context menu.
        self.plotView.EnableContextMenu(True)

        self.plot_file_name = "".join([os.getcwd(), "\\src\\dependencies\\", "plt_dat.html"])

        self.share_mem_plot_data = SharedMemoryDict(name="plotdata", size=3000)
        self.startPlotServer(None)
        new_data_temp = {
            "Binding Energy [eV]": None,
            "Pass No.": 1,
            "Time_per_step [s]": None,
            "Counts": None,
            "Counts_per_milli [/ms]": None,
            "U6_DAC0_Voltage [V]": None,
            "MAX5216_DAC_Voltage [V]": None,
        }
        self.share_mem_plot_data["interval"] = 0.5
        self.sendSharedData(new_data_temp, False, True, False, 1, 1)
        # Load plot html in the plot window.
        self.plotView.LoadURL("http://localhost:8050/")
        self.pass_row_indexes = []

        self.Fit()
        self.Update()

    def connectLabjack(self) -> None:
        """Connect to the Labjack U6 device."""
        self.u6_labjack = u6.U6()
        self.u6_labjack.getCalibrationData()
        self.u6_labjack.configIO(EnableCounter0=True)
        # ljud.eDAC(self.u6_labjack, 1, 3)  # Set the reference voltage for the MAX5216 DAC
        self.u6_labjack.getFeedback(u6.DAC1_8(self.u6_labjack.voltageToDACBits(3, 1)))
        self.labjack_connect = True

    def bindingEnergyToVolt(self, binding_energy: float) -> float:
        """Convert the binding energy to voltage for the MAX5216 DAC.

        Parameters
        ----------
        binding_energy : float
            The binding energy value.

        Returns
        -------
        float
            The voltage value for the MAX5216 DAC.

        """
        self.setpoint_ev = binding_energy
        kinetic_energy = self.excitation_voltage - binding_energy
        self.bindingEnergy.SetValue(str(binding_energy))
        self.kineticEnergy.SetValue(str(kinetic_energy))
        self.Update()
        return kinetic_energy / 498.43

    def setSpiVoltage(self, volt: float) -> None:
        """Set the voltage at the MAX5216 DAC.

        Parameters
        ----------
        volt : float
            The voltage value to set at the MAX5216 DAC.

        """
        ref_volt_at_MAX5216_DAC = self.u6_labjack.getAIN(3)  # the reference voltage at the DAC MAX5216
        volt_bits = int(
            volt * 65535 / ref_volt_at_MAX5216_DAC
        )  # convert input volts to a 16 bit scaled value with the reference voltage
        volt_bits = (
            volt_bits << 6
        )  # shift the 16 bit value 6 bits to the left to make it a 22 bit value. Refer to MAX5216 datasheet
        volt_bits |= (
            1 << 22
        )  # set the 23rd bit to 1 to indicate that the first 2 bits are the command bits. Refer to MAX5216 datasheet
        self.u6_labjack.spi(
            list(volt_bits.to_bytes(3)),
            CSPINNum=self.U6_CS_PIN_NUM,
            CLKPinNum=self.U6_CLK_PIN_NUM,
            MISOPinNum=self.U6_MISO_PIN_NUM,
            MOSIPinNum=self.U6_MOSI_PIN_NUM,
        )
        # ljud.eDAC(self.u6_labjack, 0, volt)  # Set the voltage at DAC0 of the Labjack for comparison with MAX5216.
        self.u6_labjack.getFeedback(u6.DAC0_8(self.u6_labjack.voltageToDACBits(volt, 0)))

    def startMeasurement(self, event: wx.Event) -> None:
        """Start the measurement process.

        Parameters
        ----------
        event : wxEvent
            wxEVT_BUTTON event generated.

        """
        if self.excitationSelect.GetValue():
            # if the excitation slider in the UI is set to Mg, value will be 1. Hence True.
            self.excitation_voltage = self.EXCITATION_MG
        else:
            self.excitation_voltage = self.EXCITATION_AL

        if self.modeSelect.GetSelection():
            # if Batch Scan tab is selected in the UI. Batch scan mode is 1. Single scan mode is 0.

            start_ev: float
            end_ev: float
            step_ev: float
            time_per_step: float
            pass_no: int

            total_time_s = 0
            total_steps = 0
            self.total_batch_passes = 0
            self.batch_pass_no = 1
            self.batch_step_no = 1

            for row_index in range(1, self.batchInput.GetNumberRows()):
                batch_time = 0
                start_ev = self.batchInput.GetCellValue(row_index, self.BATCH_START_EV).strip()
                end_ev = self.batchInput.GetCellValue(row_index, self.BATCH_END_EV).strip()
                step_ev = self.batchInput.GetCellValue(row_index, self.BATCH_STEP_EV).strip()
                time_per_step = self.batchInput.GetCellValue(row_index, self.BATCH_TIME_PER_STEP).strip()
                pass_no = self.batchInput.GetCellValue(row_index, self.BATCH_PASSES).strip()
                if (
                    not len(start_ev)
                    or not len(end_ev)
                    or not len(step_ev)
                    or not len(time_per_step)
                    or not len(pass_no)
                ):
                    break
                batch_time = (
                    float(time_per_step) * float(pass_no) * ((float(end_ev) - float(start_ev)) / float(step_ev) + 1)
                )
                total_time_s += batch_time
                total_steps += ((float(end_ev) - float(start_ev)) / float(step_ev) + 1) * pass_no
                self.total_batch_passes += pass_no

            self.elapsedTime.SetValue("0")
            self.remainingTime.SetValue(str(round(total_time_s / 60, 2)))
            self.measProgress.SetRange(float(total_steps))
            self.measProgress.SetValue(0)
            self.measurement_thread = threading.Thread(target=self.runBatchMeasurement)
            self.plot_fig = reset_fig(batch_mode=True)
        else:
            self.start_ev = self.singleStarteV.GetValue()
            self.end_ev = self.singleEndeV.GetValue()
            self.step_ev = self.singleStepWidtheV.GetValue()
            self.time_per_step = self.singleTimePerStep.GetValue()
            self.pass_no = self.singlePasses.GetValue()
            self.measProgress.SetRange(int(abs((self.end_ev - self.start_ev) / self.step_ev + 1) * self.pass_no))
            total_time_s = self.time_per_step * self.pass_no * ((self.end_ev - self.start_ev) / self.step_ev + 1)
            self.remainingTime.SetValue(str(round(total_time_s / 60, 2)))
            self.elapsedTime.SetValue("0")
            self.measProgress.SetValue(0)

            self.measurement_thread = threading.Thread(
                target=self.runSingleMeasurement,
                args=[self.start_ev, self.end_ev, self.step_ev, self.time_per_step, self.pass_no, 0, 0, False],
            )
            self.plot_fig = reset_fig()

        self.typ_schema = {
            "Binding Energy [eV]": pl.Float64,
            "Pass No.": pl.Float64,
            "Time_per_step [s]": pl.Float64,
            "Counts": pl.Float64,
            "Counts_per_milli [/ms]": pl.Float64,
            "U6_DAC0_Voltage [V]": pl.Float64,
            "MAX5216_DAC_Voltage [V]": pl.Float64,
        }
        data_temp = {
            "Binding Energy [eV]": [],
            "Pass No.": [],
            "Time_per_step [s]": [],
            "Counts": [],
            "Counts_per_milli [/ms]": [],
            "U6_DAC0_Voltage [V]": [],
            "MAX5216_DAC_Voltage [V]": [],
        }

        self.data_table = pl.DataFrame(
            data_temp,
            schema=self.typ_schema,
        )

        self.pass_row_indexes = [0]
        new_data_temp = {
            "Binding Energy [eV]": None,
            "Pass No.": 1,
            "Time_per_step [s]": None,
            "Counts": None,
            "Counts_per_milli [/ms]": None,
            "U6_DAC0_Voltage [V]": None,
            "MAX5216_DAC_Voltage [V]": None,
        }
        batch_mode_check = False
        if self.modeSelect.GetSelection():
            batch_mode_check = True
        self.sendSharedData(new_data_temp, False, True, batch_mode_check, 1, 1)

        self.meas_running = True
        self.meas_interrupted = False
        self.measurement_thread.start()

        self.disableControls()
        event.Skip()

    def runSingleMeasurement(
        self,
        start_ev: float,
        end_ev: float,
        step_ev: float,
        time_per_step: float,
        pass_no: int,
        batch_no: int,
        batch_pass_no: int,
        type_batch=False,
    ) -> None:
        """Run a single measurement.

        Parameters
        ----------
        start_ev : float
            The starting energy value for the measurement in eV.
        end_ev : float
            The ending energy value for the measurement in eV.
        step_ev : float
            The step width for the measurement in eV.
        time_per_step : float
            The time per step for the measurement in s.
        pass_no : int
            The number of passes for the measurement.
        type_batch : bool
            The type of measurement. True for batch measurement, False for single measurement.

        """
        self.setSpiVoltage(self.bindingEnergyToVolt(start_ev))

        pass_index = 1

        typ_schema = {
            "Binding Energy [eV]": pl.Float64,
            "Counts": pl.Float64,
        }
        data_temp = {
            "Binding Energy [eV]": [],
            "Counts": [],
        }

        plot_dataframe = pl.DataFrame(
            data_temp,
            schema=typ_schema,
        )

        self.share_mem_plot_data["interval"] = time_per_step


        while pass_index <= pass_no:
            self.u6_labjack.getFeedback(u6.Counter0(True))
            start_time = time.time()
            __refresh_time = 0
            while __refresh_time <= time_per_step:
                if self.meas_interrupted:
                    break
                if __refresh_time + 1 < time_per_step:
                    time.sleep(1)
                    __refresh_time += 1
                else:
                    time.sleep(time_per_step - __refresh_time)
                    break

            if self.meas_interrupted:
                self.meas_interrupted = False
                if self.meas_interrupt_id == wx.ID_CANCEL:
                    self.measProgress.SetValue(0)
                    data_temp = {
                        "Binding Energy [eV]": None,
                        "Pass No.": 1,
                        "Time_per_step [s]": None,
                        "Counts": None,
                        "Counts_per_milli [/ms]": None,
                        "U6_DAC0_Voltage [V]": None,
                        "MAX5216_DAC_Voltage [V]": None,
                    }
                    self.data_table = pl.DataFrame(
                        data_temp,
                        schema=self.typ_schema,
                    )

                    self.pass_row_indexes = [0]
                    self.sendSharedData(data_temp, False, True, False, 1, 1)
                    return
                else:
                    self.saveMeasurementData(False)
                    return
            # time.sleep(self.time_per_step)
            # counts = ljud.eTCValues(
            #     self.u6_labjack,
            #     aReadTimers=[0, 0, 0, 0],
            #     aUpdateResetTimers=[0, 0, 0, 0],
            #     aReadCounters=[1, 0],
            #     aResetCounters=[0, 0],
            #     aTimerValues=[0, 0, 0, 0],
            # )[1][0]
            counts = self.u6_labjack.getFeedback(u6.Counter0(False))[0]
            time_taken = time.time() - start_time  # record in s
            binding_energy = self.setpoint_ev
            counts_per_milli = round(counts / (time_taken * 1000), 6)
            u6_dac0_voltage = round(self.u6_labjack.getAIN(0), 6)
            max5216_dac_voltage = round(self.u6_labjack.getAIN(2), 6)

            new_data = {
                "Binding Energy [eV]": binding_energy,
                "Pass No.": pass_index,
                "Time_per_step [s]": time_taken,
                "Counts": counts,
                "Counts_per_milli [/ms]": counts_per_milli,
                "U6_DAC0_Voltage [V]": u6_dac0_voltage,
                "MAX5216_DAC_Voltage [V]": max5216_dac_voltage,
            }

            new_plot_point = pl.DataFrame(
                {
                    "Binding Energy [eV]": [binding_energy],
                    "Counts": [counts],
                },
                schema=typ_schema,
            )
            plot_dataframe = pl.concat([plot_dataframe, new_plot_point])

            new_df = pl.DataFrame(new_data, schema=self.typ_schema)
            self.data_table = pl.concat([self.data_table, new_df])
            if not type_batch:
                self.plot_fig = addOrUpdatePlotTraceData(
                    self.plot_fig,
                    pass_index,
                    plot_dataframe["Binding Energy [eV]"],
                    plot_dataframe["Counts"],
                    f"pass_{pass_index}",
                )
            else:
                self.plot_fig = addOrUpdatePlotTraceData(
                    self.plot_fig,
                    self.batch_pass_no,
                    plot_dataframe["Binding Energy [eV]"],
                    plot_dataframe["Counts"],
                    f"b{batch_no}_pass_{pass_index}",
                )
            # if not type_batch:
            #     if existing_passes < pass_index:
            #         self.pass_row_indexes.append(temp_row_index)
            #         self.plot_fig.add_trace(
            #             go.Scatter(
            #                 x=plot_dataframe["Binding Energy [eV]"],
            #                 y=plot_dataframe["Counts"],
            #                 mode="markers+lines",
            #                 line_width=1,
            #                 marker_size=4,
            #                 name=f"pass_{pass_index}",
            #             )
            #         )
            #     self.plot_fig.update_traces(
            #         overwrite=False,
            #         x=plot_dataframe["Binding Energy [eV]"],
            #         y=plot_dataframe["Counts"],
            #         selector=dict(name=f"pass_{pass_index}"),
            #     )
            # else:
            #     if existing_passes < self.batch_pass_no:
            #         self.plot_fig.add_trace(
            #             go.Scatter(
            #                 x=plot_dataframe["Binding Energy [eV]"],
            #                 y=plot_dataframe["Counts"],
            #                 mode="markers+lines",
            #                 line_width=1,
            #                 marker_size=4,
            #                 name=f"b{batch_no}_pass_{pass_index}",
            #             )
            #         )
            #     self.plot_fig.update_traces(
            #         overwrite=False,
            #         x=plot_dataframe["Binding Energy [eV]"],
            #         y=plot_dataframe["Counts"],
            #         selector=dict(name=f"b{batch_no}_pass_{pass_index}"),
            #     )
            self.plot_fig.write_html(
                self.plot_file_name,
                config=self.CONFIG,
                include_plotlyjs="cdn",
            )

            self.sendSharedData(new_data, True, False, type_batch, batch_no, self.plot_iter)

            self.measProgress.SetValue(self.measProgress.GetValue() + 1)
            new_remaining_time = float(self.remainingTime.GetValue()) - time_taken / 60
            self.remainingTime.SetValue(str(round(new_remaining_time, 2)))
            new_elapsed_time = float(self.elapsedTime.GetValue()) + time_taken / 60
            self.elapsedTime.SetValue(str(round(new_elapsed_time, 2)))

            if self.setpoint_ev + step_ev <= end_ev:
                self.setpoint_ev += step_ev
                if type_batch:
                    self.batch_step_no += 1
                self.setSpiVoltage(self.bindingEnergyToVolt(self.setpoint_ev))
            else:
                self.setSpiVoltage(self.bindingEnergyToVolt(start_ev))
                pass_index += 1
                if type_batch:
                    self.batch_pass_no += 1
                plot_dataframe = pl.DataFrame(
                    {
                        "Binding Energy [eV]": [],
                        "Counts": [],
                    },
                    typ_schema,
                )

            self.Update()
            self.plot_iter += 1

        self.saveMeasurementData(type_batch)

    def runBatchMeasurement(self) -> None:
        """Run a batch measurement."""
        for row_index in self.batchInput.GetNumberRows():
            if self.meas_running:
                self.start_ev = self.batchInput.GetCellValue(row_index, self.BATCH_START_EV).strip()
                self.end_ev = self.batchInput.GetCellValue(row_index, self.BATCH_END_EV).strip()
                self.step_ev = self.batchInput.GetCellValue(row_index, self.BATCH_STEP_EV).strip()
                self.time_per_step = self.batchInput.GetCellValue(row_index, self.BATCH_TIME_PER_STEP).strip()
                self.pass_no = self.batchInput.GetCellValue(row_index, self.BATCH_PASSES).strip()
                if (
                    not len(self.start_ev)
                    or not len(self.end_ev)
                    or not len(self.step_ev)
                    or not len(self.time_per_step)
                    or not len(self.pass_no)
                ):
                    self.saveMeasurementData(False)
                    break
                self.runSingleMeasurement(
                    self.start_ev,
                    self.end_ev,
                    self.step_ev,
                    self.time_per_step,
                    self.pass_no,
                    row_index + 1,
                    self.batch_pass_no,
                    True,
                )
        return

    def saveMeasurementData(self, batch: bool) -> None:
        """Save the measurement data to a CSV file.

        Parameters
        ----------
        batch : bool
            The type of measurement. True for batch measurement, False for single measurement.
        """
        if not batch:
            wait = wx.BusyCursor()
            wxsavefiledialog1 = wx.FileDialog(
                self,
                "Save data as",
                defaultFile=wx.DateTime.UNow().Format("%d%m%y"),
                wildcard="CSV files(*.csv)|*.csv",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            )
            if wxsavefiledialog1.ShowModal() == wx.ID_CANCEL:
                wxsavefiledialog1.SetFilename("")
                # copy of file for plotting
                filename = self.DEP_PATH + "aktualdata.csv"

                self.data_table.write_csv(filename)
            else:
                if len(wxsavefiledialog1.GetFilename()):
                    filename = wxsavefiledialog1.GetPath()

                    self.data_table.write_csv(filename)
                    self.plot_fig.write_html(
                        filename.removesuffix(".csv") + ".html",
                        config=self.CONFIG,
                        include_plotlyjs="cdn",
                    )

                    # copy of file for plotting
                    filename = self.DEP_PATH + "aktualdata.csv"

                    self.data_table.write_csv(filename)

                wxsavefiledialog1.SetFilename("")
            del wait
            self.measProgress.SetValue(self.measProgress.GetRange())
            self.remainingTime.SetValue(str(0.0))
            self.enableControls()
            time.sleep(1)
            self.sendSharedData(None, False, False, False, 1, 1)
            self.plot_iter = 1
            self.Update()
        return

    def sendSharedData(
        self, data: dict | None, meas_running: bool, cancelled: bool, batch_mode: bool, batch_no: int, point_iter: int
    ) -> None:
        """Method to save data to the Shared Memory which is also accessed by the plot server for plotting.

        Parameters
        ----------
        data : dict | None
            The data dictionary for the plot.
        meas_running : bool
            Boolean indicating whether the measurement is currently running.
        cancelled : bool
            Boolean indicating whether the measurement was cancelled.
        batch_mode : bool
            Boolean indicating if the measurement is a batch measurement.
        batch_no : int
            Integer indicating the index of the batch measurement.
        point_iter : int
            Integer indicating the iteration point to control which point the plot server is updating.
        """
        if data is not None:
            self.share_mem_plot_data["fig"] = data
        self.share_mem_plot_data["run_status"] = meas_running
        self.share_mem_plot_data["iteration"] = point_iter
        self.share_mem_plot_data["cancelled"] = cancelled
        self.share_mem_plot_data["batch_details"] = dict(
            batch_type=batch_mode,
            batch_no=batch_no,
            batch_pass_no=self.batch_pass_no,
        )

    def startPlotServer(self, event: wx.Event | None) -> None:
        r"""Code to execute when the Restart Plot Server button is clicked.

        Parameters
        ----------
        event : wxEvent | None
            wxEVT_BUTTON event generated. None when the method if to be fired by other means.

        """
        self.plotView.Reload()
        self.plot_server_process = subprocess.Popen(
            ["start", "/MIN", "cmd", "/k", "python", os.getcwd() + "\\src\\dependencies\\plot_dash_client_copy.py"],
            shell=True,
        )
        # event.Skip()

    def enableControls(self) -> None:
        """Enable the controls in the UI."""
        self.modeSelect.Enable()
        self.startButton.Enable()
        self.excitationSelect.Enable()
        self.Update()

    def disableControls(self) -> None:
        """Disable the controls in the UI."""
        self.modeSelect.Disable()
        self.startButton.Disable()
        self.excitationSelect.Disable()
        self.Update()

    def interruptionClicked(self, event: wx.Event) -> None:
        """Handle the interruption of the measurement.

        Parameters
        ----------
        event : wxEvent
            wxEVT_BUTTON event generated.

        """
        self.meas_interrupted = True
        self.meas_running = False
        if event.GetId() == wx.ID_CANCEL:
            self.meas_interrupt_id = wx.ID_CANCEL
        else:
            self.meas_interrupt_id = wx.ID_STOP
        self.enableControls()
        event.Skip()

    def onClose(self, event) -> None:
        """Method fired when the close button is clicked.

        Parameters
        ----------
        event : wx.Event
            The close event that calls the function.

        """
        event.Skip()
        self.plot_server_process.terminate()

        self.share_mem_plot_data.shm.close()
        self.share_mem_plot_data.shm.unlink()
        self.plotView.Destroy()
        self.Destroy()
        app.ExitMainLoop()
        os._exit(0)


if __name__ == "__main__":
    frame = MainWindow(None)
    pywinstyles.apply_style(frame, "mica")
    frame.Show(True)
    frame.Centre()
    frame.SetFocus()
    app.MainLoop()
