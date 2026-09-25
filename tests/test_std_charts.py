import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria.render.html import render_to_html
from nexoria.std.charts import (
    chart_styles, charts_runtime,
    line_chart, area_chart, sparkline,
    bar_chart,
    pie_chart, donut_chart,
    radial_gauge,
    DEFAULT_PALETTE, color_for,
    LinearScale, nice_ticks,
)


# -- scale ----------------------------------------------------------------

def test_linear_scale_maps_domain_to_range():
    y = LinearScale((0, 100), (200, 0))
    assert y.to_px(0) == 200
    assert y.to_px(100) == 0
    assert y.to_px(50) == 100


def test_linear_scale_handles_flat_domain_without_zero_division():
    y = LinearScale((5, 5), (100, 0))
    y.to_px(5)  # must not raise


def test_nice_ticks_spans_the_requested_range():
    ticks = nice_ticks(0, 87, 5)
    assert ticks[0] <= 0
    assert ticks[-1] >= 87


def test_color_for_cycles_through_palette():
    assert color_for(0) == DEFAULT_PALETTE[0]
    assert color_for(len(DEFAULT_PALETTE)) == DEFAULT_PALETTE[0]


# -- styles / runtime -------------------------------------------------------

def test_chart_styles_renders_style_tag_with_raw_css():
    html = render_to_html(chart_styles())
    assert html.startswith("<style>")
    assert "data-nx-chart-bar" in html


def test_charts_runtime_renders_script_tag_with_raw_js():
    html = render_to_html(charts_runtime())
    assert html.startswith("<script>")
    assert "IntersectionObserver" in html


# -- line / area / sparkline ------------------------------------------------

def test_line_chart_single_series_renders_path_and_dots():
    html = render_to_html(line_chart([12, 19, 14, 22, 30, 26], labels=["M", "T", "W", "T", "F", "S"]))
    assert "<path" in html
    assert 'data-nx-chart-line="true"' in html
    assert "<circle" in html


def test_line_chart_multi_series_renders_legend_and_two_paths():
    html = render_to_html(line_chart([
        {"name": "2024", "values": [10, 14, 9, 18]},
        {"name": "2025", "values": [13, 18, 12, 22]},
    ]))
    assert "2024" in html and "2025" in html
    assert html.count("<path") >= 2
    assert "nx-chart-legend" in html


def test_line_chart_empty_series_does_not_raise():
    html = render_to_html(line_chart([]))
    assert "<svg" in html
    assert "None" not in html


def test_line_chart_no_class_omits_class_attribute():
    html = render_to_html(line_chart([1, 2, 3]))
    assert 'class="None"' not in html


def test_line_chart_with_class_renders_it():
    html = render_to_html(line_chart([1, 2, 3], class_="my-chart"))
    assert 'class="my-chart"' in html


def test_area_chart_fills_under_the_line():
    html = render_to_html(area_chart([1, 5, 3, 8]))
    assert 'data-nx-chart-area="true"' in html


def test_sparkline_renders_minimal_svg_with_no_axes():
    html = render_to_html(sparkline([4, 6, 5, 8, 7, 9, 12]))
    assert "<svg" in html
    assert "nx-chart-axis-label" not in html


def test_sparkline_fill_adds_an_area_path():
    html = render_to_html(sparkline([1, 2, 1, 3], fill=True))
    assert html.count("<path") == 2  # area fill + the line itself


# -- bar --------------------------------------------------------------------

def test_bar_chart_vertical_renders_one_rect_per_series_value():
    html = render_to_html(bar_chart(["Q1", "Q2", "Q3"], [
        {"name": "2024", "values": [12, 19, 14]},
        {"name": "2025", "values": [15, 22, 18]},
    ]))
    assert html.count("<rect") == 6
    assert 'data-nx-chart-bar="v"' in html
    assert "nx-chart-legend" in html


def test_bar_chart_horizontal_uses_horizontal_bar_marker():
    html = render_to_html(bar_chart(["A", "B", "C"], [5, 9, 3], horizontal=True))
    assert 'data-nx-chart-bar="h"' in html


def test_bar_chart_empty_categories_does_not_raise():
    html = render_to_html(bar_chart([], []))
    assert "<svg" in html
    assert "None" not in html


def test_bar_chart_rect_has_native_tooltip_title():
    html = render_to_html(bar_chart(["Mon"], [7]))
    assert "<title>Mon: 7</title>" in html


# -- pie / donut --------------------------------------------------------------

def test_pie_chart_renders_one_wedge_per_slice_with_legend():
    html = render_to_html(pie_chart([
        {"name": "Chrome", "value": 64},
        {"name": "Safari", "value": 19},
        {"name": "Other", "value": 17},
    ]))
    assert html.count("data-nx-chart-wedge") == 3
    assert "Chrome" in html and "nx-chart-legend" in html


def test_pie_chart_single_slice_renders_full_circle_without_error():
    html = render_to_html(pie_chart([100]))
    assert "<path" in html


def test_pie_chart_empty_data_does_not_raise():
    html = render_to_html(pie_chart([]))
    assert "<svg" in html
    assert "None" not in html


def test_donut_chart_has_inner_radius_and_center_label():
    html = render_to_html(donut_chart([64, 19, 17], center_label="100%"))
    assert "100%" in html


# -- gauge --------------------------------------------------------------------

def test_radial_gauge_renders_track_and_value_ring():
    html = render_to_html(radial_gauge(72, label="72%"))
    assert html.count("<circle") == 2
    assert "72%" in html
    assert 'data-nx-chart-gauge="true"' in html


def test_radial_gauge_no_animate_sets_final_dashoffset_directly():
    html = render_to_html(radial_gauge(50, animate=False))
    assert "data-nx-chart-gauge" not in html
    assert "stroke-dashoffset" in html


def test_radial_gauge_clamps_out_of_range_values():
    over = render_to_html(radial_gauge(150, max_value=100, animate=False))
    under = render_to_html(radial_gauge(-20, max_value=100, animate=False))
    assert "stroke-dashoffset: 0.000" in over
    assert "446.1" in under or "446." in under  # full circumference -- 0% filled


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
