"""Initialize tkGUI Controller"""
import math
import threading
import time
import datetime as dt

import tkinter as tk

from ..base import Controller as _Controller

from ...config import config, Mode

from ...utils import dialog
from ...utils.time import strfmt_td
from ...utils.monitor import Memory

from ...model.model import Model
from ...model.reader import Format
from ...view.tkGUI.base import View as GUI

from ...backend.mpl.plot import BlitPlot
from ...backend.tk import theme as theme_tk

from .plot_base import FreqPlotController

def define_args(parser):
    ctrl = parser.add_argument_group("tkGUI")
    ctrl.add_argument("--theme", default="Dark", choices=[k for k in theme_tk.theme.keys()])
    ctrl.add_argument("--sweep", default=50.0, type=float)
    ctrl.add_argument("--show", default=50.0, type=float)
    return ctrl

class Controller(_Controller):
    """tkGUI Controller"""
    def __init__(self, model: Model, view: GUI, **kwargs):
        super().__init__(model, view)
        self.view: GUI = self.view # type hints
        self.running = False
        self._stop = False
        self.time_show = kwargs.get("show", 50.0)
        self.nfft_exp = int(math.log2(self.model.nfft))
        self.model.set_sweep_time(kwargs.get("sweep", 50.0))
        self._last_f = None
        self.plot: FreqPlotController = None # type: ignore

        self.view.sld_samp.scale.config(from_=0, to=self.model.reader.max_samp) # resolution=self.model.block_size
        self.view.sld_samp.scale.config(command=self.handle_sld_samp)

        self.view.ent_sweep.bind("<Return>", self.handle_event)
        self.view.var_sweep.set(f"{self.model.sweep_time:02.3f}")
        self.view.ent_show.bind("<Return>", self.handle_event)
        self.view.var_show.set(f"{self.time_show:02.3f}")

        self.view.btn_prev.config(command=self.prev)
        self.view.btn_next.config(command=self.next)
        self.view.btn_start.config(command=self.start)
        self.view.btn_stop.config(command=self.stop)
        self.view.btn_reset.config(command=self.reset)
        self.view.var_draw_time.set(f"{0.0:06.3f}s")

        self.view.btn_file.config(command=self.handle_btn_file)
        self.view.cb_file_fmt.config(values=list([v.name for v in Format]))
        self.view.cb_file_fmt.bind("<<ComboboxSelected>>", self.handle_event)
        self.view.ent_fs.bind("<Return>", self.handle_event)
        self.view.ent_cf.bind("<Return>", self.handle_event)
        self.view.ent_nfft_exp.bind("<Return>", self.handle_event)

        self.thread: threading.Thread = None # type: ignore

        style = kwargs.get("theme", "Dark")

        theme_tk.get(style)(self.view.root) # pyright: ignore[reportCallIssue]

    def start(self):
        if self.running:
            return
        if self.model.reader.path is None:
            return
        self.running = True
        self.view.btn_start.config(state=tk.DISABLED)
        self.view.btn_stop.config(state=tk.ACTIVE)
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def stop(self):
        if not self._stop and not self.running:
            return
        self.running = False
        self.view.btn_stop.config(state=tk.DISABLED)
        self.view.btn_start.config(state=tk.ACTIVE)
        self.thread.join(timeout=0.2)

    def reset(self):
        self.stop()
        self.model.reset()
        self.plot.reset()
        self.draw_tb()

    def prev(self):
        self.stop()
        return self._prev()

    def next(self):
        self.stop()
        return self._next()

    def loop(self):
        while self.running:
            time_show = self.time_show/1000 # convert ms to s
            valid, ptime = self._next()
            if not valid or ptime is None:
                break
            wait = time_show-ptime
            if wait > 0:
                self.view.lbl_msg.configure(text="")
                time.sleep(wait)
            else:
                self.model.skip_time(-wait)
                self.view.lbl_msg.configure(text="OVERFLOW")

    def _plot(self):
        if config.MON_MEM:
            Memory().peak()
        ptime = time.perf_counter()
        if isinstance(self.plot, FreqPlotController):
            vbw = self.plot.vbw
            window = self.plot.window
            if not isinstance(self.view.plot.plotter, BlitPlot):
                self.view.plot.plotter.cla()
                print("Cleared plot!")
            self._check_f()
            self.plot.plot(self.model.f, self.model.psd(vbw, window))
            # self.plot.update()

        ptime = (time.perf_counter() - ptime)
        self.view.var_draw_time.set(f"{ptime:06.3f}s")
        self.draw_tb()
        # print(f"Plotted in {ptime*1000:.1f}ms / {self.time_show}")
        return ptime

    def _check_f(self):
        def _update_f():
            return (self.model.f[0], self.model.f[-1]+(self.model.f[-1]-self.model.f[-2]), len(self.model.f))
        if self._last_f is None:
            self._last_f = _update_f()
            self.plot.update_f(self._last_f)
        elif not self.model.f[0] == self._last_f[0] and not len(self.model.f) == self._last_f[2]:
            self._last_f = _update_f()
            self.plot.update_f(self._last_f)

    def _prev(self):
        valid = self.model.prev()
        tplot = None
        if valid:
            tplot = self._plot()
        return (valid, tplot)

    def _next(self):
        valid = self.model.next()
        tplot = None
        if valid:
            tplot = self._plot()
        return (valid, tplot)

    def draw(self):
        self.draw_tb()
        self.draw_ctrl()
        self.draw_view()

    def draw_tb(self):
        self.view.var_samp.set(self.model.reader.cur_samp)

        self.view.var_time_cur.set(strfmt_td(dt.timedelta(seconds=self.model.cur_time())))
        self.view.var_time_tot.set(strfmt_td(dt.timedelta(seconds=self.model.tot_time())))

        self.view.var_sweep.set(f"{self.model.sweep_time:02.3f}")
        self.view.var_show.set(f"{self.time_show:02.3f}")

    def draw_ctrl(self):
        self.view.var_file.set(str(self.model.reader.path))
        self.view.var_file_fmt.set(str(self.model.reader.fmt.name))

        self.view.var_fs.set(str(self.model.Fs))
        self.view.var_cf.set(str(self.model.cf))
        self.view.lbl_nfft.configure(text=str(self.model.nfft))
        self.view.var_nfft_exp.set(str(self.nfft_exp))

        self.view.lbl_block_size.configure(text=str(self.model.block_size))
        self.view.lbl_sweep_samples.configure(text=str(self.model.sweep_samples()))

    def draw_view(self):
        pass

    # --- GUI bind events and setters --- #
    def handle_event(self, event):
        if event.widget == self.view.ent_sweep:
            self.set_time_sweep(self.view.var_sweep.get())
        elif event.widget == self.view.ent_show:
            self.set_time_show(self.view.var_show.get())
        elif event.widget == self.view.cb_file_fmt:
            self.set_dtype(self.view.var_file_fmt.get())
        elif event.widget == self.view.ent_fs:
            self.set_fs(self.view.var_fs.get())
        elif event.widget == self.view.ent_cf:
            self.set_cf(self.view.var_cf.get())
        elif event.widget == self.view.ent_nfft_exp:
            self.set_nfft(self.view.var_nfft_exp.get())

    def handle_btn_file(self):
        self.set_path(dialog.get_file(False))

    def handle_sld_samp(self, *args):
        self.set_samp(self.view.var_samp.get())

    def set_samp(self, samp):
        self.stop()
        self.model.reader.cur_samp = samp
        self.draw_tb()
        # print(samp)
    def set_time_sweep(self, ts):
        try:
            self.model.set_sweep_time(float(ts))
        except ValueError:
            pass
        self.view.var_sweep.set(f"{self.model.sweep_time:02.3f}")
        self.draw_ctrl()
    def set_time_show(self, ts):
        try:
            ts = float(ts)
            self.time_show = ts
        except ValueError:
            pass
        self.view.var_show.set(f"{self.time_show:02.3f}")
    def set_path(self, path):
        self.model.reader.path = path
        print(f"Path set to '{self.model.reader.path}'")
        self.view.sld_samp.scale.config(from_=0, to=self.model.reader.max_samp) # resolution=self.model.block_size
        self.draw_tb()
        self.draw_ctrl()
    def set_dtype(self, dtype):
        self.model.reader.fmt = dtype
        self.draw_tb()
        self.draw_ctrl()
    def set_fs(self, fs):
        self.model.Fs = fs
        self.view.var_fs.set(str(self.model.Fs))
        self.draw_tb()
        self.draw_ctrl()
    def set_cf(self, cf):
        self.model.cf = cf
        self.view.var_cf.set(str(self.model.cf))
        self.draw_ctrl()

    def set_nfft(self, exp):
        exp = int(exp)
        self.nfft_exp = exp
        self.model.nfft = 2**exp
        self.view.var_nfft_exp.set(str(self.nfft_exp))
        self.view.lbl_nfft.config(text=str(self.model.nfft))
        self.plot.update_nfft(self.model.nfft)
        self.draw_ctrl()
