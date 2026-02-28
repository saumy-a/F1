"""
Unit tests for analytics navigation and page structure.

Tests the main analytics page navigation, subsection rendering,
and session state management.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Mock streamlit BEFORE importing app
mock_st = MagicMock()
mock_st.columns.return_value = (MagicMock(), MagicMock())
mock_st.selectbox.return_value = "Coming soon..."
mock_st.multiselect.return_value = []

# Create a proper session_state mock that supports both dict and attribute access
class SessionStateMock(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __contains__(self, key):
        return dict.__contains__(self, key)

mock_st.session_state = SessionStateMock()
sys.modules['streamlit'] = mock_st

# Now import app
import app


class TestAnalyticsNavigation(unittest.TestCase):
    """Test analytics navigation and page structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset session state
        mock_st.session_state.clear()
        mock_st.reset_mock()
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        mock_st.selectbox.return_value = "Coming soon..."
        mock_st.multiselect.return_value = []
    
    def test_render_analytics_main_page_exists(self):
        """Test that render_analytics_main_page function exists."""
        self.assertTrue(hasattr(app, 'render_analytics_main_page'))
        self.assertTrue(callable(app.render_analytics_main_page))
    
    def test_analytics_subsection_functions_exist(self):
        """Test that all subsection rendering functions exist."""
        subsection_functions = [
            'render_analytics_driver_subsection',
            'render_analytics_team_subsection',
            'render_analytics_circuit_subsection',
            'render_analytics_comparative_subsection',
            'render_analytics_statistical_subsection'
        ]
        
        for func_name in subsection_functions:
            self.assertTrue(
                hasattr(app, func_name),
                f"Function {func_name} should exist"
            )
            self.assertTrue(
                callable(getattr(app, func_name)),
                f"Function {func_name} should be callable"
            )
    
    def test_render_analytics_main_page_initializes_session_state(self):
        """Test that main page initializes session state variables."""
        # Mock tabs to return a list of context managers
        mock_tabs = [MagicMock() for _ in range(5)]
        mock_st.tabs.return_value = mock_tabs
        
        # Call the function
        app.render_analytics_main_page("2024")
        
        # Verify session state variables were initialized
        expected_keys = ['analytics_driver', 'analytics_team', 'analytics_circuit', 'analytics_season']
        for key in expected_keys:
            self.assertIn(key, mock_st.session_state, f"Session state should contain {key}")
    
    def test_render_analytics_main_page_creates_tabs(self):
        """Test that main page creates subsection tabs."""
        # Mock tabs
        mock_tabs = [MagicMock() for _ in range(5)]
        mock_st.tabs.return_value = mock_tabs
        
        # Call the function
        app.render_analytics_main_page("2024")
        
        # Verify tabs were created
        mock_st.tabs.assert_called_once()
        
        # Verify the tab labels
        call_args = mock_st.tabs.call_args[0][0]
        expected_tabs = [
            "🏎️ Driver Analytics",
            "🏗️ Team Analytics",
            "🏁 Circuit Analytics",
            "⚔️ Comparative Analytics",
            "📈 Statistical Insights"
        ]
        self.assertEqual(call_args, expected_tabs)
    
    def test_subsection_functions_accept_year_parameter(self):
        """Test that all subsection functions accept year parameter."""
        subsection_functions = [
            app.render_analytics_driver_subsection,
            app.render_analytics_team_subsection,
            app.render_analytics_circuit_subsection,
            app.render_analytics_comparative_subsection,
            app.render_analytics_statistical_subsection
        ]
        
        # Each function should accept year parameter without error
        for func in subsection_functions:
            try:
                func("2024")
            except Exception as e:
                self.fail(f"Function {func.__name__} failed with year parameter: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Analytics Navigation")
    print("=" * 60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsNavigation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
