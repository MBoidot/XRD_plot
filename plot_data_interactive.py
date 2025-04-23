import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from tkinter import Tk, filedialog
from ipywidgets import (
    IntSlider, FloatRangeSlider, FloatSlider, Button,
    VBox, HBox, interactive_output
)
from IPython.display import display

pio.templates.default = "plotly_white"

def read_xy_files(file_paths):
    data = {}
    for file_path in file_paths:
        serie = os.path.basename(file_path).split(".")[0]
        df = pd.read_csv(file_path, sep=r"\s+", header=None, names=["Angle", "Intensity"])
        data[serie] = df.to_dict("list")
    return data

def normalize_data(data):
    max_intensity = max(data["Intensity"])
    data["Intensity"] = [i / max_intensity for i in data["Intensity"]]
    return data

def moving_average(data, window_size):
    if window_size == 0:
        return data
    data["Intensity"] = np.convolve(
        data["Intensity"], np.ones(window_size) / window_size, mode="valid"
    )
    data["Angle"] = data["Angle"][: len(data["Intensity"])]
    return data

def plot_data_interactive(data):
    fig_holder = {"fig": None}

    def update_plot(offset, moving_avg, x_range, export_width, export_height):
        fig = go.Figure()
        cumulative_offset = 0.05

        for serie, values in data.items():
            values = normalize_data(values.copy())
            smoothed = moving_average(values.copy(), moving_avg)
            if not all(v == 0 for v in smoothed["Intensity"]):
                smoothed["Intensity"] = [i + cumulative_offset for i in smoothed["Intensity"]]
                cumulative_offset += offset
                fig.add_trace(go.Scatter(
                    x=smoothed["Angle"],
                    y=smoothed["Intensity"],
                    mode="lines",
                    name=serie,
                ))

        fig.update_layout(
            xaxis_title="2θ",
            yaxis_title="",
            showlegend=True,
            yaxis=dict(showticklabels=False, mirror=True, ticks="", showline=True, linewidth=2, linecolor="grey"),
            xaxis=dict(range=x_range, showgrid=False, mirror=True, ticks="outside", showline=True, linewidth=2, linecolor="grey"),
            margin=dict(l=0, r=40, t=0, b=0),
            legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top", bgcolor="white", bordercolor="grey", borderwidth=1),
            width=export_width,
            height=export_height,
        )
        fig.update_yaxes(showgrid=False, zeroline=False)
        fig_holder["fig"] = fig
        fig.show()

    def save_plot(b, export_width, export_height):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("PDF files", "*.pdf")],
        )
        if file_path and fig_holder["fig"] is not None:
            fig_holder["fig"].write_image(file_path, scale=6, width=export_width, height=export_height)

    # Widgets
    x_default = [20, 60]
    offset_slider = FloatSlider(min=0, max=1.2, step=0.01, value=1.1, description="Y Offset")
    moving_avg_slider = IntSlider(min=0, max=100, step=1, value=3, description="Moving Avg")
    x_range_slider = FloatRangeSlider(min=0, max=130, step=1, value=x_default, description="X Range")
    export_width_slider = IntSlider(min=100, max=2000, step=10, value=500, description="Export Width")
    export_height_slider = IntSlider(min=100, max=2000, step=10, value=400, description="Export Height")

    controls = {
        "offset": offset_slider,
        "moving_avg": moving_avg_slider,
        "x_range": x_range_slider,
        "export_width": export_width_slider,
        "export_height": export_height_slider,
    }

    output = interactive_output(update_plot, controls)

    save_button = Button(description="Save Plot")
    save_button.on_click(lambda b: save_plot(b, export_width_slider.value, export_height_slider.value))

    display(VBox([
        HBox([offset_slider, moving_avg_slider, x_range_slider]),
        HBox([export_width_slider, export_height_slider]),
        save_button,
        output,
    ]))

def main():
    root = Tk()
    root.withdraw()
    data_files = filedialog.askopenfilenames(
        title="Select .xy Data Files", filetypes=[("XY Files", "*.xy")]
    )
    if not data_files:
        print("No files selected.")
        return
    data = read_xy_files(data_files)
    plot_data_interactive(data)

if __name__ == "__main__":
    main()
