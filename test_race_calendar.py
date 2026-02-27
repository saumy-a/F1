"""
Test script for race calendar functionality
"""
import requests
from datetime import datetime, timezone

# Test the race schedule endpoint
url = "https://api.jolpi.ca/ergast/f1/current.json"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API is working!")
        
        if 'MRData' in data:
            races = data['MRData']['RaceTable'].get('Races', [])
            if races:
                print(f"\n📊 Found {len(races)} races in the schedule")
                
                # Test countdown calculation for first few races
                now = datetime.now(timezone.utc)
                
                print("\n🏁 First 3 races:")
                for i, race in enumerate(races[:3]):
                    race_name = race.get('raceName', 'Unknown')
                    race_date = race.get('date', 'TBA')
                    race_time = race.get('time', '')
                    circuit = race.get('Circuit', {})
                    circuit_name = circuit.get('circuitName', 'Unknown')
                    
                    # Calculate if upcoming or past
                    try:
                        if race_time:
                            race_time_clean = race_time.replace('Z', '')
                            race_datetime_str = f"{race_date} {race_time_clean}"
                            race_datetime = datetime.strptime(race_datetime_str, "%Y-%m-%d %H:%M:%S")
                            race_datetime = race_datetime.replace(tzinfo=timezone.utc)
                        else:
                            race_datetime = datetime.strptime(race_date, "%Y-%m-%d")
                            race_datetime = race_datetime.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                        
                        time_diff = race_datetime - now
                        
                        if time_diff.total_seconds() < 0:
                            status = "✅ Completed"
                        else:
                            days = time_diff.days
                            hours = time_diff.seconds // 3600
                            status = f"⏱️ {days}d {hours}h"
                    except (ValueError, TypeError):
                        status = "⏱️ TBA"
                    
                    print(f"\n{i+1}. {race_name}")
                    print(f"   Circuit: {circuit_name}")
                    print(f"   Date: {race_date} {race_time[:5] if race_time else ''}")
                    print(f"   Status: {status}")
                
                print("\n✅ Race calendar test completed successfully!")
            else:
                print("❌ No races found in schedule")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
