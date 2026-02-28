# Implementation Plan: Advanced Analytics

## Overview

This implementation plan adds advanced analytics capabilities to the existing Streamlit F1 Dashboard. The feature adds a 10th tab "📊 Advanced Analytics" with five analytical subsections: Driver Analytics, Team Analytics, Circuit Analytics, Comparative Analytics, and Statistical Insights. All code will be integrated into the existing app.py file following the established single-file architecture pattern.

The implementation follows a 6-phase approach: Core Infrastructure, Driver Analytics, Team Analytics, Circuit & Comparative Analytics, Statistical Insights, and Polish & Optimization. Each phase builds incrementally on previous work, with checkpoints to ensure stability before proceeding.

## Tasks

- [ ] 1. Phase 1: Core Infrastructure Setup
  - [x] 1.1 Add required imports and helper functions to app.py
    - Add numpy and scipy.stats imports for statistical calculations
    - Implement safe_int(), safe_float(), safe_divide() helper functions
    - Implement is_dnf() function for DNF detection
    - Implement safe_correlation() function with variance checking
    - _Requirements: 25.1, 25.2, 25.3_

  - [x] 1.2 Implement basic analytics calculation functions
    - Implement calculate_analytics_performance_trends() with caching
    - Implement calculate_analytics_consistency_score() with caching
    - Implement calculate_analytics_dnf_rate() with caching
    - Implement calculate_analytics_points_per_race() with caching
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 4.1, 4.2, 5.1, 5.2_

  - [x] 1.3 Write property test for performance trends calculation
    - **Property 1: Performance Trends Calculation**
    - **Validates: Requirements 1.1, 1.2, 1.5**
    - Test that DataFrame has one row per race with correct columns

  - [x] 1.4 Write property test for consistency score calculation
    - **Property 2: Consistency Score Calculation**
    - **Validates: Requirements 2.1, 2.2, 2.3**
    - Test that score is 0-100 range and inversely proportional to std dev

  - [x] 1.5 Implement basic analytics chart functions
    - Implement create_analytics_trend_chart() for line charts
    - Implement create_analytics_scatter_chart() with optional trend line
    - Add hover tooltips and interactive features to charts
    - _Requirements: 1.3, 1.4, 19.1, 19.2, 19.3_

  - [x] 1.6 Write property test for chart structure validation
    - **Property 4: Performance Trend Chart Structure**
    - **Validates: Requirements 1.3, 1.4**
    - Test that charts have proper axes, traces, and hover data

  - [x] 1.7 Create main analytics page with navigation
    - Implement render_analytics_main_page() with subsection selector
    - Add "📊 Advanced Analytics" tab to main() function navigation
    - Set up session state for preserving user selections
    - _Requirements: 21.1, 21.2, 21.3, 21.4_

  - [x] 1.8 Write unit tests for helper functions
    - Test safe_int(), safe_float(), safe_divide() edge cases
    - Test is_dnf() with various status strings
    - Test safe_correlation() with zero variance inputs

- [x] 2. Checkpoint - Verify core infrastructure
  - Ensure all tests pass, verify basic analytics page loads, ask the user if questions arise.

- [x] 3. Phase 2: Driver Analytics Implementation
  - [x] 3.1 Implement remaining driver analytics calculations
    - Implement calculate_analytics_qualifying_race_correlation() with caching
    - Implement calculate_analytics_form_indicator() with caching
    - Add trend classification logic (improving/declining/stable)
    - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3_

  - [x] 3.2 Write property test for qualifying-race correlation
    - **Property 3: Qualifying-Race Correlation Calculation**
    - **Validates: Requirements 3.1, 3.2**
    - Test correlation coefficient is between -1 and 1

  - [x] 3.3 Write property test for form indicator calculation
    - **Property 8: Form Indicator Calculation**
    - **Validates: Requirements 6.1, 6.2, 6.3**
    - Test trend direction matches linear regression slope

  - [x] 3.4 Create driver analytics page with all visualizations
    - Implement render_analytics_driver_page() with driver selector
    - Display performance trends chart with metric toggle
    - Display consistency metrics using st.metric cards
    - Display qualifying vs race correlation scatter plot
    - Display DNF rate analysis with cause breakdown
    - Display points per race comparison
    - Display form indicator with trend arrows
    - _Requirements: 1.3, 1.4, 2.5, 3.3, 3.4, 4.4, 4.5, 5.4, 5.5, 6.4, 6.5_

  - [x] 3.5 Write unit tests for driver analytics calculations
    - Test consistency score with perfect consistency (std_dev = 0)
    - Test consistency score excludes DNF results
    - Test DNF rate with no DNFs and all DNFs
    - Test DNF cause categorization
    - Test form indicator with improving/declining trends

  - [x] 3.6 Add error handling for driver analytics
    - Handle insufficient data errors (< 5 races)
    - Handle missing qualifying or race data
    - Display user-friendly error messages
    - _Requirements: 20.1, 20.2, 20.3, 20.4_

- [x] 4. Checkpoint - Verify driver analytics
  - Ensure all tests pass, verify driver analytics page works correctly, ask the user if questions arise.

- [ ] 5. Phase 3: Team Analytics Implementation
  - [ ] 5.1 Implement team analytics calculation functions
    - Implement calculate_analytics_team_reliability() with caching
    - Implement calculate_analytics_constructor_development() with caching
    - Implement calculate_analytics_driver_pairing() with caching
    - Add rolling window calculations for development trends
    - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2, 9.1, 9.2, 9.3_

  - [ ] 5.2 Write property test for team reliability calculation
    - **Property 9: Team Reliability Calculation**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**
    - Test both-finished percentage and mechanical DNF rate

  - [ ] 5.3 Write property test for constructor development trends
    - **Property 10: Constructor Development Trends**
    - **Validates: Requirements 8.1, 8.2, 8.4**
    - Test rolling averages with correct window size

  - [ ] 5.4 Write property test for driver pairing effectiveness
    - **Property 11: Driver Pairing Effectiveness**
    - **Validates: Requirements 9.1, 9.2, 9.3**
    - Test points ratio sums to 100% and imbalance flag

  - [ ] 5.5 Create team analytics page with visualizations
    - Implement render_analytics_team_page() with constructor selector
    - Display reliability metrics using st.metric cards
    - Display development trends chart with rolling averages
    - Display driver pairing effectiveness comparison
    - Add team color consistency using get_team_color()
    - _Requirements: 7.4, 8.3, 8.5, 9.4, 9.5_

  - [ ] 5.6 Write unit tests for team analytics calculations
    - Test team reliability with both drivers finishing
    - Test constructor development with improving/declining trends
    - Test driver pairing with balanced and imbalanced ratios

- [ ] 6. Checkpoint - Verify team analytics
  - Ensure all tests pass, verify team analytics page works correctly, ask the user if questions arise.

- [ ] 7. Phase 4: Circuit & Comparative Analytics Implementation
  - [ ] 7.1 Implement circuit analytics calculation functions
    - Implement calculate_analytics_circuit_performance() with caching
    - Implement calculate_analytics_circuit_difficulty() with caching
    - Add low-sample-size warning logic
    - _Requirements: 10.1, 10.2, 10.3, 11.1, 11.2, 11.4_

  - [ ] 7.2 Write property test for circuit-specific performance
    - **Property 12: Circuit-Specific Performance**
    - **Validates: Requirements 10.1, 10.2, 10.3**
    - Test average finish, win rate, podium rate calculations

  - [ ] 7.3 Write property test for circuit difficulty rating
    - **Property 13: Circuit Difficulty Rating**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**
    - Test difficulty score is 0-100 range

  - [ ] 7.4 Implement comparative analytics calculation functions
    - Implement calculate_analytics_multi_driver_comparison() with caching
    - Implement calculate_analytics_season_comparison() with caching
    - Implement calculate_analytics_percentile_rankings() with caching
    - Add points normalization for different scoring systems
    - _Requirements: 12.1, 12.2, 13.1, 13.2, 13.4, 13.5, 14.1, 14.2, 14.3, 14.4_

  - [ ] 7.5 Write property test for multi-driver comparison
    - **Property 14: Multi-Driver Comparison**
    - **Validates: Requirements 12.1, 12.2**
    - Test standardized metrics calculated for all drivers

  - [ ] 7.6 Write property test for season-over-season comparison
    - **Property 15: Season-Over-Season Comparison**
    - **Validates: Requirements 13.1, 13.2, 13.4, 13.5**
    - Test year-over-year percentage changes and normalization

  - [ ] 7.7 Write property test for percentile rankings
    - **Property 16: Percentile Rankings**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
    - Test percentiles are 0-100 range

  - [ ] 7.8 Implement additional chart functions
    - Implement create_analytics_radar_chart() for multi-entity comparison
    - Implement create_analytics_grouped_bar_chart() for metric comparison
    - Implement create_analytics_horizontal_percentile_chart()
    - _Requirements: 12.3, 12.4, 13.3, 14.5_

  - [ ] 7.9 Create circuit analytics page
    - Implement render_analytics_circuit_page() with circuit selector
    - Display circuit difficulty ratings table
    - Display driver performance at selected circuit
    - Display historical performance trends
    - _Requirements: 10.4, 10.5, 11.5_

  - [ ] 7.10 Create comparative analytics page
    - Implement render_analytics_comparative_page() with multi-select
    - Display radar chart for multi-driver comparison
    - Display grouped bar charts for direct metric comparison
    - Display season-over-season line charts
    - Display percentile rankings
    - Support comparison of up to 10 drivers
    - _Requirements: 12.3, 12.4, 12.5, 13.3, 14.5_

  - [ ] 7.11 Write unit tests for circuit and comparative analytics
    - Test circuit performance with low sample size warning
    - Test multi-driver comparison with 3-10 drivers
    - Test season comparison with scoring system normalization

- [ ] 8. Checkpoint - Verify circuit and comparative analytics
  - Ensure all tests pass, verify both analytics pages work correctly, ask the user if questions arise.

- [ ] 9. Phase 5: Statistical Insights Implementation
  - [ ] 9.1 Implement statistical calculation functions
    - Implement calculate_analytics_win_probability_by_grid() with caching
    - Implement calculate_analytics_championship_projection() with caching
    - Add three-scenario projection logic (optimistic/realistic/pessimistic)
    - _Requirements: 15.1, 15.2, 15.3, 16.1, 16.2, 16.3, 16.4, 17.1, 17.2, 17.3_

  - [ ] 9.2 Write property test for qualifying-race correlation analysis
    - **Property 17: Qualifying-Race Correlation Analysis**
    - **Validates: Requirements 15.1, 15.2, 15.3, 15.5**
    - Test Pearson correlation and pole position win percentage

  - [ ] 9.3 Write property test for win probability by grid position
    - **Property 18: Win Probability by Grid Position**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**
    - Test win/podium/points percentages for each grid position

  - [ ] 9.4 Write property test for championship projections
    - **Property 19: Championship Projections**
    - **Validates: Requirements 17.1, 17.2, 17.3**
    - Test three-scenario projections based on recent form

  - [ ] 9.5 Create statistical insights page
    - Implement render_analytics_statistical_page() with season range selector
    - Display qualifying-race correlation analysis with scatter plots
    - Display win probability by grid position chart
    - Display championship projections (if mid-season)
    - Display statistical summary cards
    - _Requirements: 15.4, 15.5, 16.5, 17.4, 17.5_

  - [ ] 9.6 Write unit tests for statistical calculations
    - Test win probability with various grid positions
    - Test championship projection with different scenarios
    - Test projection notice when fewer than 5 races remain

- [ ] 10. Checkpoint - Verify statistical insights
  - Ensure all tests pass, verify statistical insights page works correctly, ask the user if questions arise.

- [ ] 11. Phase 6: Polish & Optimization
  - [ ] 11.1 Implement export functionality
    - Add download button for exporting charts as PNG
    - Add option to download underlying data as CSV
    - Include attribution and data source information in exports
    - _Requirements: 23.1, 23.2, 23.5_

  - [ ] 11.2 Implement URL state sharing
    - Generate shareable URLs preserving analytics view settings
    - Implement URL decoding to restore view configuration
    - _Requirements: 23.3, 23.4_

  - [ ] 11.3 Write property test for URL state round-trip
    - **Property 24: URL State Round-Trip**
    - **Validates: Requirements 23.3, 23.4**
    - Test encoding and decoding restores exact configuration

  - [ ] 11.4 Write property test for export metadata inclusion
    - **Property 25: Export Metadata Inclusion**
    - **Validates: Requirements 23.5**
    - Test exported files include attribution

  - [ ] 11.5 Add responsive design improvements
    - Implement multi-column layouts for wide screens (>1200px)
    - Implement vertical stacking for narrow screens (<768px)
    - Scale chart dimensions proportionally to viewport
    - Ensure mobile accessibility for all controls
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

  - [ ] 11.6 Implement performance optimizations
    - Add vectorized Pandas operations for large datasets
    - Add progress indicators for calculations exceeding 3 seconds
    - Implement cache warming for common analytics views
    - Limit single queries to maximum 20 seasons
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5_

  - [ ] 11.7 Write property test for cache key generation
    - **Property 20: Cache Key Generation**
    - **Validates: Requirements 18.3, 18.4**
    - Test cache keys include all parameters affecting results

  - [ ] 11.8 Add comprehensive error handling
    - Handle API failures with user-friendly messages
    - Handle rate limit errors with retry suggestions
    - Add validation for all input data
    - Log errors for debugging
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 25.1, 25.2, 25.3, 25.4_

  - [ ] 11.9 Write property test for error handling and messages
    - **Property 22: Error Handling and Messages**
    - **Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5**
    - Test appropriate error messages for various failure conditions

  - [ ] 11.10 Write property test for input data validation
    - **Property 26: Input Data Validation**
    - **Validates: Requirements 25.1, 25.2, 25.3, 25.4**
    - Test validation catches null values, zero denominators, zero variance

  - [ ] 11.11 Update requirements.txt and documentation
    - Add scipy and hypothesis to requirements.txt
    - Update README.md with Advanced Analytics feature description
    - Document analytics subsections and capabilities

- [ ] 12. Final checkpoint - Complete testing and verification
  - Run full test suite (pytest test_analytics.py test_analytics_properties.py -v)
  - Verify all 26 correctness properties pass
  - Test all analytics pages with real API data
  - Verify responsive design on different screen sizes
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each phase
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- All analytics functions use @st.cache_data(ttl=3600) for performance
- Single-file architecture maintained throughout implementation
- Existing fetch_* and parse_* functions are reused wherever possible
