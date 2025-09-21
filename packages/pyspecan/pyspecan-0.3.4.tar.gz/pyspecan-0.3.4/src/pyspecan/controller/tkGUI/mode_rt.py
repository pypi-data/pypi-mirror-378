"""Controller for RT mode"""
import argparse
import time

import numpy as np

from ...utils import matrix
from ...backend.mpl.color import cmap

from ...view.tkGUI.mode_rt import ViewRT, PlotRT

from .base import Controller
from .base import define_args as base_args
from .plot_base import define_args as freq_args

from .plot_base import FreqPlotController

def args_rt(parser: argparse.ArgumentParser):
    ctrl = base_args(parser)
    freq_args(parser)
    mode = ctrl.add_argument_group("RT mode")
    mode.add_argument("--x", default=1001, type=int, help="histogram x pixels")
    mode.add_argument("--y", default=600, type=int, help="histogram y pixels")
    mode.add_argument("--cmap", default="hot", choices=[k for k in cmap.keys()], help="histogram color map")

class ControllerRT(Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = PlotControllerRT(self, self.view.plot, **kwargs)
        self.draw()


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
                # self.model.skip_time(-wait)
                self.view.lbl_msg.configure(text="OVERFLOW")

class PlotControllerRT(FreqPlotController):
    """Controller for ViewRT"""
    __slots__ = (
        "x", "y", "cmap",
        "_cmap_set", "_cb_drawn"
    )
    def __init__(self, parent, view, **kwargs):
        self.x = kwargs.get("x", 1001)
        self.y = kwargs.get("y", 600)
        self.cmap = kwargs.get("cmap", "hot")
        super().__init__(parent, view, **kwargs)
        # self.view: viewPSD = self.view # type hint
        self._cmap_set = False
        self._cb_drawn = False

        self.view.settings["overlap"].set(f"{self.parent.model.overlap:.2f}")
        self.view.wg_sets["overlap"].bind("<Return>", self.handle_event)

        self.view.settings["cmap"].set(self.cmap)
        self.view.wg_sets["cmap"].configure(values=[k for k in cmap.keys()])
        self.view.wg_sets["cmap"].bind("<<ComboboxSelected>>", self.handle_event)

        self.view.ax("pst").ax.set_autoscale_on(False)
        self.view.ax("pst").ax.locator_params(axis="x", nbins=5)
        self.view.ax("pst").ax.locator_params(axis="y", nbins=10)
        self.view.ax("pst").ax.grid(True, alpha=0.2)

        self.set_y()

    def update_f(self, f):
        fmin, fmax, fnum = f
        x_mul = [0.0,0.25,0.5,0.75,1.0]

        x_tick = [self.x*m for m in x_mul]
        x_text = [f"{m-self.x/2:.1f}" for m in x_tick]
        self.view.ax("pst").ax.set_xticks(x_tick, x_text)
        self.view.ax("pst").set_xlim(0, self.x)

    def set_y(self):
        """Set plot yticks and ylabels"""
        y_mul = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
        y_max = self.y_top
        y_min = self.y_btm
        y_rng = abs(abs(y_max) - abs(y_min))
        y_off = y_min if y_min < 0 else -y_min

        y_tick = [self.y*m for m in y_mul]
        y_text = [f"{(y_rng*m)+y_off:.1f}" for m in y_mul]
        self.view.ax("pst").ax.set_yticks(y_tick, y_text)
        self.view.ax("pst").set_ylim(0, self.y)

    def plot(self, freq, psd):
        self._plot_persistent(psd)

        self._show_y_location(psd)
        self.update()

    def _plot_persistent(self, psds):
        self.view.ax("pst").ax.set_title(f"Persistent - {psds.shape[1]} FFTs")
        mat = matrix.cvec(self.x, self.y, psds, self.y_top, self.y_btm)
        mat = mat / np.max(mat)

        im = self.view.ax("pst").imshow(
                mat, name="mat", cmap=cmap[self.cmap],
                vmin=0, vmax=1,
                aspect="auto",
                interpolation="nearest", resample=False, rasterized=True
        )

        if not self._cb_drawn:
            # print("Adding colorbar")
            cb = self.view.plotter.fig.colorbar(
                im, ax=self.view.ax("pst").ax, # type: ignore
                pad=0.005, fraction=0.05
            )
            self.view.plotter.canvas.draw()
            self._cb_drawn = True

        if self._cmap_set:
            self.view.ax("pst").set_ylim(0, self.y)
            self._cmap_set = False

    # --- GUI bind events and setters --- #
    def handle_event(self, event):
        if event.widget == self.view.wg_sets["cmap"]:
            self.set_cmap(self.view.settings["cmap"].get())
        elif event.widget == self.view.wg_sets["overlap"]:
            self.set_overlap(self.view.settings["overlap"].get())
        else:
            super().handle_event(event)

    def set_scale(self, scale):
        prev = self.scale
        super().set_scale(scale)
        if not prev == self.scale:
            self.set_y()
    def set_ref_level(self, ref):
        prev = self.ref_level
        super().set_ref_level(ref)
        if not prev == self.ref_level:
            self.set_y()
    def set_cmap(self, _cmap):
        """Set plot color mapping"""
        self.cmap = _cmap
        self._cmap_set = True

    def set_overlap(self, overlap):
        try:
            overlap = float(overlap)
            self.parent.model.overlap = overlap
        except ValueError:
            ref = self.ref_level
        self.view.settings["ref_level"].set(f"{self.parent.model.overlap:.2f}")
