import random
import time
import requests
from datetime import datetime
import json

API_URL = 'http://localhost:5000'
GAME_DURATION = 60

def load_game_data():
    """Load player data and kill history from game_stats.json"""
    try:
        with open('game_stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: game_stats.json not found!")
        print("Please create game_stats.json with player data first.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in game_stats.json: {e}")
        return None

def register_all_players(game_data):
    """Register all players from game_stats.json"""
    print("\n📝 Registering players...")
    
    for rfid, player_data in game_data.items():
        team = f"team{player_data['team']}"
        
        response = requests.post(f'{API_URL}/api/register', json={
            'rfid': rfid,
            'name': player_data['name'],
            'team': team
        })
        
        if response.ok:
            print(f"  ✓ {player_data['name']} registered ({rfid}, Team {player_data['team']})")
        else:
            print(f"  ✗ Failed to register {player_data['name']}: {response.text}")
        
        time.sleep(0.1)

def simulate_kill(killer_rfid):
    """Simulate a kill event"""
    try:
        response = requests.post(f'{API_URL}/api/kill', json={'rfid': killer_rfid})
        return response.ok
    except Exception as e:
        print(f"  ❌ Kill error for {killer_rfid}: {e}")
        return False

def simulate_death(victim_rfid):
    """Simulate a death event"""
    try:
        response = requests.post(f'{API_URL}/api/death', json={'rfid': victim_rfid})
        return response.ok
    except Exception as e:
        print(f"  ❌ Death error for {victim_rfid}: {e}")
        return False

def build_kill_queue(game_data):
    """Build a queue of all kill events from game_stats.json"""
    kill_queue = []
    
    for killer_rfid, player_data in game_data.items():
        if 'kill_history' not in player_data:
            continue
        
        for kill_event in player_data['kill_history']:
            kill_queue.append({
                'killer_rfid': killer_rfid,
                'killer_name': player_data['name'],
                'victim_rfid': kill_event['victim'],
                'victim_name': game_data.get(kill_event['victim'], {}).get('name', kill_event['victim']),
                'interval': kill_event['interval']
            })
    
    # Shuffle to create varied gameplay
    random.shuffle(kill_queue)
    
    return kill_queue

def run_simulation():
    print("\n" + "="*60)
    print("🔥 BLAZE GAME SIMULATION - REALISTIC KILL PATTERNS")
    print("="*60)
    
    # Load game data
    game_data = load_game_data()
    if not game_data:
        return
    
    # Register all players
    register_all_players(game_data)
    
    # Build kill queue from actual data
    kill_queue = build_kill_queue(game_data)
    
    if not kill_queue:
        print("\n⚠️ No kill history found in game_stats.json!")
        print("Please add 'kill_history' arrays to your player data.")
        return
    
    print(f"\n🎮 Starting {GAME_DURATION}s simulation with {len(kill_queue)} kill events...")
    print(f"📊 Total players: {len(game_data)}")
    print(f"⚔️ Total kills to simulate: {len(kill_queue)}\n")
    
    start_time = time.time()
    event_count = 0
    
    # Simulate each kill event
    for event in kill_queue:
        elapsed = time.time() - start_time
        
        # Stop if we've exceeded game duration
        if elapsed >= GAME_DURATION:
            print(f"\n⏰ Game time limit reached ({GAME_DURATION}s)")
            break
        
        # Wait based on the kill interval (scale it down to fit in 60s)
        wait_time = min(event['interval'], 5.0)  # Max 5s wait between kills
        time.sleep(wait_time)
        
        # Execute kill and death
        kill_success = simulate_kill(event['killer_rfid'])
        death_success = simulate_death(event['victim_rfid'])
        
        if kill_success and death_success:
            event_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] ⚔️  {event['killer_name']} killed {event['victim_name']}")
        else:
            print(f"[{timestamp}] ❌ Failed: {event['killer_name']} -> {event['victim_name']}")
        
        time.sleep(0.3)  # Small delay for readability
    
    # Summary
    print("\n" + "="*60)
    print(f"✅ SIMULATION COMPLETE!")
    print(f"📊 Total events simulated: {event_count}/{len(kill_queue)}")
    print(f"⏱️  Duration: {time.time() - start_time:.1f}s")
    print(f"🌐 View leaderboard at: http://localhost:5173")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        # Check if server is running
        try:
            requests.get(f'{API_URL}/api/players', timeout=2)
        except:
            print("\n❌ ERROR: Server not running!")
            print(f"Please start server.py first: python server.py")
            exit(1)
        
        run_simulation()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()