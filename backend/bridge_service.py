import requests
import time
from pymongo import MongoClient

# Connect to MongoDB to watch for new registrations
client = MongoClient('mongodb://localhost:27017/')
db = client['lasertag']
registered_collection = db['registered']

API_URL = 'http://localhost:5000'

last_game_no = 0

print("🌉 Bridge service started - watching for new games...")

while True:
    try:
        # Get latest game
        latest = registered_collection.find_one(sort=[('game_no', -1)])
        
        if latest and latest['game_no'] > last_game_no:
            game_no = latest['game_no']
            team_one = latest['team_one']
            team_two = latest['team_two']
            
            print(f"\n🎮 New game detected: Game #{game_no}")
            
            # Register team 1 players
            for player in team_one:
                rfid = player.get('rollNumber', player.get('roll', f"P{time.time()}"))
                name = player.get('name', 'Unknown')
                
                requests.post(f'{API_URL}/api/register', json={
                    'rfid': rfid,
                    'name': name,
                    'team': 'team1'
                })
                print(f"  ✓ Registered {name} to Team Hearts")
            
            # Register team 2 players
            for player in team_two:
                rfid = player.get('rollNumber', player.get('roll', f"P{time.time()}"))
                name = player.get('name', 'Unknown')
                
                requests.post(f'{API_URL}/api/register', json={
                    'rfid': rfid,
                    'name': name,
                    'team': 'team2'
                })
                print(f"  ✓ Registered {name} to Team Spades")
            
            last_game_no = game_no
            print(f"✅ Game #{game_no} registered to leaderboard!\n")
        
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(5)
