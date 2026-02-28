# Requirements Document

## Introduction

This document specifies requirements for adding advanced analytics and statistics features to an existing Streamlit F1 Dashboard application. The feature will provide deeper insights into Formula 1 performance data through driver analytics, team performance metrics, circuit-specific analysis, comparative analytics, and statistical insights. The implementation must work within the existing single-file Streamlit architecture, use the Jolpica F1 API (Ergast data) without a database, and leverage caching for performance optimization.

## Glossary

- **Analytics_Module**: The component responsible for calculating advanced statistics and performance metrics
- **Dashboard**: The existing Streamlit F1 Dashboard application
- **API_Client**: The component that retrieves data from the Jolpica F1 API
- **Cache_Manager**: The component that manages Streamlit's caching mechanism for API responses and calculations
- **Driver_Analytics**: Subsystem providing driver-specific performance metrics
- **Team_Analytics**: Subsystem providing constructor/team performance metrics
- **Circuit_Analytics**: Subsystem providing track-specific performance analysis
- **Comparative_Analytics**: Subsystem enabling multi-entity performance comparisons
- **Statistical_Engine**: Component performing correlation analysis and predictions
- **Visualization_Component**: Component rendering interactive charts using Plotly
- **Performance_Metric**: A calculated statistical measure of driver, team, or circuit performance
- **DNF**: Did Not Finish - a race retirement
- **Form_Indicator**: Performance trend based on recent race results
- **Consistency_Score**: Statistical measure of result variability (inverse of standard deviation)
- **Grid_Position**: Starting position in a race (qualifying result)
- **Race_Result**: Final finishing position in a race

## Requirements

### Requirement 1: Driver Performance Trends

**User Story:** As a F1 analyst, I want to view driver performance trends over time, so that I can identify improvement or decline patterns across seasons.

#### Acceptance Criteria

1. WHEN a user selects a driver and time period, THE Driver_Analytics SHALL calculate performance trends based on finishing positions
2. WHEN a user selects a driver and time period, THE Driver_Analytics SHALL calculate performance trends based on points scored per race
3. THE Visualization_Component SHALL display performance trends as interactive line charts with race-by-race data points
4. WHEN a user hovers over a data point, THE Visualization_Component SHALL display race name, date, finishing position, and points scored
5. WHERE a user selects multiple seasons, THE Driver_Analytics SHALL aggregate data across the selected time period

### Requirement 2: Driver Consistency Metrics

**User Story:** As a F1 analyst, I want to measure driver consistency, so that I can evaluate performance reliability beyond average results.

#### Acceptance Criteria

1. WHEN a user requests consistency metrics for a driver, THE Driver_Analytics SHALL calculate the standard deviation of finishing positions for completed races
2. WHEN a user requests consistency metrics for a driver, THE Driver_Analytics SHALL calculate a Consistency_Score normalized to a 0-100 scale where higher values indicate greater consistency
3. THE Driver_Analytics SHALL exclude DNF results from consistency calculations
4. WHEN calculating consistency for a season, THE Driver_Analytics SHALL require a minimum of 5 completed races
5. THE Visualization_Component SHALL display consistency metrics alongside average finishing position

### Requirement 3: Qualifying vs Race Performance Correlation

**User Story:** As a F1 analyst, I want to analyze the correlation between qualifying and race performance, so that I can understand a driver's race-day strengths or weaknesses.

#### Acceptance Criteria

1. WHEN a user selects a driver and season, THE Driver_Analytics SHALL calculate the correlation coefficient between Grid_Position and Race_Result
2. WHEN a user selects a driver and season, THE Driver_Analytics SHALL calculate the average position change from qualifying to race finish
3. THE Visualization_Component SHALL display a scatter plot with Grid_Position on x-axis and Race_Result on y-axis
4. THE Visualization_Component SHALL display the correlation coefficient and trend line on the scatter plot
5. WHEN the correlation coefficient is below -0.3, THE Driver_Analytics SHALL classify the driver as "strong race performer"
6. WHEN the correlation coefficient is above 0.7, THE Driver_Analytics SHALL classify the driver as "qualifying-dependent performer"

### Requirement 4: DNF Rate Analysis

**User Story:** As a F1 analyst, I want to track DNF rates for drivers, so that I can assess reliability and risk factors.

#### Acceptance Criteria

1. WHEN a user requests DNF analysis for a driver, THE Driver_Analytics SHALL calculate the percentage of races ending in DNF
2. WHEN a user requests DNF analysis for a driver, THE Driver_Analytics SHALL categorize DNF causes as mechanical, accident, or other when available from API data
3. THE Driver_Analytics SHALL calculate DNF rate over user-selected time periods (season, career, last N races)
4. THE Visualization_Component SHALL display DNF rate as a percentage with visual comparison to season average
5. WHERE DNF cause data is available, THE Visualization_Component SHALL display a breakdown chart of DNF causes

### Requirement 5: Points Per Race Average

**User Story:** As a F1 analyst, I want to calculate points per race averages, so that I can normalize performance across different season lengths and scoring systems.

#### Acceptance Criteria

1. WHEN a user requests points analysis for a driver, THE Driver_Analytics SHALL calculate total points divided by races entered
2. WHEN a user requests points analysis for a driver, THE Driver_Analytics SHALL calculate points per race for completed races only (excluding DNFs)
3. THE Driver_Analytics SHALL calculate points per race for user-selected time periods (season, career, last N races)
4. THE Visualization_Component SHALL display points per race alongside total points and races entered
5. WHERE multiple seasons are selected, THE Visualization_Component SHALL display a bar chart comparing points per race across seasons

### Requirement 6: Form Indicators

**User Story:** As a F1 analyst, I want to see recent form indicators, so that I can assess current driver momentum and trends.

#### Acceptance Criteria

1. WHEN a user views driver analytics, THE Driver_Analytics SHALL calculate average finishing position for the last 5 races
2. WHEN a user views driver analytics, THE Driver_Analytics SHALL calculate total points scored in the last 5 races
3. WHEN a user views driver analytics, THE Driver_Analytics SHALL calculate the trend direction (improving, declining, stable) based on linear regression of last 5 race results
4. THE Visualization_Component SHALL display form indicators with visual trend arrows (up, down, flat)
5. WHEN fewer than 5 races are available in the current season, THE Driver_Analytics SHALL use all available races and indicate the sample size

### Requirement 7: Team Reliability Metrics

**User Story:** As a F1 analyst, I want to measure team reliability, so that I can evaluate constructor performance beyond speed.

#### Acceptance Criteria

1. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate the percentage of races where both drivers finished
2. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate the average finishing position for both drivers combined
3. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate mechanical DNF rate across both drivers
4. THE Visualization_Component SHALL display reliability metrics with comparison to constructor championship position
5. THE Team_Analytics SHALL calculate reliability metrics for user-selected time periods (season, multiple seasons)

### Requirement 8: Constructor Development Trends

**User Story:** As a F1 analyst, I want to track constructor development throughout a season, so that I can identify teams improving or declining.

#### Acceptance Criteria

1. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate rolling average points per race over 3-race windows
2. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate rolling average finishing position over 3-race windows
3. THE Visualization_Component SHALL display development trends as line charts with race-by-race progression
4. THE Team_Analytics SHALL calculate the trend slope to classify development as improving, stable, or declining
5. WHERE multiple teams are selected, THE Visualization_Component SHALL overlay development trends for comparison

### Requirement 9: Driver Pairing Effectiveness

**User Story:** As a F1 analyst, I want to analyze driver pairing effectiveness, so that I can evaluate team dynamics and point distribution.

#### Acceptance Criteria

1. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate the points ratio between the two drivers
2. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate the average qualifying position gap between drivers
3. WHEN a user selects a team and season, THE Team_Analytics SHALL calculate the average race finishing position gap between drivers
4. THE Visualization_Component SHALL display driver pairing metrics with side-by-side comparison charts
5. WHEN the points ratio exceeds 70:30, THE Team_Analytics SHALL flag the pairing as "imbalanced"

### Requirement 10: Circuit-Specific Driver Performance

**User Story:** As a F1 analyst, I want to analyze driver performance at specific circuits, so that I can identify track specialties and weaknesses.

#### Acceptance Criteria

1. WHEN a user selects a driver and circuit, THE Circuit_Analytics SHALL retrieve all historical race results at that circuit for the driver
2. WHEN a user selects a driver and circuit, THE Circuit_Analytics SHALL calculate average finishing position at the circuit
3. WHEN a user selects a driver and circuit, THE Circuit_Analytics SHALL calculate win rate, podium rate, and points rate at the circuit
4. THE Visualization_Component SHALL display circuit-specific performance with comparison to driver's overall average
5. WHERE a driver has competed at a circuit fewer than 3 times, THE Circuit_Analytics SHALL display a low-sample-size warning

### Requirement 11: Circuit Difficulty Ratings

**User Story:** As a F1 analyst, I want to see circuit difficulty ratings, so that I can understand which tracks are most challenging.

#### Acceptance Criteria

1. WHEN a user requests circuit analysis, THE Circuit_Analytics SHALL calculate average DNF rate across all races at each circuit
2. WHEN a user requests circuit analysis, THE Circuit_Analytics SHALL calculate average position changes from grid to finish at each circuit
3. WHEN a user requests circuit analysis, THE Circuit_Analytics SHALL calculate safety car deployment frequency when available from API data
4. THE Circuit_Analytics SHALL normalize difficulty ratings to a 0-100 scale where higher values indicate greater difficulty
5. THE Visualization_Component SHALL display circuit difficulty ratings as a sortable table with visual indicators

### Requirement 12: Multi-Driver Comparison

**User Story:** As a F1 analyst, I want to compare multiple drivers simultaneously, so that I can evaluate relative performance across various metrics.

#### Acceptance Criteria

1. WHEN a user selects 3 or more drivers, THE Comparative_Analytics SHALL retrieve performance data for all selected drivers
2. WHEN a user selects 3 or more drivers, THE Comparative_Analytics SHALL calculate standardized Performance_Metrics for each driver (average finish, points per race, consistency, DNF rate)
3. THE Visualization_Component SHALL display multi-driver comparisons as radar charts with each metric as an axis
4. THE Visualization_Component SHALL display multi-driver comparisons as grouped bar charts for direct metric comparison
5. THE Comparative_Analytics SHALL support comparison of up to 10 drivers simultaneously

### Requirement 13: Season-Over-Season Comparison

**User Story:** As a F1 analyst, I want to compare driver or team performance across seasons, so that I can track long-term development.

#### Acceptance Criteria

1. WHEN a user selects a driver and multiple seasons, THE Comparative_Analytics SHALL calculate key Performance_Metrics for each season
2. WHEN a user selects a team and multiple seasons, THE Comparative_Analytics SHALL calculate key Performance_Metrics for each season
3. THE Visualization_Component SHALL display season-over-season comparisons as line charts showing metric evolution
4. THE Comparative_Analytics SHALL calculate year-over-year percentage change for each metric
5. WHERE scoring systems changed between seasons, THE Comparative_Analytics SHALL normalize points to a common scale

### Requirement 14: Performance Percentile Rankings

**User Story:** As a F1 analyst, I want to see percentile rankings for drivers, so that I can understand relative performance within the field.

#### Acceptance Criteria

1. WHEN a user views driver analytics for a season, THE Comparative_Analytics SHALL calculate the driver's percentile rank for average finishing position
2. WHEN a user views driver analytics for a season, THE Comparative_Analytics SHALL calculate the driver's percentile rank for points scored
3. WHEN a user views driver analytics for a season, THE Comparative_Analytics SHALL calculate the driver's percentile rank for consistency score
4. THE Comparative_Analytics SHALL calculate percentile ranks relative to all drivers who competed in at least 50% of season races
5. THE Visualization_Component SHALL display percentile rankings as horizontal bar charts with field position indicators

### Requirement 15: Qualifying-Race Correlation Analysis

**User Story:** As a F1 analyst, I want to analyze overall correlation between qualifying and race results, so that I can understand the importance of qualifying performance.

#### Acceptance Criteria

1. WHEN a user requests statistical insights for a season, THE Statistical_Engine SHALL calculate the Pearson correlation coefficient between Grid_Position and Race_Result across all races
2. WHEN a user requests statistical insights for a season, THE Statistical_Engine SHALL calculate the percentage of races won from pole position
3. WHEN a user requests statistical insights for a season, THE Statistical_Engine SHALL calculate the average position gain/loss from grid to finish
4. THE Visualization_Component SHALL display correlation analysis with scatter plots and regression lines
5. THE Statistical_Engine SHALL calculate correlation separately for different circuit types when circuit classification data is available

### Requirement 16: Win Probability by Grid Position

**User Story:** As a F1 analyst, I want to see win probabilities based on grid position, so that I can understand the strategic importance of qualifying.

#### Acceptance Criteria

1. WHEN a user requests statistical insights, THE Statistical_Engine SHALL calculate historical win percentage for each Grid_Position (P1-P20)
2. WHEN a user requests statistical insights, THE Statistical_Engine SHALL calculate historical podium percentage for each Grid_Position
3. WHEN a user requests statistical insights, THE Statistical_Engine SHALL calculate historical points-scoring percentage for each Grid_Position
4. THE Statistical_Engine SHALL calculate probabilities using data from user-selected time periods (single season, multiple seasons, all-time)
5. THE Visualization_Component SHALL display win probabilities as a bar chart with Grid_Position on x-axis and probability percentage on y-axis

### Requirement 17: Championship Projections

**User Story:** As a F1 analyst, I want to see championship projections based on current form, so that I can estimate likely championship outcomes.

#### Acceptance Criteria

1. WHEN a user requests championship projections during an active season, THE Statistical_Engine SHALL calculate projected points for remaining races based on each driver's points per race average from last 5 races
2. WHEN a user requests championship projections during an active season, THE Statistical_Engine SHALL calculate projected final championship standings
3. THE Statistical_Engine SHALL provide optimistic, realistic, and pessimistic projection scenarios
4. THE Visualization_Component SHALL display championship projections with current points, projected points, and final projected totals
5. WHEN fewer than 5 races remain in the season, THE Statistical_Engine SHALL display a notice that projections have limited remaining races

### Requirement 18: Data Caching Strategy

**User Story:** As a user, I want analytics to load quickly, so that I can explore data without long wait times.

#### Acceptance Criteria

1. WHEN the Analytics_Module requests data from the API_Client, THE Cache_Manager SHALL cache API responses for 1 hour
2. WHEN the Analytics_Module performs expensive calculations, THE Cache_Manager SHALL cache calculation results using Streamlit's caching mechanism
3. THE Cache_Manager SHALL use driver ID, team ID, season, and metric type as cache keys
4. WHEN cached data exists and is not expired, THE Analytics_Module SHALL retrieve data from cache instead of recalculating
5. THE Dashboard SHALL provide a manual cache refresh option for users who want updated data

### Requirement 19: Interactive Visualization Requirements

**User Story:** As a user, I want interactive visualizations, so that I can explore data dynamically and extract detailed insights.

#### Acceptance Criteria

1. WHEN the Visualization_Component renders a chart, THE Visualization_Component SHALL enable hover tooltips with detailed data points
2. WHEN the Visualization_Component renders a chart, THE Visualization_Component SHALL enable zoom and pan functionality
3. WHEN the Visualization_Component renders a multi-series chart, THE Visualization_Component SHALL enable legend-based series toggling
4. THE Visualization_Component SHALL use consistent color schemes across all analytics visualizations
5. WHEN a chart contains more than 20 data points, THE Visualization_Component SHALL optimize rendering for performance

### Requirement 20: Error Handling and Data Availability

**User Story:** As a user, I want clear feedback when data is unavailable, so that I understand limitations and can adjust my analysis.

#### Acceptance Criteria

1. WHEN the API_Client fails to retrieve data, THE Analytics_Module SHALL display a user-friendly error message indicating the specific data unavailable
2. WHEN insufficient data exists for a calculation (e.g., fewer than minimum required races), THE Analytics_Module SHALL display a warning message with the minimum data requirement
3. WHEN a driver has no historical data at a selected circuit, THE Circuit_Analytics SHALL display a "No data available" message instead of empty charts
4. IF the API_Client returns incomplete data, THEN THE Analytics_Module SHALL calculate metrics using available data and indicate which data points are missing
5. WHEN API rate limits are encountered, THE Analytics_Module SHALL display a message indicating when data will be available and suggest using cached data

### Requirement 21: Analytics Navigation and Organization

**User Story:** As a user, I want organized navigation for analytics features, so that I can easily find and access different analysis types.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a dedicated "Advanced Analytics" section in the navigation menu
2. THE Dashboard SHALL organize analytics into subsections: Driver Analytics, Team Analytics, Circuit Analytics, Comparative Analytics, and Statistical Insights
3. WHEN a user selects an analytics subsection, THE Dashboard SHALL display relevant input controls (driver selector, season selector, etc.)
4. THE Dashboard SHALL maintain user selections when navigating between related analytics views
5. THE Dashboard SHALL provide breadcrumb navigation showing the current analytics context

### Requirement 22: Responsive Design for Analytics

**User Story:** As a user, I want analytics to display properly on different screen sizes, so that I can access insights on various devices.

#### Acceptance Criteria

1. WHEN the Dashboard renders analytics on screens wider than 1200px, THE Visualization_Component SHALL display charts in multi-column layouts
2. WHEN the Dashboard renders analytics on screens narrower than 768px, THE Visualization_Component SHALL stack charts vertically
3. THE Visualization_Component SHALL scale chart dimensions proportionally to viewport width
4. THE Dashboard SHALL ensure all interactive controls remain accessible on mobile devices
5. WHEN charts are too complex for mobile display, THE Visualization_Component SHALL provide a simplified mobile-optimized view

### Requirement 23: Export and Sharing Capabilities

**User Story:** As a user, I want to export analytics data and visualizations, so that I can use insights in reports and presentations.

#### Acceptance Criteria

1. WHEN a user views an analytics visualization, THE Dashboard SHALL provide a download button for exporting the chart as PNG
2. WHEN a user views analytics data, THE Dashboard SHALL provide an option to download underlying data as CSV
3. THE Dashboard SHALL generate shareable URLs that preserve analytics view settings (selected drivers, seasons, metrics)
4. WHEN a user clicks a shareable URL, THE Dashboard SHALL restore the exact analytics view configuration
5. THE Dashboard SHALL include attribution and data source information in exported files

### Requirement 24: Performance Optimization for Large Datasets

**User Story:** As a developer, I want analytics to perform efficiently with large historical datasets, so that users experience minimal latency.

#### Acceptance Criteria

1. WHEN the Analytics_Module processes data spanning more than 10 seasons, THE Analytics_Module SHALL use vectorized Pandas operations instead of iterative loops
2. WHEN the Analytics_Module calculates metrics for multiple entities, THE Analytics_Module SHALL parallelize independent calculations where possible
3. THE Cache_Manager SHALL implement cache warming for commonly accessed analytics views
4. WHEN a calculation exceeds 3 seconds, THE Dashboard SHALL display a progress indicator
5. THE Analytics_Module SHALL limit single queries to a maximum of 20 seasons to prevent excessive API calls

### Requirement 25: Analytics Data Validation

**User Story:** As a developer, I want to validate analytics calculations, so that users receive accurate and reliable insights.

#### Acceptance Criteria

1. WHEN the Analytics_Module calculates a Performance_Metric, THE Analytics_Module SHALL validate that input data contains no null values in required fields
2. WHEN the Analytics_Module calculates percentages, THE Analytics_Module SHALL ensure denominators are non-zero
3. WHEN the Analytics_Module calculates correlation coefficients, THE Analytics_Module SHALL verify that both variables have sufficient variance (standard deviation > 0)
4. IF data validation fails, THEN THE Analytics_Module SHALL log the validation error and display a user-friendly error message
5. THE Analytics_Module SHALL implement unit tests for all statistical calculations with known expected outputs

## Implementation Notes

This requirements document focuses on what the advanced analytics feature must do, not how it should be implemented. The design phase will address technical architecture, API integration patterns, caching strategies, and specific Streamlit component usage. All requirements are written to be testable and verifiable against the Jolpica F1 API data structure and Streamlit framework capabilities.
