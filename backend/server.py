from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

STATS_FILE = 'game_stats.json'
CONTACTS_FILE = 'contacts_rolls.json'
EXTERNAL_COUNTER_FILE = 'external_counter.json'

if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(EXTERNAL_COUNTER_FILE):
    with open(EXTERNAL_COUNTER_FILE, 'w') as f:
        json.dump({'counter': 0}, f)

match_state = {
    'ended': False,
    'victory_data': None
}

def load_game_stats():
    """Load stats from game_stats.json"""
    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            print(f"📖 Loaded game stats: {len(data)} players")
            return data
    except Exception as e:
        print(f"❌ Error loading stats: {e}")
        return {}

def save_game_stats(data):
    """Save stats to game_stats.json"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(data, f, indent=4, default=str)
        print(f"💾 Saved game stats: {len(data)} players")
    except Exception as e:
        print(f"❌ Error saving stats: {e}")

def get_next_external_id():
    """Get next ID for external players"""
    try:
        with open(EXTERNAL_COUNTER_FILE, 'r') as f:
            data = json.load(f)
        counter = data.get('counter', 0) + 1
        with open(EXTERNAL_COUNTER_FILE, 'w') as f:
            json.dump({'counter': counter}, f)
        return str(counter)
    except:
        return "1"

def convert_to_leaderboard_format(game_stats):
    """Convert game_stats.json format to React leaderboard format"""
    team1 = []
    team2 = []
    
    for player_id, stats in game_stats.items():
        player_data = {
            'rfid': player_id,
            'name': stats.get('name', player_id.replace('_', ' ').title()),
            'kills': stats.get('kills', 0),
            'deaths': stats.get('deaths', 0)
        }
        
        if stats.get('team') == 1:
            team1.append(player_data)
        elif stats.get('team') == 2:
            team2.append(player_data)
    
    return {'team1': team1, 'team2': team2}

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get current leaderboard in React format"""
    game_stats = load_game_stats()
    result = convert_to_leaderboard_format(game_stats)
    print(f"📊 Sending leaderboard: Team1={len(result['team1'])}, Team2={len(result['team2'])}")
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
def register_player():
    """Register a player with RFID (for NITW students)"""
    data = request.json
    rfid = data.get('rfid')
    name = data.get('name')
    team = data.get('team')
    
    if not all([rfid, name, team]):
        return jsonify({'error': 'Missing data'}), 400
    
    team_num = 1 if team == 'team1' else 2
    
    game_stats = load_game_stats()
    player_id = str(rfid)
    
    if player_id not in game_stats:
        game_stats[player_id] = {
            'name': name,
            'team': team_num,
            'kills': 0,
            'deaths': 0,
            'kd': 0.0,
            'last_kill_time': None,
            'kill_intervals': []
        }
        print(f"✅ Registered NEW player: {name} (RFID: {rfid}, Team: {team_num})")
    else:
        game_stats[player_id]['name'] = name
        game_stats[player_id]['team'] = team_num
        print(f"⚠️ Updated existing player: {name} (RFID: {rfid})")
    
    save_game_stats(game_stats)
    return jsonify({'success': True, 'message': f'{name} registered to team {team_num}'})

@app.route('/api/registered_candidates', methods=['GET'])
def get_registered_candidates():
    """Get list of all externally registered players"""
    game_stats = load_game_stats()
    
    external_players = []
    for rfid, stats in game_stats.items():
        if stats.get('external', False):
            external_players.append({
                'rfid': rfid,
                'name': stats.get('name', ''),
                'email': stats.get('email', ''),
                'mobile': stats.get('mobile', ''),
                'college': stats.get('college', 'External'),
                'team': 'Team Hearts' if stats.get('team') == 1 else 'Team Spades'
            })
    
    return jsonify({
        'success': True,
        'count': len(external_players),
        'candidates': external_players
    })

@app.route('/api/kill', methods=['POST'])
def register_kill():
    """Register a kill for a player"""
    data = request.json
    rfid = str(data.get('rfid'))
    
    print(f"🎯 Kill request for RFID: {rfid}")
    
    game_stats = load_game_stats()
    
    if rfid not in game_stats:
        print(f"❌ Player not found: {rfid}")
        return jsonify({'error': 'Player not registered'}), 404
    
    player = game_stats[rfid]
    player['kills'] += 1
    
    now = datetime.now()
    if player.get('last_kill_time'):
        try:
            last_time = datetime.fromisoformat(player['last_kill_time']) if isinstance(player['last_kill_time'], str) else player['last_kill_time']
            time_diff = (now - last_time).total_seconds()
            if 'kill_intervals' not in player:
                player['kill_intervals'] = []
            player['kill_intervals'].append(time_diff)
        except:
            pass
    
    player['last_kill_time'] = now.isoformat()
    
    if player['deaths'] > 0:
        player['kd'] = round(player['kills'] / player['deaths'], 2)
    else:
        player['kd'] = float(player['kills'])
    
    print(f"✅ Kill registered for {player['name']}: Kills={player['kills']}, Deaths={player['deaths']}, KD={player['kd']}")
    
    save_game_stats(game_stats)
    return jsonify({'success': True})

@app.route('/api/death', methods=['POST'])
def register_death():
    """Register a death for a player"""
    data = request.json
    rfid = str(data.get('rfid'))
    
    print(f"💀 Death request for RFID: {rfid}")
    
    game_stats = load_game_stats()
    
    if rfid not in game_stats:
        print(f"❌ Player not found: {rfid}")
        return jsonify({'error': 'Player not registered'}), 404
    
    player = game_stats[rfid]
    player['deaths'] += 1
    
    if player['deaths'] > 0:
        player['kd'] = round(player['kills'] / player['deaths'], 2)
    else:
        player['kd'] = 0.0
    
    print(f"✅ Death registered for {player['name']}: Kills={player['kills']}, Deaths={player['deaths']}, KD={player['kd']}")
    
    save_game_stats(game_stats)
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def reset_match():
    """Reset leaderboard for new match"""
    game_stats = load_game_stats()
    
    for player in game_stats.values():
        player['kills'] = 0
        player['deaths'] = 0
        player['kd'] = 0.0
        player['last_kill_time'] = None
        player['kill_intervals'] = []
    
    save_game_stats(game_stats)
    
    match_state['ended'] = False
    match_state['victory_data'] = None
    
    print("🔄 Match reset!")
    return jsonify({'success': True, 'message': 'Match reset'})

@app.route('/api/end_match', methods=['POST'])
def end_match():
    """End the match and calculate victory data"""
    game_stats = load_game_stats()
    leaderboard = convert_to_leaderboard_format(game_stats)
    
    team1_score = sum(p['kills'] for p in leaderboard['team1'])
    team2_score = sum(p['kills'] for p in leaderboard['team2'])
    
    winning_team = 'team1' if team1_score > team2_score else 'team2' if team2_score > team1_score else 'tie'
    
    all_players = leaderboard['team1'] + leaderboard['team2']
    mvp = max(all_players, key=lambda p: p['kills']) if all_players else {'name': 'N/A', 'kills': 0}
    
    match_state['ended'] = True
    match_state['victory_data'] = {
        'winningTeam': winning_team,
        'team1Score': team1_score,
        'team2Score': team2_score,
        'mvp': mvp
    }
    
    print(f"🏁 Match ended! Winner: {winning_team}, MVP: {mvp['name']}")
    return jsonify({'success': True, 'message': 'Match ended'})

@app.route('/api/match_status', methods=['GET'])
def match_status():
    """Check if match has ended"""
    return jsonify({'ended': match_state['ended']})

@app.route('/api/victory_data', methods=['GET'])
def victory_data():
    """Get victory screen data"""
    if match_state['victory_data']:
        return jsonify(match_state['victory_data'])
    return jsonify({'error': 'No victory data available'}), 404

@app.route('/api/clear_team', methods=['POST'])
def clear_team():
    """Clear all players from a team"""
    data = request.json
    team = data.get('team')
    team_num = 1 if team == 'team1' else 2
    
    game_stats = load_game_stats()
    game_stats = {k: v for k, v in game_stats.items() if v.get('team') != team_num}
    
    save_game_stats(game_stats)
    print(f"🗑️ Cleared team {team_num}")
    
    return jsonify({'success': True})

@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    """Remove a single player"""
    data = request.json
    rfid = str(data.get('rfid'))
    
    game_stats = load_game_stats()
    
    if rfid in game_stats:
        player_name = game_stats[rfid].get('name', rfid)
        del game_stats[rfid]
        save_game_stats(game_stats)
        print(f"🗑️ Removed player: {player_name}")
        return jsonify({'success': True})
    
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/registry', methods=['GET'])
def get_registry():
    """Get all registered RFIDs"""
    game_stats = load_game_stats()
    registry = {}
    
    for rfid, stats in game_stats.items():
        registry[rfid] = {
            'name': stats.get('name', rfid),
            'team': stats.get('team', 1)
        }
    
    return jsonify(registry)

@app.route('/admin')
def admin():
    return send_file('admin_panel.html')

@app.route('/')
def index():
    return send_file('admin_panel.html')

if __name__ == '__main__':
    print("🔥 Blaze Server Starting...")
    print("📡 Backend API: http://0.0.0.0:5000")
    print("👑 Admin Panel: http://0.0.0.0:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=True)