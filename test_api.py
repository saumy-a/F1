import requests

# Test the Jolpica F1 API
url = "https://api.jolpi.ca/ergast/f1/current/last/results.json"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API is working!")
        print(f"Data keys: {list(data.keys())}")
        
        if 'MRData' in data:
            races = data['MRData']['RaceTable'].get('Races', [])
            if races:
                race = races[0]
                print(f"Latest Race: {race.get('raceName')}")
                print(f"Date: {race.get('date')}")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
