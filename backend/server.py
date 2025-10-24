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
        json.dump({'players': [], 'gameIsActive': False, 'team1Score': 0, 'team2Score': 0}, f)

if not os.path.exists(EXTERNAL_COUNTER_FILE):
    with open(EXTERNAL_COUNTER_FILE, 'w') as f:
        json.dump({'counter': 0}, f)

match_state = {
    'ended': False,
    'victory_data': None
}

def load_game_stats():
    """Load stats from game_stats.json (supports both old and new format)"""
    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            
            # Check if it's the new format with 'players' array
            if 'players' in data and isinstance(data['players'], list):
                print(f"📖 Loaded game stats (NEW FORMAT): {len(data['players'])} players")
                return data
            else:
                # Old format - convert to new format internally
                print(f"📖 Loaded game stats (OLD FORMAT): {len(data)} players")
                players = []
                for rfid, stats in data.items():
                    if isinstance(stats, dict):  # Skip non-player keys
                        players.append({
                            'id': rfid,
                            'teamId': stats.get('team', 1),
                            'name': stats.get('name', rfid),
                            'kills': stats.get('kills', 0),
                            'deaths': stats.get('deaths', 0),
                            'killTimestamps': [],
                            'deathTimestamps': []
                        })
                return {
                    'players': players,
                    'gameIsActive': False,
                    'team1Score': 0,
                    'team2Score': 0
                }
    except Exception as e:
        print(f"❌ Error loading stats: {e}")
        return {'players': [], 'gameIsActive': False, 'team1Score': 0, 'team2Score': 0}

def save_game_stats(data):
    """Save stats to game_stats.json"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(data, f, indent=4, default=str)
        player_count = len(data.get('players', [])) if 'players' in data else len(data)
        print(f"💾 Saved game stats: {player_count} players")
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
    
    # Handle new format with 'players' array
    if 'players' in game_stats and isinstance(game_stats['players'], list):
        for player in game_stats['players']:
            player_data = {
                'rfid': player.get('id', ''),
                'name': player.get('name', 'Unknown'),
                'kills': player.get('kills', 0),
                'deaths': player.get('deaths', 0)
            }
            
            if player.get('teamId') == 1:
                team1.append(player_data)
            elif player.get('teamId') == 2:
                team2.append(player_data)
    else:
        # Handle old format (for backward compatibility)
        for player_id, stats in game_stats.items():
            if not isinstance(stats, dict):
                continue
                
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

def find_player_by_id(game_stats, player_id):
    """Find a player by ID in the new format"""
    if 'players' in game_stats:
        for player in game_stats['players']:
            if player.get('id') == player_id:
                return player
    return None

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get current leaderboard in React format"""
    game_stats = load_game_stats()
    result = convert_to_leaderboard_format(game_stats)
    print(f"📊 Sending leaderboard: Team1={len(result['team1'])}, Team2={len(result['team2'])}")
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
def register_player():
    """Register a player with RFID"""
    data = request.json
    rfid = str(data.get('rfid'))
    name = data.get('name')
    team = data.get('team')
    
    if not all([rfid, name, team]):
        return jsonify({'error': 'Missing data'}), 400
    
    team_num = 1 if team == 'team1' else 2
    
    game_stats = load_game_stats()
    
    # Ensure we have the new format
    if 'players' not in game_stats:
        game_stats = {'players': [], 'gameIsActive': False, 'team1Score': 0, 'team2Score': 0}
    
    # Check if player already exists
    player = find_player_by_id(game_stats, rfid)
    
    if player:
        # Update existing player
        player['name'] = name
        player['teamId'] = team_num
        print(f"⚠️ Updated existing player: {name} (RFID: {rfid})")
    else:
        # Add new player
        new_player = {
            'id': rfid,
            'teamId': team_num,
            'name': name,
            'kills': 0,
            'deaths': 0,
            'killTimestamps': [],
            'deathTimestamps': []
        }
        game_stats['players'].append(new_player)
        print(f"✅ Registered NEW player: {name} (RFID: {rfid}, Team: {team_num})")
    
    save_game_stats(game_stats)
    return jsonify({'success': True, 'message': f'{name} registered to team {team_num}'})

@app.route('/api/registered_candidates', methods=['GET'])
def get_registered_candidates():
    """Get list of all externally registered players"""
    game_stats = load_game_stats()
    
    external_players = []
    if 'players' in game_stats:
        for player in game_stats['players']:
            if player.get('external', False):
                external_players.append({
                    'rfid': player.get('id'),
                    'name': player.get('name', ''),
                    'email': player.get('email', ''),
                    'mobile': player.get('mobile', ''),
                    'college': player.get('college', 'External'),
                    'team': 'Team Hearts' if player.get('teamId') == 1 else 'Team Spades'
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
    player = find_player_by_id(game_stats, rfid)
    
    if not player:
        print(f"❌ Player not found: {rfid}")
        return jsonify({'error': 'Player not registered'}), 404
    
    player['kills'] += 1
    
    # Add timestamp (optional, for tracking)
    now = datetime.now()
    if 'killTimestamps' not in player:
        player['killTimestamps'] = []
    # We don't add timestamps here since they come from the simulation data
    
    print(f"✅ Kill registered for {player['name']}: Kills={player['kills']}, Deaths={player['deaths']}")
    
    save_game_stats(game_stats)
    return jsonify({'success': True})

@app.route('/api/death', methods=['POST'])
def register_death():
    """Register a death for a player"""
    data = request.json
    rfid = str(data.get('rfid'))
    
    print(f"💀 Death request for RFID: {rfid}")
    
    game_stats = load_game_stats()
    player = find_player_by_id(game_stats, rfid)
    
    if not player:
        print(f"❌ Player not found: {rfid}")
        return jsonify({'error': 'Player not registered'}), 404
    
    player['deaths'] += 1
    
    # Add timestamp (optional, for tracking)
    if 'deathTimestamps' not in player:
        player['deathTimestamps'] = []
    # We don't add timestamps here since they come from the simulation data
    
    print(f"✅ Death registered for {player['name']}: Kills={player['kills']}, Deaths={player['deaths']}")
    
    save_game_stats(game_stats)
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def reset_match():
    """Reset leaderboard for new match"""
    game_stats = load_game_stats()
    
    if 'players' in game_stats:
        for player in game_stats['players']:
            player['kills'] = 0
            player['deaths'] = 0
            player['killTimestamps'] = []
            player['deathTimestamps'] = []
        game_stats['team1Score'] = 0
        game_stats['team2Score'] = 0
    
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
    
    if 'players' in game_stats:
        game_stats['players'] = [p for p in game_stats['players'] if p.get('teamId') != team_num]
    
    save_game_stats(game_stats)
    print(f"🗑️ Cleared team {team_num}")
    
    return jsonify({'success': True})

@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    """Remove a single player"""
    data = request.json
    rfid = str(data.get('rfid'))
    
    game_stats = load_game_stats()
    
    if 'players' in game_stats:
        player = find_player_by_id(game_stats, rfid)
        if player:
            player_name = player.get('name', rfid)
            game_stats['players'] = [p for p in game_stats['players'] if p.get('id') != rfid]
            save_game_stats(game_stats)
            print(f"🗑️ Removed player: {player_name}")
            return jsonify({'success': True})
    
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/registry', methods=['GET'])
def get_registry():
    """Get all registered RFIDs"""
    game_stats = load_game_stats()
    registry = {}
    
    if 'players' in game_stats:
        for player in game_stats['players']:
            registry[player.get('id')] = {
                'name': player.get('name', ''),
                'team': player.get('teamId', 1)
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