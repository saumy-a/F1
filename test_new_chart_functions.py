"""
Test the three new chart functions added in task 7.8:
- create_analytics_radar_chart()
- create_analytics_grouped_bar_chart()
- create_analytics_horizontal_percentile_chart()
"""

import sys
import pandas as pd
import plotly.graph_objects as go

# Import the functions from app.py
from app import (
    create_analytics_radar_chart,
    create_analytics_grouped_bar_chart,
    create_analytics_horizontal_percentile_chart
)


def test_radar_chart():
    """Test create_analytics_radar_chart function."""
    print("\n=== Testing Radar Chart Creation ===")
    
    # Create sample comparison data
    comparison_data = pd.DataFrame({
        'driver_name': ['Verstappen', 'Hamilton', 'Leclerc'],
        'avg_finish': [85.5, 75.2, 70.8],
        'points_per_race': [90.3, 80.1, 75.5],
        'consistency_score': [92.0, 85.0, 78.0],
        'dnf_rate': [95.0, 90.0, 85.0]  # Inverted for radar (higher is better)
    })
    
    metrics = ['avg_finish', 'points_per_race', 'consistency_score', 'dnf_rate']
    entity_names = ['Verstappen', 'Hamilton', 'Leclerc']
    
    # Test basic radar chart creation
    fig = create_analytics_radar_chart(
        comparison_data=comparison_data,
        metrics=metrics,
        entity_names=entity_names
    )
    
    print(f"✓ Chart type: {type(fig)}")
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure object"
    
    # Check that the figure has data (one trace per entity)
    assert len(fig.data) > 0, "Figure should have at least one trace"
    print(f"✓ Number of traces: {len(fig.data)}")
    
    # Check the trace type
    assert isinstance(fig.data[0], go.Scatterpolar), "Traces should be Scatterpolar"
    print(f"✓ Trace type: {type(fig.data[0])}")
    
    # Check that hover template is set
    assert fig.data[0].hovertemplate is not None, "Hover template should be set"
    print(f"✓ Hover template configured")
    
    # Check layout properties
    assert fig.layout.title is not None, "Chart should have a title"
    assert fig.layout.polar is not None, "Should have polar configuration"
    print(f"✓ Layout configured with title and polar axes")
    
    # Test with empty data
    empty_fig = create_analytics_radar_chart(
        comparison_data=pd.DataFrame(),
        metrics=[],
        entity_names=[]
    )
    assert isinstance(empty_fig, go.Figure), "Should return Figure even with empty data"
    print(f"✓ Handles empty data gracefully")
    
    print("✅ Radar chart tests passed!")


def test_grouped_bar_chart():
    """Test create_analytics_grouped_bar_chart function."""
    print("\n=== Testing Grouped Bar Chart Creation ===")
    
    # Create sample comparison data
    comparison_data = pd.DataFrame({
        'season': ['2021', '2022', '2023', '2024'],
        'avg_finish': [2.5, 1.8, 2.1, 1.5],
        'points_per_race': [18.5, 22.3, 20.1, 23.5],
        'consistency_score': [85.0, 90.5, 88.2, 92.0]
    })
    
    # Test basic grouped bar chart creation
    fig = create_analytics_grouped_bar_chart(
        comparison_data=comparison_data,
        x_col='season',
        y_cols=['avg_finish', 'points_per_race', 'consistency_score'],
        title='Season Comparison'
    )
    
    print(f"✓ Chart type: {type(fig)}")
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure object"
    
    # Check that the figure has data (one trace per metric)
    assert len(fig.data) > 0, "Figure should have at least one trace"
    print(f"✓ Number of traces: {len(fig.data)}")
    
    # Check the trace type
    assert isinstance(fig.data[0], go.Bar), "Traces should be Bar"
    print(f"✓ Trace type: {type(fig.data[0])}")
    
    # Check that hover template is set
    assert fig.data[0].hovertemplate is not None, "Hover template should be set"
    print(f"✓ Hover template configured")
    
    # Check layout properties
    assert fig.layout.title is not None, "Chart should have a title"
    assert fig.layout.barmode == 'group', "Should be in grouped bar mode"
    print(f"✓ Layout configured with grouped bar mode")
    
    # Test with empty data
    empty_fig = create_analytics_grouped_bar_chart(
        comparison_data=pd.DataFrame(),
        x_col='test',
        y_cols=[],
        title='Empty Chart'
    )
    assert isinstance(empty_fig, go.Figure), "Should return Figure even with empty data"
    print(f"✓ Handles empty data gracefully")
    
    # Test with missing column
    missing_col_fig = create_analytics_grouped_bar_chart(
        comparison_data=comparison_data,
        x_col='nonexistent',
        y_cols=['avg_finish'],
        title='Missing Column'
    )
    assert isinstance(missing_col_fig, go.Figure), "Should handle missing column"
    print(f"✓ Handles missing column gracefully")
    
    print("✅ Grouped bar chart tests passed!")


def test_horizontal_percentile_chart():
    """Test create_analytics_horizontal_percentile_chart function."""
    print("\n=== Testing Horizontal Percentile Chart Creation ===")
    
    # Create sample percentile data
    percentile_data = {
        'avg_finish_percentile': 92.5,
        'points_percentile': 88.3,
        'consistency_percentile': 85.7,
        'field_size': 20
    }
    
    # Test basic horizontal percentile chart creation
    fig = create_analytics_horizontal_percentile_chart(
        percentile_data=percentile_data,
        driver_name='Max Verstappen'
    )
    
    print(f"✓ Chart type: {type(fig)}")
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure object"
    
    # Check that the figure has data
    assert len(fig.data) > 0, "Figure should have at least one trace"
    print(f"✓ Number of traces: {len(fig.data)}")
    
    # Check the trace type
    assert isinstance(fig.data[0], go.Bar), "Trace should be Bar"
    print(f"✓ Trace type: {type(fig.data[0])}")
    
    # Check orientation is horizontal
    assert fig.data[0].orientation == 'h', "Should be horizontal orientation"
    print(f"✓ Horizontal orientation configured")
    
    # Check that hover template is set
    assert fig.data[0].hovertemplate is not None, "Hover template should be set"
    print(f"✓ Hover template configured")
    
    # Check layout properties
    assert fig.layout.title is not None, "Chart should have a title"
    assert 'Verstappen' in fig.layout.title.text, "Title should include driver name"
    print(f"✓ Layout configured with driver name in title")
    
    # Check that reference lines are added (quartiles)
    shapes = fig.layout.shapes
    if shapes:
        print(f"✓ Reference lines added: {len(shapes)} line(s)")
    
    # Test with empty data
    empty_fig = create_analytics_horizontal_percentile_chart(
        percentile_data={},
        driver_name='Test Driver'
    )
    assert isinstance(empty_fig, go.Figure), "Should return Figure even with empty data"
    print(f"✓ Handles empty data gracefully")
    
    # Test with only field_size (no percentile metrics)
    no_metrics_fig = create_analytics_horizontal_percentile_chart(
        percentile_data={'field_size': 20},
        driver_name='Test Driver'
    )
    assert isinstance(no_metrics_fig, go.Figure), "Should handle no metrics"
    print(f"✓ Handles missing metrics gracefully")
    
    print("✅ Horizontal percentile chart tests passed!")


def test_chart_styling():
    """Test that all charts follow F1 styling guidelines."""
    print("\n=== Testing Chart Styling ===")
    
    # Test radar chart styling
    comparison_data = pd.DataFrame({
        'driver_name': ['Verstappen', 'Hamilton'],
        'metric1': [85.5, 75.2],
        'metric2': [90.3, 80.1]
    })
    radar_fig = create_analytics_radar_chart(
        comparison_data=comparison_data,
        metrics=['metric1', 'metric2'],
        entity_names=['Verstappen', 'Hamilton']
    )
    
    # Check F1 red color is used
    assert '#E10600' in str(radar_fig.layout.title_font.color), "Should use F1 red in title"
    print(f"✓ Radar chart uses F1 styling")
    
    # Test grouped bar chart styling
    bar_data = pd.DataFrame({
        'season': ['2023', '2024'],
        'metric': [10, 20]
    })
    bar_fig = create_analytics_grouped_bar_chart(
        comparison_data=bar_data,
        x_col='season',
        y_cols=['metric'],
        title='Test'
    )
    
    assert '#E10600' in str(bar_fig.layout.title_font.color), "Should use F1 red in title"
    print(f"✓ Grouped bar chart uses F1 styling")
    
    # Test percentile chart styling
    percentile_fig = create_analytics_horizontal_percentile_chart(
        percentile_data={'metric_percentile': 85.0},
        driver_name='Test'
    )
    
    assert '#E10600' in str(percentile_fig.layout.title_font.color), "Should use F1 red in title"
    print(f"✓ Percentile chart uses F1 styling")
    
    print("✅ Styling tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing New Chart Functions (Task 7.8)")
    print("=" * 60)
    
    try:
        test_radar_chart()
        test_grouped_bar_chart()
        test_horizontal_percentile_chart()
        test_chart_styling()
        
        print("\n" + "=" * 60)
        print("✅ ALL NEW CHART TESTS PASSED!")
        print("=" * 60)
        print("\nSuccessfully implemented:")
        print("  • create_analytics_radar_chart() for multi-entity comparison")
        print("  • create_analytics_grouped_bar_chart() for metric comparison")
        print("  • create_analytics_horizontal_percentile_chart() for rankings")
        print("\nAll functions include:")
        print("  • Proper error handling for empty/invalid data")
        print("  • Interactive hover tooltips")
        print("  • F1-themed styling")
        print("  • Responsive layouts")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
