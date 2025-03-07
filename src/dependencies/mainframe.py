###############################################################################
# Code generated by wxUiEditor -- see https://github.com/KeyWorksRW/wxUiEditor/
#
# Do not edit any code above the "End of generated code" comment block.
# Any changes before that block will be lost if it is re-generated!
###############################################################################

"""mainFrame class generated by wxUiEditor."""

import wx
import wx.adv
import wx.grid
import wx.html2

class mainFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=
                wx.DefaultPosition, size=wx.Size(1000, 800),
                style=wx.DEFAULT_FRAME_STYLE|wx.CLOSE_BOX|wx.MAXIMIZE_BOX|
                wx.MINIMIZE_BOX|wx.FULL_REPAINT_ON_RESIZE,
                name=wx.FrameNameStr):
        wx.Frame.__init__(self)

        if not self.Create(parent, id, title, pos, size, style, name):
            return
        self.SetMinSize(wx.Size(800, 600))

        self.toolBar = self.CreateToolBar()
        self.toolBar.Realize()

        self.menubar = wx.MenuBar()

        self.SetMenuBar(self.menubar)

        self.statusBar = self.CreateStatusBar()

        panel2 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.TAB_TRAVERSAL)

        flex_grid_sizer = wx.FlexGridSizer(2, 0, 0)
        flex_grid_sizer.AddGrowableCol(1)

        flex_grid_sizer4 = wx.FlexGridSizer(10, 0, 0, 0)

        self.modeSelect = wx.Notebook(panel2, wx.ID_ANY)
        flex_grid_sizer4.Add(self.modeSelect, wx.SizerFlags().Expand().Border(wx.ALL))

        single_scan = wx.Panel(self.modeSelect, wx.ID_ANY, wx.DefaultPosition,
            wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.modeSelect.AddPage(single_scan, "Single Scan", True)
        single_scan.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        static_box = wx.StaticBoxSizer(wx.VERTICAL, single_scan, "Measurement Parameters")

        flex_grid_sizer2 = wx.FlexGridSizer(2, 0, 0)

        self.static_text = wx.StaticText(static_box.GetStaticBox(), wx.ID_ANY,
            "Start [eV] : ")
        flex_grid_sizer2.Add(self.static_text,
            wx.SizerFlags().Right().Border(wx.LEFT|wx.RIGHT|wx.TOP, 10))

        self.singleStarteV = wx.SpinCtrlDouble(static_box.GetStaticBox(), wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1500, 0,
            0.005)
        flex_grid_sizer2.Add(self.singleStarteV, wx.SizerFlags().Border(wx.ALL))

        self.static_text2 = wx.StaticText(static_box.GetStaticBox(), wx.ID_ANY,
            "End [eV] : ")
        flex_grid_sizer2.Add(self.static_text2,
            wx.SizerFlags().Right().Border(wx.LEFT|wx.RIGHT|wx.TOP, 10))

        self.singleEndeV = wx.SpinCtrlDouble(static_box.GetStaticBox(), wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1500, 0,
            0.005)
        flex_grid_sizer2.Add(self.singleEndeV, wx.SizerFlags().Border(wx.ALL))

        self.static_text3 = wx.StaticText(static_box.GetStaticBox(), wx.ID_ANY,
            "Step width [eV] : ")
        flex_grid_sizer2.Add(self.static_text3,
            wx.SizerFlags().Right().Border(wx.LEFT|wx.RIGHT|wx.TOP, 10))

        self.singleStepWidtheV = wx.SpinCtrlDouble(static_box.GetStaticBox(), wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0.005, 1500,
            0.005, 0.005)
        flex_grid_sizer2.Add(self.singleStepWidtheV, wx.SizerFlags().Border(wx.ALL))

        self.static_text4 = wx.StaticText(static_box.GetStaticBox(), wx.ID_ANY,
            "Time per step [s] : ")
        flex_grid_sizer2.Add(self.static_text4,
            wx.SizerFlags().Right().Border(wx.LEFT|wx.RIGHT|wx.TOP, 10))

        self.singleTimePerStep = wx.SpinCtrlDouble(static_box.GetStaticBox(), wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000, 1,
            1)
        flex_grid_sizer2.Add(self.singleTimePerStep, wx.SizerFlags().Border(wx.ALL))

        self.static_text5 = wx.StaticText(static_box.GetStaticBox(), wx.ID_ANY,
            "No. of passes : ")
        flex_grid_sizer2.Add(self.static_text5,
            wx.SizerFlags().Right().Border(wx.LEFT|wx.RIGHT|wx.TOP, 10))

        self.singlePasses = wx.SpinCtrl(static_box.GetStaticBox(), wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 100, 1)
        flex_grid_sizer2.Add(self.singlePasses, wx.SizerFlags().Border(wx.ALL))

        static_box.Add(flex_grid_sizer2, wx.SizerFlags().Expand().Border(wx.ALL))
        single_scan.SetSizerAndFit(static_box)

        batch_scan = wx.Panel(self.modeSelect, wx.ID_ANY, wx.DefaultPosition,
            wx.DefaultSize, wx.TAB_TRAVERSAL|wx.ALWAYS_SHOW_SB)
        self.modeSelect.AddPage(batch_scan, "Batch Scan")
        batch_scan.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        static_box3 = wx.StaticBoxSizer(wx.VERTICAL, batch_scan, "Measurement Parameters")

        flex_grid_sizer3 = wx.FlexGridSizer(1, 0, 0)

        self.batchInput = wx.grid.Grid(static_box3.GetStaticBox(), wx.ID_ANY,
            wx.DefaultPosition, wx.Size(-1, 100))
        self.batchInput.CreateGrid(100, 5)
        self.batchInput.EnableDragGridSize(False)
        self.batchInput.SetMargins(0, 0)
        self.batchInput.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.batchInput.SetDefaultColSize(60)
        self.batchInput.EnableDragColSize(False)
        self.batchInput.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.batchInput.SetColLabelSize(40)
        self.batchInput.SetColLabelValue(0, "Start [eV]")
        self.batchInput.SetColLabelValue(1, "End [eV]")
        self.batchInput.SetColLabelValue(2, "Step [eV]")
        self.batchInput.SetColLabelValue(3, "s/eV")
        self.batchInput.SetColLabelValue(4, "Passes")

        self.batchInput.EnableDragRowSize(False)
        self.batchInput.SetRowLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.batchInput.SetRowLabelSize(20)
        flex_grid_sizer3.Add(self.batchInput, wx.SizerFlags().Expand().Border(wx.ALL))

        static_box3.Add(flex_grid_sizer3, wx.SizerFlags().Expand().Border(wx.ALL))
        batch_scan.SetSizerAndFit(static_box3)

        box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.static_text13 = wx.StaticText(panel2, wx.ID_ANY, "Excitation")
        box_sizer.Add(self.static_text13,
            wx.SizerFlags().Center().Border(wx.LEFT|wx.RIGHT|wx.TOP, wx.SizerFlags.GetDefaultBorder()))

        flex_grid_sizer5 = wx.FlexGridSizer(3, 0, 0)

        self.static_text11 = wx.StaticText(panel2, wx.ID_ANY, "Al")
        flex_grid_sizer5.Add(self.static_text11,
            wx.SizerFlags().CenterVertical().Border(wx.LEFT|wx.RIGHT|wx.BOTTOM, wx.SizerFlags.GetDefaultBorder()))

        self.excitationSelect = wx.Slider(panel2, wx.ID_ANY, 0, 0, 1)
        self.excitationSelect.SetValue(0)
        self.excitationSelect.SetLineSize(10)
        flex_grid_sizer5.Add(self.excitationSelect,
            wx.SizerFlags().CenterHorizontal().Border(wx.LEFT|wx.RIGHT|wx.BOTTOM, wx.SizerFlags.GetDefaultBorder()))

        self.static_text12 = wx.StaticText(panel2, wx.ID_ANY, "Mg")
        flex_grid_sizer5.Add(self.static_text12,
            wx.SizerFlags().CenterVertical().Border(wx.LEFT|wx.RIGHT|wx.BOTTOM, wx.SizerFlags.GetDefaultBorder()))

        box_sizer.Add(flex_grid_sizer5,
        wx.SizerFlags().Center().Border(wx.LEFT|wx.RIGHT|wx.BOTTOM, wx.SizerFlags.GetDefaultBorder()))

        box_sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.startButton = wx.Button(panel2, wx.ID_ANY, "Start")
        box_sizer2.Add(self.startButton, wx.SizerFlags().Border(wx.ALL))

        self.cancelButton = wx.Button(panel2, wx.ID_CANCEL, "Cancel")
        box_sizer2.Add(self.cancelButton, wx.SizerFlags().Border(wx.ALL))

        box_sizer.Add(box_sizer2, wx.SizerFlags().Center().Border(wx.ALL))

        self.stopButton = wx.Button(panel2, wx.ID_STOP, "Stop")
        box_sizer.Add(self.stopButton, wx.SizerFlags().Center().Border(wx.ALL))

        flex_grid_sizer4.Add(box_sizer, wx.SizerFlags().Expand().Border(wx.ALL))

        static_line2 = wx.StaticLine(panel2, wx.ID_ANY, wx.DefaultPosition,
            wx.Size(20, -1), wx.LI_HORIZONTAL)
        flex_grid_sizer4.Add(static_line2, wx.SizerFlags().Expand().Border(wx.ALL))

        self.measProgress = wx.Gauge(panel2, wx.ID_ANY, 100, wx.DefaultPosition,
            wx.DefaultSize, wx.GA_SMOOTH)
        self.measProgress.SetValue(0)
        self.measProgress.SetMinSize(wx.Size(150, -1))
        flex_grid_sizer4.Add(self.measProgress, wx.SizerFlags().Expand().Border(wx.ALL))

        box_sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        box_sizer4 = wx.BoxSizer(wx.VERTICAL)

        self.static_text6 = wx.StaticText(panel2, wx.ID_ANY, "K.E [eV]")
        box_sizer4.Add(self.static_text6, wx.SizerFlags().Center().Border(wx.ALL))

        self.kineticEnergy = wx.TextCtrl(panel2, wx.ID_ANY, "", wx.DefaultPosition,
            wx.DefaultSize, wx.TE_READONLY|wx.TE_CENTER)
        self.kineticEnergy.SetMinSize(wx.Size(60, -1))
        self.kineticEnergy.SetMaxSize(wx.Size(60, -1))
        box_sizer4.Add(self.kineticEnergy, wx.SizerFlags().Center().Border(wx.ALL))

        box_sizer3.Add(box_sizer4, wx.SizerFlags().Border(wx.ALL))

        box_sizer5 = wx.BoxSizer(wx.VERTICAL)

        self.static_text7 = wx.StaticText(panel2, wx.ID_ANY, "B.E [eV]")
        box_sizer5.Add(self.static_text7, wx.SizerFlags().Center().Border(wx.ALL))

        self.bindingEnergy = wx.TextCtrl(panel2, wx.ID_ANY, "", wx.DefaultPosition,
            wx.DefaultSize, wx.TE_READONLY|wx.TE_CENTER)
        self.bindingEnergy.SetMinSize(wx.Size(60, -1))
        self.bindingEnergy.SetMaxSize(wx.Size(60, -1))
        box_sizer5.Add(self.bindingEnergy, wx.SizerFlags().Center().Border(wx.ALL))

        box_sizer3.Add(box_sizer5, wx.SizerFlags().Border(wx.ALL))

        box_sizer6 = wx.BoxSizer(wx.VERTICAL)

        self.static_text8 = wx.StaticText(panel2, wx.ID_ANY, "Elapsed [min]")
        box_sizer6.Add(self.static_text8, wx.SizerFlags().Center().Border(wx.ALL))

        self.elapsedTime = wx.TextCtrl(panel2, wx.ID_ANY, "", wx.DefaultPosition,
            wx.DefaultSize, wx.TE_READONLY|wx.TE_CENTER)
        self.elapsedTime.SetMinSize(wx.Size(60, -1))
        self.elapsedTime.SetMaxSize(wx.Size(60, -1))
        box_sizer6.Add(self.elapsedTime, wx.SizerFlags().Center().Border(wx.ALL))

        box_sizer3.Add(box_sizer6, wx.SizerFlags().Border(wx.ALL))

        box_sizer7 = wx.BoxSizer(wx.VERTICAL)

        self.static_text9 = wx.StaticText(panel2, wx.ID_ANY, "Remaining [min]")
        box_sizer7.Add(self.static_text9, wx.SizerFlags().Center().Border(wx.ALL))

        self.remainingTime = wx.TextCtrl(panel2, wx.ID_ANY, "", wx.DefaultPosition,
            wx.DefaultSize, wx.TE_READONLY|wx.TE_CENTER)
        self.remainingTime.SetMinSize(wx.Size(60, -1))
        self.remainingTime.SetMaxSize(wx.Size(60, -1))
        box_sizer7.Add(self.remainingTime, wx.SizerFlags().Center().Border(wx.ALL))

        box_sizer3.Add(box_sizer7, wx.SizerFlags().Border(wx.ALL))

        flex_grid_sizer4.Add(box_sizer3,
        wx.SizerFlags().CenterHorizontal().Border(wx.ALL))

        static_line3 = wx.StaticLine(panel2, wx.ID_ANY, wx.DefaultPosition,
            wx.Size(20, -1), wx.LI_HORIZONTAL)
        flex_grid_sizer4.Add(static_line3, wx.SizerFlags().Expand().Border(wx.ALL))

        self.measurementStatus = wx.StaticText(panel2, wx.ID_ANY, "Welcome")
        flex_grid_sizer4.Add(self.measurementStatus,
            wx.SizerFlags().CenterHorizontal().Border(wx.ALL))

        self.btn = wx.adv.CommandLinkButton(panel2, wx.ID_ANY, "Restart Plot Server",
            "In case the backend plot server has stopped")
        flex_grid_sizer4.Add(self.btn, wx.SizerFlags().Border(wx.ALL))

        flex_grid_sizer.Add(flex_grid_sizer4, wx.SizerFlags().Expand().Border(wx.ALL))

        flex_grid_sizer6 = wx.FlexGridSizer(1, 1, 0, 0)
        flex_grid_sizer6.AddGrowableCol(0)
        flex_grid_sizer6.AddGrowableRow(0)

        self.plotView = wx.html2.WebView.New(panel2, wx.ID_ANY, "")
        self.plotView.SetMinSize(wx.Size(-1, 600))
        flex_grid_sizer6.Add(self.plotView, wx.SizerFlags(1).Expand().Border(wx.ALL))

        flex_grid_sizer.Add(flex_grid_sizer6, wx.SizerFlags().Expand().Border(wx.ALL))
        panel2.SetSizerAndFit(flex_grid_sizer)

        self.Centre(wx.BOTH)

        # Bind Event handlers
        self.cancelButton.Bind(wx.EVT_BUTTON, self.interruptionClicked)
        self.stopButton.Bind(wx.EVT_BUTTON, self.interruptionClicked)
        self.startButton.Bind(wx.EVT_BUTTON, self.startMeasurement)
        self.btn.Bind(wx.EVT_BUTTON, self.startPlotServer)
        self.batchInput.Bind(wx.EVT_CHAR, self.myNumValid)

    # Unimplemented Event handler functions
    # Copy any listed and paste them below the comment block, or to your inherited class.
    """
    def interruptionClicked(self, event):
        event.Skip()

    def myNumValid(self, event):
        event.Skip()

    def startMeasurement(self, event):
        event.Skip()

    def startPlotServer(self, event):
        event.Skip()

    """

# ************* End of generated code ***********
# DO NOT EDIT THIS COMMENT BLOCK!
#
# Code below this comment block will be preserved
# if the code for this class is re-generated.
# ***********************************************

    def myNumValid(self, event: wx.KeyEvent):
        r"""Method called when a key is pressed.

        This method enables only numeric values to be entered in the grid. When non-numeric values are entered,
        the character is blocked from being entered. The method also checks if the :kbd:`TAB` key is pressed to
        enable tab navigation between the cells in the grid.

            Parameters
            ----------
            event : wxEvent
                wxEVT_CHAR event generated when a character key on the keyboard is pressed.

        """

        key = event.GetKeyCode()
        if chr(key) in "0123456789.":
            event.Skip()
        elif not (chr(key).isalpha() or chr(key) in "+*/\\][';/,`=") and event.GetModifiers() != wx.MOD_SHIFT:
            event.Skip()
        elif key == wx.WXK_TAB and event.GetModifiers() == wx.MOD_SHIFT:
            event.Skip()
