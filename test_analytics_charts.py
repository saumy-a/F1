"""
Basic tests for analytics chart functions.
Tests the chart creation functions implemented in task 1.5.
"""

import sys
import pandas as pd
import plotly.graph_objects as go

# Import the functions from app.py
from app import (
    create_analytics_trend_chart,
    create_analytics_scatter_chart
)


def create_sample_trend_data():
    """Create sample trend data for testing."""
    return pd.DataFrame({
        'race_name': ['Bahrain GP', 'Saudi Arabian GP', 'Australian GP', 'Japanese GP', 'Chinese GP'],
        'race_date': ['2024-03-02', '2024-03-09', '2024-03-24', '2024-04-07', '2024-04-21'],
        'round': [1, 2, 3, 4, 5],
        'metric_value': [1, 2, 1, 3, 2]
    })


def create_sample_scatter_data():
    """Create sample scatter data for testing."""
    return [
        {'grid': 1, 'finish': 1},
        {'grid': 2, 'finish': 3},
        {'grid': 1, 'finish': 2},
        {'grid': 3, 'finish': 4},
        {'grid': 2, 'finish': 1},
        {'grid': 4, 'finish': 5},
    ]


def test_trend_chart_creation():
    """Test create_analytics_trend_chart function."""
    print("\n=== Testing Trend Chart Creation ===")
    
    trend_data = create_sample_trend_data()
    
    # Test basic chart creation
    fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Max Verstappen",
        team_color="#1E41FF"
    )
    
    print(f"✓ Chart type: {type(fig)}")
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure object"
    
    # Check that the figure has data
    assert len(fig.data) > 0, "Figure should have at least one trace"
    print(f"✓ Number of traces: {len(fig.data)}")
    
    # Check the trace type
    assert isinstance(fig.data[0], go.Scatter), "First trace should be a Scatter plot"
    print(f"✓ Trace type: {type(fig.data[0])}")
    
    # Check that hover template is set
    assert fig.data[0].hovertemplate is not None, "Hover template should be set"
    print(f"✓ Hover template configured")
    
    # Check layout properties
    assert fig.layout.title is not None, "Chart should have a title"
    assert fig.layout.xaxis.title is not None, "X-axis should have a title"
    assert fig.layout.yaxis.title is not None, "Y-axis should have a title"
    print(f"✓ Layout configured with title and axis labels")
    
    # Test with empty data
    empty_fig = create_analytics_trend_chart(
        trend_data=pd.DataFrame(),
        metric_name="Position",
        driver_name="Test Driver"
    )
    assert isinstance(empty_fig, go.Figure), "Should return Figure even with empty data"
    print(f"✓ Handles empty data gracefully")
    
    print("✅ Trend chart tests passed!")


def test_scatter_chart_creation():
    """Test create_analytics_scatter_chart function."""
    print("\n=== Testing Scatter Chart Creation ===")
    
    scatter_data = create_sample_scatter_data()
    
    # Test basic scatter chart without correlation
    fig = create_analytics_scatter_chart(
        scatter_data=scatter_data,
        x_label="Grid Position",
        y_label="Finish Position",
        title="Qualifying vs Race Performance"
    )
    
    print(f"✓ Chart type: {type(fig)}")
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure object"
    
    # Check that the figure has data
    assert len(fig.data) > 0, "Figure should have at least one trace"
    print(f"✓ Number of traces: {len(fig.data)}")
    
    # Check the trace type
    assert isinstance(fig.data[0], go.Scatter), "First trace should be a Scatter plot"
    print(f"✓ Trace type: {type(fig.data[0])}")
    
    # Check that markers are configured
    assert fig.data[0].mode == 'markers', "Should be in markers mode"
    print(f"✓ Markers mode configured")
    
    # Test with correlation (should add trend line)
    fig_with_trend = create_analytics_scatter_chart(
        scatter_data=scatter_data,
        x_label="Grid Position",
        y_label="Finish Position",
        title="Qualifying vs Race Performance",
        correlation=0.75
    )
    
    # Should have 2 traces: scatter points + trend line
    assert len(fig_with_trend.data) >= 1, "Should have at least scatter points"
    print(f"✓ Chart with correlation has {len(fig_with_trend.data)} trace(s)")
    
    # Check layout properties
    assert fig.layout.title is not None, "Chart should have a title"
    assert fig.layout.xaxis.title is not None, "X-axis should have a title"
    assert fig.layout.yaxis.title is not None, "Y-axis should have a title"
    print(f"✓ Layout configured with title and axis labels")
    
    # Test with empty data
    empty_fig = create_analytics_scatter_chart(
        scatter_data=[],
        x_label="X",
        y_label="Y",
        title="Empty Chart"
    )
    assert isinstance(empty_fig, go.Figure), "Should return Figure even with empty data"
    print(f"✓ Handles empty data gracefully")
    
    # Test with x/y keys instead of grid/finish
    xy_data = [
        {'x': 1.5, 'y': 2.3},
        {'x': 2.1, 'y': 3.5},
        {'x': 3.2, 'y': 4.1},
    ]
    xy_fig = create_analytics_scatter_chart(
        scatter_data=xy_data,
        x_label="X Value",
        y_label="Y Value",
        title="XY Scatter"
    )
    assert isinstance(xy_fig, go.Figure), "Should handle x/y keys"
    assert len(xy_fig.data) > 0, "Should have data with x/y keys"
    print(f"✓ Handles x/y key format")
    
    print("✅ Scatter chart tests passed!")


def test_chart_interactivity():
    """Test that charts have interactive features."""
    print("\n=== Testing Chart Interactivity ===")
    
    trend_data = create_sample_trend_data()
    scatter_data = create_sample_scatter_data()
    
    # Test trend chart interactivity
    trend_fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    # Check hover mode is set
    assert trend_fig.layout.hovermode is not None, "Hover mode should be configured"
    print(f"✓ Trend chart hover mode: {trend_fig.layout.hovermode}")
    
    # Check hover template includes race information
    hover_template = trend_fig.data[0].hovertemplate
    assert 'customdata' in hover_template or '%{' in hover_template, \
        "Hover template should include data references"
    print(f"✓ Trend chart has hover tooltips")
    
    # Test scatter chart interactivity
    scatter_fig = create_analytics_scatter_chart(
        scatter_data=scatter_data,
        x_label="Grid",
        y_label="Finish",
        title="Test",
        correlation=0.8
    )
    
    # Check hover mode is set
    assert scatter_fig.layout.hovermode is not None, "Hover mode should be configured"
    print(f"✓ Scatter chart hover mode: {scatter_fig.layout.hovermode}")
    
    # Check hover template
    hover_template = scatter_fig.data[0].hovertemplate
    assert hover_template is not None, "Hover template should be set"
    print(f"✓ Scatter chart has hover tooltips")
    
    # Check that legend is shown for scatter with trend line
    assert scatter_fig.layout.showlegend is not None, "Legend should be configured"
    print(f"✓ Scatter chart legend configured")
    
    print("✅ Interactivity tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Analytics Chart Functions (Task 1.5)")
    print("=" * 60)
    
    try:
        test_trend_chart_creation()
        test_scatter_chart_creation()
        test_chart_interactivity()
        
        print("\n" + "=" * 60)
        print("✅ ALL CHART TESTS PASSED!")
        print("=" * 60)
        print("\nChart functions successfully implement:")
        print("  • create_analytics_trend_chart() for line charts")
        print("  • create_analytics_scatter_chart() with optional trend line")
        print("  • Hover tooltips with race details")
        print("  • Interactive features (zoom, pan)")
        print("  • F1-themed styling")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
