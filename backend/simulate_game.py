import random
import time
import requests
from datetime import datetime
import json

API_URL = 'http://localhost:5000'
GAME_DURATION = 60

def load_game_data():
    """Load player data from game_stats.json (new format with players array)"""
    try:
        with open('game_stats.json', 'r') as f:
            data = json.load(f)
            # Check if 'players' key exists in the new format
            if 'players' not in data:
                print("❌ ERROR: No 'players' array found in game_stats.json!")
                print("Expected format: {'players': [...], 'gameIsActive': false, ...}")
                return None
            return data
    except FileNotFoundError:
        print("❌ ERROR: game_stats.json not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in game_stats.json: {e}")
        return None

def register_all_players(game_data):
    """Register all players from the players array"""
    print("\n📝 Registering players...")
    
    for player in game_data['players']:
        team = f"team{player['teamId']}"
        
        response = requests.post(f'{API_URL}/api/register', json={
            'rfid': player['id'],
            'name': player['name'],
            'team': team
        })
        
        if response.ok:
            print(f"  ✓ {player['name']} registered ({player['id']}, Team {player['teamId']})")
        else:
            print(f"  ✗ Failed to register {player['name']}: {response.text}")
        
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

def build_event_timeline(game_data):
    """Build chronological timeline of all kill/death events from timestamps"""
    events = []
    
    # Collect all kill events
    for player in game_data['players']:
        for timestamp in player.get('killTimestamps', []):
            events.append({
                'type': 'kill',
                'timestamp': timestamp,
                'player_id': player['id'],
                'player_name': player['name']
            })
    
    # Collect all death events
    for player in game_data['players']:
        for timestamp in player.get('deathTimestamps', []):
            events.append({
                'type': 'death',
                'timestamp': timestamp,
                'player_id': player['id'],
                'player_name': player['name']
            })
    
    # Sort by timestamp (chronological order)
    events.sort(key=lambda x: x['timestamp'])
    
    return events

def run_simulation():
    print("\n" + "="*60)
    print("🔥 BLAZE GAME SIMULATION - TIMESTAMP-BASED REPLAY")
    print("="*60)
    
    # Load game data
    game_data = load_game_data()
    if not game_data:
        return
    
    # Register all players
    register_all_players(game_data)
    
    # Build event timeline
    events = build_event_timeline(game_data)
    
    if not events:
        print("\n⚠️ No events found in game_stats.json!")
        print("Make sure players have killTimestamps and deathTimestamps arrays.")
        return
    
    print(f"\n🎮 Starting simulation with {len(events)} events...")
    print(f"📊 Total players: {len(game_data['players'])}")
    print(f"⚔️ Events to replay: {len(events)}\n")
    
    # Calculate time scaling factor to fit in GAME_DURATION
    max_timestamp = max(e['timestamp'] for e in events) if events else 0
    time_scale = GAME_DURATION / (max_timestamp / 1000.0) if max_timestamp > 0 else 1.0
    
    print(f"⏱️  Original game duration: {max_timestamp/1000:.1f}s")
    print(f"⏱️  Time scale: {time_scale:.3f}x (compressed to {GAME_DURATION}s)\n")
    
    start_time = time.time()
    event_count = 0
    last_timestamp = 0
    
    # Replay each event
    for event in events:
        # Calculate wait time based on timestamp difference
        timestamp_seconds = event['timestamp'] / 1000.0
        wait_time = (timestamp_seconds - last_timestamp) * time_scale
        last_timestamp = timestamp_seconds
        
        # Wait until it's time for this event
        if wait_time > 0:
            time.sleep(min(wait_time, 5.0))  # Cap at 5s for safety
        
        elapsed = time.time() - start_time
        
        # Stop if we've exceeded game duration (with 20% buffer)
        if elapsed >= GAME_DURATION * 1.2:
            print(f"\n⏰ Simulation time limit reached")
            break
        
        # Execute the event
        success = False
        if event['type'] == 'kill':
            success = simulate_kill(event['player_id'])
            icon = "⚔️"
            action = "got a kill"
        else:  # death
            success = simulate_death(event['player_id'])
            icon = "💀"
            action = "died"
        
        if success:
            event_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            game_time = f"{event['timestamp']/1000:.1f}s"
            print(f"[{timestamp}] {icon} {event['player_name']} {action} (game time: {game_time})")
        else:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] ❌ Failed: {event['player_name']} {action}")
        
        time.sleep(0.05)  # Small delay for readability
    
    # Summary
    print("\n" + "="*60)
    print(f"✅ SIMULATION COMPLETE!")
    print(f"📊 Total events replayed: {event_count}/{len(events)}")
    print(f"⏱️  Actual duration: {time.time() - start_time:.1f}s")
    print(f"🏆 Team 1 Score: {game_data.get('team1Score', 'N/A')}")
    print(f"🏆 Team 2 Score: {game_data.get('team2Score', 'N/A')}")
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