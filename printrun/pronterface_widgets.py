# This file is part of the Printrun suite.
#
# Printrun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Printrun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Printrun.  If not, see <http://www.gnu.org/licenses/>.

import wx
import re

class MacroEditor(wx.Dialog):
    """Really simple editor to edit macro definitions"""

    def __init__(self, macro_name, definition, callback, gcode = False):
        self.indent_chars = "  "
        title = "  macro %s"
        if gcode:
            title = "  %s"
        self.gcode = gcode
        wx.Dialog.__init__(self, None, title = title % macro_name, style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.callback = callback
        self.panel = wx.Panel(self,-1)
        titlesizer = wx.BoxSizer(wx.HORIZONTAL)
        titletext = wx.StaticText(self.panel,-1, "              _")  #title%macro_name)
        #title.SetFont(wx.Font(11, wx.NORMAL, wx.NORMAL, wx.BOLD))
        titlesizer.Add(titletext, 1)
        self.findb = wx.Button(self.panel,  -1, _("Find"), style = wx.BU_EXACTFIT)  #New button for "Find" (Jezmy)
        self.findb.Bind(wx.EVT_BUTTON,  self.find)
        self.okb = wx.Button(self.panel, -1, _("Save"), style = wx.BU_EXACTFIT)
        self.okb.Bind(wx.EVT_BUTTON, self.save)
        self.Bind(wx.EVT_CLOSE, self.close)
        titlesizer.Add(self.findb)
        titlesizer.Add(self.okb)
        self.cancelb = wx.Button(self.panel, -1, _("Cancel"), style = wx.BU_EXACTFIT)
        self.cancelb.Bind(wx.EVT_BUTTON, self.close)
        titlesizer.Add(self.cancelb)
        topsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(titlesizer, 0, wx.EXPAND)
        self.e = wx.TextCtrl(self.panel, style = wx.HSCROLL|wx.TE_MULTILINE|wx.TE_RICH2, size = (400, 400))
        if not self.gcode:
            self.e.SetValue(self.unindent(definition))
        else:
            self.e.SetValue("\n".join(definition))
        topsizer.Add(self.e, 1, wx.ALL+wx.EXPAND)
        self.panel.SetSizer(topsizer)
        topsizer.Layout()
        topsizer.Fit(self)
        self.Show()
        self.e.SetFocus()

    def find(self, ev):
        # Ask user what to look for, find it and point at it ...  (Jezmy)
        S = self.e.GetStringSelection()
        if not S :
            S = "Z"
        FindValue = wx.GetTextFromUser('Please enter a search string:', caption = "Search", default_value = S, parent = None)
        somecode = self.e.GetValue()
        numLines = len(somecode)
        position = somecode.find(FindValue,  self.e.GetInsertionPoint())
        if position == -1 :
         #   ShowMessage(self,-1,  "Not found!")
            titletext = wx.TextCtrl(self.panel,-1, "Not Found!")
        else:
        # self.title.SetValue("Position : "+str(position))

            titletext = wx.TextCtrl(self.panel,-1, str(position))

            # ananswer = wx.MessageBox(str(numLines)+" Lines detected in file\n"+str(position), "OK")
            self.e.SetFocus()
            self.e.SetInsertionPoint(position)
            self.e.SetSelection(position,  position + len(FindValue))
            self.e.ShowPosition(position)

    def ShowMessage(self, ev , message):
        dlg = wxMessageDialog(self, message,
                              "Info!", wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def save(self, ev):
        self.Destroy()
        if not self.gcode:
            self.callback(self.reindent(self.e.GetValue()))
        else:
            self.callback(self.e.GetValue().split("\n"))

    def close(self, ev):
        self.Destroy()

    def unindent(self, text):
        self.indent_chars = text[:len(text)-len(text.lstrip())]
        if len(self.indent_chars) == 0:
            self.indent_chars = "  "
        unindented = ""
        lines = re.split(r"(?:\r\n?|\n)", text)
        #print lines
        if len(lines) <= 1:
            return text
        for line in lines:
            if line.startswith(self.indent_chars):
                unindented += line[len(self.indent_chars):] + "\n"
            else:
                unindented += line + "\n"
        return unindented
    def reindent(self, text):
        lines = re.split(r"(?:\r\n?|\n)", text)
        if len(lines) <= 1:
            return text
        reindented = ""
        for line in lines:
            if line.strip() != "":
                reindented += self.indent_chars + line + "\n"
        return reindented

class PronterOptionsDialog(wx.Dialog):
    """Options editor"""
    def __init__(self, pronterface):
        wx.Dialog.__init__(self, parent = None, title = _("Edit settings"), size = (400, 500), style = wx.DEFAULT_DIALOG_STYLE)
        panel = wx.Panel(self)
        header = wx.StaticBox(panel, label = _("Settings"))
        sbox = wx.StaticBoxSizer(header, wx.VERTICAL)
        panel2 = wx.Panel(panel)
        grid = wx.FlexGridSizer(rows = 0, cols = 2, hgap = 8, vgap = 2)
        grid.SetFlexibleDirection(wx.BOTH)
        grid.AddGrowableCol(1)
        grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        for setting in pronterface.settings._all_settings():
            grid.Add(setting.get_label(panel2), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT)
            grid.Add(setting.get_widget(panel2), 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        panel2.SetSizer(grid)
        sbox.Add(panel2, 1, wx.EXPAND)
        panel.SetSizer(sbox)
        topsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(panel, 1, wx.ALL | wx.EXPAND)
        topsizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALIGN_RIGHT)
        self.SetSizerAndFit(topsizer)
        self.SetMinSize(self.GetSize())
        #self.CentreOnScreen()

def PronterOptions(pronterface):
    dialog = PronterOptionsDialog(pronterface)
    if dialog.ShowModal() == wx.ID_OK:
        for setting in pronterface.settings._all_settings():
            old_value = setting.value
            setting.update()
            if setting.value != old_value:
                pronterface.set(setting.name, setting.value)
    dialog.Destroy()

class ButtonEdit(wx.Dialog):
    """Custom button edit dialog"""
    def __init__(self, pronterface):
        wx.Dialog.__init__(self, None, title = _("Custom button"), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.pronterface = pronterface
        topsizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(rows = 0, cols = 2, hgap = 4, vgap = 2)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self,-1, _("Button title")), 0, wx.BOTTOM|wx.RIGHT)
        self.name = wx.TextCtrl(self,-1, "")
        grid.Add(self.name, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, -1, _("Command")), 0, wx.BOTTOM|wx.RIGHT)
        self.command = wx.TextCtrl(self,-1, "")
        xbox = wx.BoxSizer(wx.HORIZONTAL)
        xbox.Add(self.command, 1, wx.EXPAND)
        self.command.Bind(wx.EVT_TEXT, self.macrob_enabler)
        self.macrob = wx.Button(self,-1, "..", style = wx.BU_EXACTFIT)
        self.macrob.Bind(wx.EVT_BUTTON, self.macrob_handler)
        xbox.Add(self.macrob, 0)
        grid.Add(xbox, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self,-1, _("Color")), 0, wx.BOTTOM|wx.RIGHT)
        self.color = wx.TextCtrl(self,-1, "")
        grid.Add(self.color, 1, wx.EXPAND)
        topsizer.Add(grid, 0, wx.EXPAND)
        topsizer.Add( (0, 0), 1)
        topsizer.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALIGN_CENTER)
        self.SetSizer(topsizer)

    def macrob_enabler(self, e):
        macro = self.command.GetValue()
        valid = False
        try:
            if macro == "":
                valid = True
            elif self.pronterface.macros.has_key(macro):
                valid = True
            elif hasattr(self.pronterface.__class__, u"do_"+macro):
                valid = False
            elif len([c for c in macro if not c.isalnum() and c != "_"]):
                valid = False
            else:
                valid = True
        except:
            if macro == "":
                valid = True
            elif self.pronterface.macros.has_key(macro):
                valid = True
            elif len([c for c in macro if not c.isalnum() and c != "_"]):
                valid = False
            else:
                valid = True
        self.macrob.Enable(valid)

    def macrob_handler(self, e):
        macro = self.command.GetValue()
        macro = self.pronterface.edit_macro(macro)
        self.command.SetValue(macro)
        if self.name.GetValue()=="":
            self.name.SetValue(macro)

class TempGauge(wx.Panel):

    def __init__(self, parent, size = (200, 22), title = "", maxval = 240, gaugeColour = None):
        wx.Panel.__init__(self, parent,-1, size = size)
        self.Bind(wx.EVT_PAINT, self.paint)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.width, self.height = size
        self.title = title
        self.max = maxval
        self.gaugeColour = gaugeColour
        self.value = 0
        self.setpoint = 0
        self.recalc()

    def recalc(self):
        mmax = max(int(self.setpoint*1.05), self.max)
        self.scale = float(self.width-2)/float(mmax)
        self.ypt = max(16, int(self.scale*max(self.setpoint, self.max/6)))

    def SetValue(self, value):
        self.value = value
        wx.CallAfter(self.Refresh)

    def SetTarget(self, value):
        self.setpoint = value
        wx.CallAfter(self.Refresh)

    def interpolatedColour(self, val, vmin, vmid, vmax, cmin, cmid, cmax):
        if val < vmin: return cmin
        if val > vmax: return cmax
        if val <= vmid:
            lo, hi, val, valhi = cmin, cmid, val-vmin, vmid-vmin
        else:
            lo, hi, val, valhi = cmid, cmax, val-vmid, vmax-vmid
        vv = float(val)/valhi
        rgb = lo.Red()+(hi.Red()-lo.Red())*vv, lo.Green()+(hi.Green()-lo.Green())*vv, lo.Blue()+(hi.Blue()-lo.Blue())*vv
        rgb = map(lambda x:x*0.8, rgb)
        return wx.Colour(*map(int, rgb))

    def paint(self, ev):
        self.width, self.height = self.GetClientSizeTuple()
        self.recalc()
        x0, y0, x1, y1, xE, yE = 1, 1, self.ypt+1, 1, self.width+1-2, 20
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush((255, 255, 255)))
        dc.Clear()
        cold, medium, hot = wx.Colour(0, 167, 223), wx.Colour(239, 233, 119), wx.Colour(210, 50.100)
        gauge1, gauge2 = wx.Colour(255, 255, 210), (self.gaugeColour or wx.Colour(234, 82, 0))
        shadow1, shadow2 = wx.Colour(110, 110, 110), wx.Colour(255, 255, 255)
        gc = wx.GraphicsContext.Create(dc)
        # draw shadow first
        # corners
        gc.SetBrush(gc.CreateRadialGradientBrush(xE-7, 9, xE-7, 9, 8, shadow1, shadow2))
        gc.DrawRectangle(xE-7, 1, 8, 8)
        gc.SetBrush(gc.CreateRadialGradientBrush(xE-7, 17, xE-7, 17, 8, shadow1, shadow2))
        gc.DrawRectangle(xE-7, 17, 8, 8)
        gc.SetBrush(gc.CreateRadialGradientBrush(x0+6, 17, x0+6, 17, 8, shadow1, shadow2))
        gc.DrawRectangle(0, 17, x0+6, 8)
        # edges
        gc.SetBrush(gc.CreateLinearGradientBrush(xE-6, 0, xE+1, 0, shadow1, shadow2))
        gc.DrawRectangle(xE-7, 9, 8, 8)
        gc.SetBrush(gc.CreateLinearGradientBrush(x0, yE-2, x0, yE+5, shadow1, shadow2))
        gc.DrawRectangle(x0+6, yE-2, xE-12, 7)
        # draw gauge background
        gc.SetBrush(gc.CreateLinearGradientBrush(x0, y0, x1+1, y1, cold, medium))
        gc.DrawRoundedRectangle(x0, y0, x1+4, yE, 6)
        gc.SetBrush(gc.CreateLinearGradientBrush(x1-2, y1, xE, y1, medium, hot))
        gc.DrawRoundedRectangle(x1-2, y1, xE-x1, yE, 6)
        # draw gauge
        width = 12
        w1 = y0+9-width/2
        w2 = w1+width
        value = x0+max(10, min(self.width+1-2, int(self.value*self.scale)))
        #gc.SetBrush(gc.CreateLinearGradientBrush(x0, y0+3, x0, y0+15, gauge1, gauge2))
        #gc.SetBrush(gc.CreateLinearGradientBrush(0, 3, 0, 15, wx.Colour(255, 255, 255), wx.Colour(255, 90, 32)))
        gc.SetBrush(gc.CreateLinearGradientBrush(x0, y0+3, x0, y0+15, gauge1, self.interpolatedColour(value, x0, x1, xE, cold, medium, hot)))
        val_path = gc.CreatePath()
        val_path.MoveToPoint(x0, w1)
        val_path.AddLineToPoint(value, w1)
        val_path.AddLineToPoint(value+2, w1+width/4)
        val_path.AddLineToPoint(value+2, w2-width/4)
        val_path.AddLineToPoint(value, w2)
        #val_path.AddLineToPoint(value-4, 10)
        val_path.AddLineToPoint(x0, w2)
        gc.DrawPath(val_path)
        # draw setpoint markers
        setpoint = x0+max(10, int(self.setpoint*self.scale))
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0))))
        setp_path = gc.CreatePath()
        setp_path.MoveToPoint(setpoint-4, y0)
        setp_path.AddLineToPoint(setpoint+4, y0)
        setp_path.AddLineToPoint(setpoint, y0+5)
        setp_path.MoveToPoint(setpoint-4, yE)
        setp_path.AddLineToPoint(setpoint+4, yE)
        setp_path.AddLineToPoint(setpoint, yE-5)
        gc.DrawPath(setp_path)
        # draw readout
        text = u"T\u00B0 %u/%u"%(self.value, self.setpoint)
        #gc.SetFont(gc.CreateFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.WHITE))
        #gc.DrawText(text, 29,-2)
        gc.SetFont(gc.CreateFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.WHITE))
        gc.DrawText(self.title, x0+19, y0+4)
        gc.DrawText(text,      x0+119, y0+4)
        gc.SetFont(gc.CreateFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)))
        gc.DrawText(self.title, x0+18, y0+3)
        gc.DrawText(text,      x0+118, y0+3)

class SpecialButton(object):

    label = None
    command = None
    background = None
    pos = None
    span = None
    tooltip = None
    custom = None

    def __init__(self, label, command, background = None, pos = None, span = None, tooltip = None, custom = False):
        self.label = label
        self.command = command
        self.pos = pos
        self.background = background
        self.span = span
        self.tooltip = tooltip
        self.custom = custom
