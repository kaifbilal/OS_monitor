from tkinter import *
import random
import math
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BG = "#191919"
FG = "#ffffff"
FG_DIM = "#aaaaaa"
MAX_POINTS = 60
UPDATE_MS = 1000
Y_MIN = 0
Y_MAX = 100

# Chart palette and grid settings
CHART_BG = "#191919"
CHART_FIG_BG = "#0b1712"
CHART_LINE_COLOR = "#7bd88f"
CHART_FILL_COLOR = "#7bd88f"
CHART_DOT_COLOR = "#c9f8d5"
CHART_GRID_COLOR = "#ffffff"
CHART_BORDER_COLOR = "#ffffff"
CHART_GRID_BOXES_X = 15
CHART_GRID_BOXES_Y = 10
CHART_LINE_WIDTH = 1.25
CHART_BORDER_WIDTH = 0.8



class Chart:
    def __init__(self, parent):
        self.parent = parent
        self.title = "Chart"
        self.geometry = "400x300"
        
        # Fixed x-axis positions: left=0 ... right=59
        self.x_data = list(range(MAX_POINTS))

        # Pre-fill with NaN so window is always length 60 from the start.
        # New values are appended on the right; oldest values disappear on the left.
        self.y_data = deque([math.nan] * MAX_POINTS, maxlen=MAX_POINTS)

        self.container = Frame(self.parent, bg=BG)
        self.container.pack(fill=BOTH, expand=True)
        self.frm0 = Frame(self.container, bg=BG)
        self.frm0.pack(side=TOP, fill=X, padx=8, pady=(4, 0))
        self.top_left = Label(self.frm0, text="% Utilization", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.top_right = Label(self.frm0, text="100%", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.top_left.pack(side=LEFT)
        self.top_right.pack(side=TOP, anchor=E)

        self.frm1 = Frame(self.container, bg=BG)
        self.frm1.pack(fill=BOTH, expand=True)
        self.chart = Frame(self.frm1, bg=BG)
        self.chart.pack(fill=BOTH, expand=True)

        self.frm2 = Frame(self.container, bg=BG)
        self.frm2.pack(side=BOTTOM, fill=X, padx=8, pady=(0, 4))
        self.bottom_left = Label(self.frm2, text="60 seconds", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.bottom_right = Label(self.frm2, text="0", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.bottom_left.pack(side=LEFT)
        self.bottom_right.pack(side=RIGHT)

        self._init_plot()

        self._after_id = None
        self._closed = False
        self._pending_value = None
        self.container.bind("<Destroy>", self._on_destroy, add="+")

        self.start()

    def _init_plot(self):
        self.fig = Figure(figsize=(7.4, 3.8), dpi=100)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor(CHART_FIG_BG)
        self.ax.set_facecolor(CHART_BG)

        self.ax.set_xlim(0, MAX_POINTS - 1)
        self.ax.set_ylim(Y_MIN, Y_MAX)

        # Grid is driven by ticks, but labels/tick marks are hidden.
        x_step = (MAX_POINTS - 1) / CHART_GRID_BOXES_X
        y_step = (Y_MAX - Y_MIN) / CHART_GRID_BOXES_Y
        self.ax.set_xticks([i * x_step for i in range(CHART_GRID_BOXES_X + 1)])
        self.ax.set_yticks([Y_MIN + i * y_step for i in range(CHART_GRID_BOXES_Y + 1)])
        self.ax.grid(which="major", color=CHART_GRID_COLOR, alpha=0.18, linewidth=0.6)
        self.ax.tick_params(axis="both", which="both", length=0, labelbottom=False, labelleft=False)
        self.ax.margins(x=0, y=0)

        for spine in self.ax.spines.values():
            spine.set_visible(True)
            spine.set_color(CHART_BORDER_COLOR)
            spine.set_linewidth(CHART_BORDER_WIDTH)
            spine.set_alpha(0.55)

        (self.line,) = self.ax.plot(
            self.x_data,
            list(self.y_data),
            linewidth=CHART_LINE_WIDTH,
            color=CHART_LINE_COLOR,
        )
        self.fill_poly = None
        (self.dot,) = self.ax.plot([], [], marker="o", markersize=4, color=CHART_DOT_COLOR)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=0, pady=0)

    def get_next_value(self):
        if self._pending_value is not None:
            value = self._pending_value
            self._pending_value = None
            return value
        return random.uniform(0, 99)

    def set_latest_value(self, value):
        self._pending_value = value

    def sanitize_value(self, value):
        try:
            v = float(value)
        except (TypeError, ValueError):
            return math.nan

        if not math.isfinite(v):
            return math.nan

        return max(float(Y_MIN), min(float(Y_MAX), v))

    def _refresh_series(self, value):
        self.y_data.append(value)
        y_list = list(self.y_data)
        self.line.set_data(self.x_data, y_list)

        if self.fill_poly is not None:
            self.fill_poly.remove()
            self.fill_poly = None

        finite_mask = [math.isfinite(v) for v in y_list]
        self.fill_poly = self.ax.fill_between(
            self.x_data,
            y_list,
            Y_MIN,
            where=finite_mask,
            interpolate=False,
            color=CHART_FILL_COLOR,
            alpha=0.13,
        )

        if math.isfinite(value):
            self.dot.set_data([MAX_POINTS - 1], [value])
            self.top_right.config(text=f"{value:.1f}%")
        else:
            self.dot.set_data([], [])
            self.top_right.config(text="N/A")

    def update_chart(self):
        if self._closed:
            return

        raw = self.get_next_value()
        value = self.sanitize_value(raw)
        self._refresh_series(value)

        self.canvas.draw_idle()
        self._after_id = self.parent.after(UPDATE_MS, self.update_chart)

    def start(self):
        if self._after_id is None and not self._closed:
            self.update_chart()

    def stop(self):
        if self._after_id is not None:
            try:
                self.parent.after_cancel(self._after_id)
            except TclError:
                pass
            self._after_id = None

    def _on_destroy(self, event):
        if event.widget is self.container:
            self._closed = True
            self.stop()



if __name__ == "__main__":
    root = Tk()
    app = Chart(root)
    root.mainloop()