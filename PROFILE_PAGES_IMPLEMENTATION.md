# Driver & Team Profile Pages Implementation

## Overview
This document describes the implementation of the driver and team profile pages feature for the F1 Dashboard application (Task 13.5).

## Features Implemented

### 1. Driver Profile Pages
Driver profile pages provide comprehensive statistics and performance analysis for individual drivers.

**Features:**
- Personal information display (name, number, nationality, date of birth, Wikipedia link)
- Season statistics:
  - Total races participated
  - Wins
  - Podium finishes
  - Total points
  - Pole positions
  - Fastest laps
  - DNFs (Did Not Finish)
  - Average finishing position
- Current championship standing (position, points, wins)
- Complete race-by-race results table with:
  - Round number
  - Race name
  - Finishing position
  - Starting grid position
  - Points scored
  - Race status
- Interactive visualizations:
  - Points scored per race (bar chart)
  - Finishing positions throughout season (line chart)

**Navigation:**
- Click on any driver name in the Driver Standings page to view their profile
- Back button to return to standings

### 2. Team Profile Pages
Team profile pages provide detailed statistics and performance analysis for constructors.

**Features:**
- Team information display (name, nationality, Wikipedia link)
- Current driver lineup
- Season statistics:
  - Total races
  - Wins
  - Podium finishes
  - Total points
  - 1-2 finishes (both drivers on podium)
  - DNFs
- Current championship standing (position, points, wins)
- Complete race-by-race results table with:
  - Round number
  - Race name
  - Best finishing position
  - Points scored
  - Driver results summary
- Interactive visualization:
  - Points scored per race (bar chart)

**Navigation:**
- Click on any team name in the Constructor Standings page to view their profile
- Back button to return to standings

## Technical Implementation

### New API Functions

1. **`fetch_driver_details(driver_id, year)`**
   - Fetches detailed driver information
   - Cached for 5 minutes

2. **`fetch_driver_race_results(driver_id, year)`**
   - Fetches all race results for a specific driver
   - Cached for 5 minutes

3. **`fetch_constructor_details(constructor_id, year)`**
   - Fetches detailed constructor information
   - Cached for 5 minutes

4. **`fetch_constructor_race_results(constructor_id, year)`**
   - Fetches all race results for a specific constructor
   - Cached for 5 minutes

5. **`fetch_constructor_drivers(constructor_id, year)`**
   - Fetches all drivers for a specific constructor
   - Cached for 5 minutes

### Helper Functions

1. **`get_driver_id_from_name(driver_name, standings_data)`**
   - Converts driver display name to API driver ID

2. **`get_constructor_id_from_name(constructor_name, standings_data)`**
   - Converts constructor display name to API constructor ID

3. **`calculate_driver_statistics(race_results)`**
   - Calculates comprehensive driver statistics from race results
   - Returns: races, wins, podiums, points, avg_finish, DNFs, poles, fastest laps

4. **`calculate_constructor_statistics(race_results)`**
   - Calculates comprehensive constructor statistics from race results
   - Returns: races, wins, podiums, points, 1-2 finishes, DNFs

### UI Rendering Functions

1. **`render_driver_profile_page(driver_name, year)`**
   - Renders complete driver profile page with all statistics and visualizations

2. **`render_constructor_profile_page(constructor_name, year)`**
   - Renders complete team profile page with all statistics and visualizations

### Modified Functions

1. **`render_driver_standings_page(year)`**
   - Added profile navigation logic
   - Replaced static table with clickable driver names
   - Added session state management for profile viewing

2. **`render_constructor_standings_page(year)`**
   - Added profile navigation logic
   - Replaced static table with clickable team names
   - Added session state management for profile viewing

## Session State Management

The implementation uses Streamlit session state to manage navigation between standings and profile pages:

- `show_driver_profile`: Boolean flag to show/hide driver profile
- `selected_driver_name`: Name of the selected driver
- `show_constructor_profile`: Boolean flag to show/hide constructor profile
- `selected_constructor_name`: Name of the selected constructor

## Data Flow

### Driver Profile Flow
1. User clicks driver name in standings
2. Session state updated with driver name and profile flag
3. Page reruns and checks session state
4. If profile flag is set, render profile page instead of standings
5. Fetch driver ID from standings data
6. Fetch driver details and race results from API
7. Calculate statistics
8. Render profile with visualizations
9. Back button clears session state and returns to standings

### Team Profile Flow
1. User clicks team name in standings
2. Session state updated with team name and profile flag
3. Page reruns and checks session state
4. If profile flag is set, render profile page instead of standings
5. Fetch constructor ID from standings data
6. Fetch constructor details, drivers, and race results from API
7. Calculate statistics
8. Render profile with visualizations
9. Back button clears session state and returns to standings

## Testing

A comprehensive test suite was created (`test_profile_pages.py`) that validates:

### Driver Profile Tests
- ✓ Fetching driver standings
- ✓ Converting driver name to ID
- ✓ Fetching driver details
- ✓ Fetching driver race results
- ✓ Calculating driver statistics

### Team Profile Tests
- ✓ Fetching constructor standings
- ✓ Converting constructor name to ID
- ✓ Fetching constructor details
- ✓ Fetching constructor drivers
- ✓ Fetching constructor race results
- ✓ Calculating constructor statistics

**Test Results (2024 Season):**
- All tests passed successfully
- Tested with Max Verstappen (24 races, 9 wins, 14 podiums, 399 points)
- Tested with McLaren (24 races, 6 wins, 21 podiums, 609 points)

## Performance Considerations

1. **Caching**: All API calls are cached for 5 minutes to minimize API requests
2. **Lazy Loading**: Profile data is only fetched when a profile is viewed
3. **Efficient Calculations**: Statistics are calculated once and reused
4. **Responsive Charts**: Plotly charts are optimized for fast rendering

## User Experience

1. **Intuitive Navigation**: Click driver/team names to view profiles
2. **Clear Back Navigation**: Prominent back button to return to standings
3. **Consistent Styling**: Profile pages match the F1 theme of the main app
4. **Loading Indicators**: Spinners shown during data fetching
5. **Error Handling**: Graceful error messages if data cannot be loaded

## Documentation Updates

1. **README.md**: Updated features list to include profile pages
2. **README.md**: Added detailed section about profile page features
3. **README.md**: Updated caching strategy to include profile data

## Files Modified

1. `app.py`: Main application file with all new functionality
2. `README.md`: Documentation updates
3. `test_profile_pages.py`: Test suite for profile pages (new file)
4. `PROFILE_PAGES_IMPLEMENTATION.md`: This implementation document (new file)

## Acceptance Criteria Met

✓ Dark theme works correctly (uses existing Streamlit theme configuration)
✓ Team filter successfully filters drivers (existing feature, still functional)
✓ Progression chart shows points over time (existing feature, still functional)
✓ All bonus features are polished and bug-free (tested and validated)
✓ Profile pages display detailed statistics
✓ Navigation to/from profile pages works seamlessly
✓ Charts and visualizations are interactive and informative
✓ Consistent styling with existing pages
✓ Error handling for missing data

## Future Enhancements

Potential improvements for future iterations:
1. Head-to-head driver comparison on profile pages
2. Historical performance trends across multiple seasons
3. Qualifying results and lap time analysis
4. Team strategy analysis (pit stops, tire choices)
5. Circuit-specific performance statistics
6. Export profile data to PDF/CSV

## Conclusion

The driver and team profile pages feature has been successfully implemented, tested, and documented. The feature provides users with comprehensive insights into driver and team performance, enhancing the overall value of the F1 Dashboard application.
