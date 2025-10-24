import random
import time
import requests
from datetime import datetime

API_URL = 'http://localhost:5000'
GAME_DURATION = 60

PLAYERS = [
    {'name': 'H1', 'team': 'team1'},
    {'name': 'H2', 'team': 'team1'},
    {'name': 'H3', 'team': 'team1'},
    {'name': 'H4', 'team': 'team1'},
    {'name': 'S1', 'team': 'team2'},
    {'name': 'S2', 'team': 'team2'},
    {'name': 'BlahBlah', 'team': 'team2'},
    {'name': 'S4', 'team': 'team2'},
]

def register_all_players():
    """Register all players"""
    print("Registering players...")
    for i, player in enumerate(PLAYERS):
        rfid = f"RFID{str(i+1).zfill(3)}"
        response = requests.post(f'{API_URL}/api/register', json={
            'rfid': rfid,
            'name': player['name'],
            'team': player['team']
        })
        if response.ok:
            print(f"  ✓ {player['name']} registered (RFID: {rfid})")
        else:
            print(f"  ✗ Failed to register {player['name']}: {response.text}")
        time.sleep(0.2)

def simulate_kill(killer_rfid):
    """Simulate a kill"""
    try:
        response = requests.post(f'{API_URL}/api/kill', json={'rfid': killer_rfid})
        if response.ok:
            return True
        else:
            print(f"  Kill failed for {killer_rfid}: {response.text}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def simulate_death(victim_rfid):
    """Simulate a death"""
    try:
        response = requests.post(f'{API_URL}/api/death', json={'rfid': victim_rfid})
        if response.ok:
            return True
        else:
            print(f"  Death failed for {victim_rfid}: {response.text}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def run_simulation():
    print("\nBLAZE GAME SIMULATION")
    print("=" * 50)
    
    register_all_players()
    
    print(f"\n🏁 Starting {GAME_DURATION}s game simulation...\n")
    start_time = time.time()
    event_count = 0
    
    while time.time() - start_time < GAME_DURATION:
        killer_idx = random.randint(0, 7)
        victim_idx = random.randint(0, 7)
        
        if killer_idx != victim_idx:
            killer_rfid = f"RFID{str(killer_idx+1).zfill(3)}"
            victim_rfid = f"RFID{str(victim_idx+1).zfill(3)}"
            
            kill_ok = simulate_kill(killer_rfid)
            death_ok = simulate_death(victim_rfid)
            time.sleep(1)
            
            if kill_ok and death_ok:
                event_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {PLAYERS[killer_idx]['name']} killed {PLAYERS[victim_idx]['name']}")
        
        time.sleep(random.uniform(1, 3))
    
    print(f"\n Simulation complete! Total events: {event_count}")
    print(" Check the leaderboard at http://localhost:5173")

if __name__ == '__main__':
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\n Simulation stopped")
    except Exception as e:
        print(f"\n Error: {e}")
