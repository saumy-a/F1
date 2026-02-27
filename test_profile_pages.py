"""
Test script for driver and team profile pages functionality.
"""

import sys
sys.path.insert(0, '.')

from app import (
    fetch_driver_details,
    fetch_driver_race_results,
    fetch_constructor_details,
    fetch_constructor_race_results,
    fetch_constructor_drivers,
    calculate_driver_statistics,
    calculate_constructor_statistics,
    get_driver_id_from_name,
    get_constructor_id_from_name,
    fetch_driver_standings,
    fetch_constructor_standings
)


def test_driver_profile_functions():
    """Test driver profile related functions."""
    print("Testing driver profile functions...")
    
    # Test fetching driver standings to get a driver ID
    print("\n1. Fetching driver standings...")
    standings = fetch_driver_standings("2024")
    if standings:
        print(f"✓ Successfully fetched {len(standings)} driver standings")
        
        # Get first driver
        first_driver = standings[0]
        driver = first_driver.get('Driver', {})
        driver_id = driver.get('driverId')
        driver_name = f"{driver.get('givenName')} {driver.get('familyName')}"
        
        print(f"\n2. Testing with driver: {driver_name} (ID: {driver_id})")
        
        # Test get_driver_id_from_name
        print("\n3. Testing get_driver_id_from_name...")
        found_id = get_driver_id_from_name(driver_name, standings)
        if found_id == driver_id:
            print(f"✓ Successfully found driver ID: {found_id}")
        else:
            print(f"✗ Failed to find driver ID")
        
        # Test fetch_driver_details
        print("\n4. Testing fetch_driver_details...")
        details = fetch_driver_details(driver_id, "2024")
        if details:
            print(f"✓ Successfully fetched driver details")
            print(f"  - Name: {details.get('givenName')} {details.get('familyName')}")
            print(f"  - Nationality: {details.get('nationality')}")
            print(f"  - Number: {details.get('permanentNumber', 'N/A')}")
        else:
            print(f"✗ Failed to fetch driver details")
        
        # Test fetch_driver_race_results
        print("\n5. Testing fetch_driver_race_results...")
        race_results = fetch_driver_race_results(driver_id, "2024")
        if race_results:
            print(f"✓ Successfully fetched {len(race_results)} race results")
            
            # Test calculate_driver_statistics
            print("\n6. Testing calculate_driver_statistics...")
            stats = calculate_driver_statistics(race_results)
            print(f"✓ Successfully calculated statistics:")
            print(f"  - Total Races: {stats['total_races']}")
            print(f"  - Wins: {stats['wins']}")
            print(f"  - Podiums: {stats['podiums']}")
            print(f"  - Points: {stats['total_points']:.1f}")
            print(f"  - Pole Positions: {stats['pole_positions']}")
            print(f"  - Fastest Laps: {stats['fastest_laps']}")
            print(f"  - DNFs: {stats['dnf_count']}")
            if stats['avg_finish'] > 0:
                print(f"  - Avg Finish: {stats['avg_finish']:.2f}")
        else:
            print(f"✗ Failed to fetch race results")
    else:
        print("✗ Failed to fetch driver standings")


def test_constructor_profile_functions():
    """Test constructor profile related functions."""
    print("\n\n" + "="*60)
    print("Testing constructor profile functions...")
    
    # Test fetching constructor standings to get a constructor ID
    print("\n1. Fetching constructor standings...")
    standings = fetch_constructor_standings("2024")
    if standings:
        print(f"✓ Successfully fetched {len(standings)} constructor standings")
        
        # Get first constructor
        first_constructor = standings[0]
        constructor = first_constructor.get('Constructor', {})
        constructor_id = constructor.get('constructorId')
        constructor_name = constructor.get('name')
        
        print(f"\n2. Testing with constructor: {constructor_name} (ID: {constructor_id})")
        
        # Test get_constructor_id_from_name
        print("\n3. Testing get_constructor_id_from_name...")
        found_id = get_constructor_id_from_name(constructor_name, standings)
        if found_id == constructor_id:
            print(f"✓ Successfully found constructor ID: {found_id}")
        else:
            print(f"✗ Failed to find constructor ID")
        
        # Test fetch_constructor_details
        print("\n4. Testing fetch_constructor_details...")
        details = fetch_constructor_details(constructor_id, "2024")
        if details:
            print(f"✓ Successfully fetched constructor details")
            print(f"  - Name: {details.get('name')}")
            print(f"  - Nationality: {details.get('nationality')}")
        else:
            print(f"✗ Failed to fetch constructor details")
        
        # Test fetch_constructor_drivers
        print("\n5. Testing fetch_constructor_drivers...")
        drivers = fetch_constructor_drivers(constructor_id, "2024")
        if drivers:
            print(f"✓ Successfully fetched {len(drivers)} drivers")
            for driver in drivers:
                print(f"  - {driver.get('givenName')} {driver.get('familyName')}")
        else:
            print(f"✗ Failed to fetch constructor drivers")
        
        # Test fetch_constructor_race_results
        print("\n6. Testing fetch_constructor_race_results...")
        race_results = fetch_constructor_race_results(constructor_id, "2024")
        if race_results:
            print(f"✓ Successfully fetched {len(race_results)} race results")
            
            # Test calculate_constructor_statistics
            print("\n7. Testing calculate_constructor_statistics...")
            stats = calculate_constructor_statistics(race_results)
            print(f"✓ Successfully calculated statistics:")
            print(f"  - Total Races: {stats['total_races']}")
            print(f"  - Wins: {stats['wins']}")
            print(f"  - Podiums: {stats['podiums']}")
            print(f"  - Points: {stats['total_points']:.1f}")
            print(f"  - 1-2 Finishes: {stats['one_two_finishes']}")
            print(f"  - DNFs: {stats['dnf_count']}")
        else:
            print(f"✗ Failed to fetch race results")
    else:
        print("✗ Failed to fetch constructor standings")


if __name__ == "__main__":
    print("="*60)
    print("Testing Profile Pages Functionality")
    print("="*60)
    
    test_driver_profile_functions()
    test_constructor_profile_functions()
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
