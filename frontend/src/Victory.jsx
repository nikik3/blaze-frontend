import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Skull, Crown, Swords } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const Victory = () => {
  const [victoryData, setVictoryData] = useState(null);
  const [winningPlayers, setWinningPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPlayers, setShowPlayers] = useState(false);

  useEffect(() => {
    loadVictoryData();
  }, []);

  const loadVictoryData = async () => {
    try {
      const [victoryResponse, playersResponse] = await Promise.all([
        fetch(`${API_URL}/api/victory_data`),
        fetch(`${API_URL}/api/players`)
      ]);
      
      const victory = await victoryResponse.json();
      const playersData = await playersResponse.json();
      
      const winners = victory.winningTeam === 'team1' ? playersData.team1 : 
                      victory.winningTeam === 'team2' ? playersData.team2 : 
                      [...playersData.team1, ...playersData.team2];
      
      const sortedWinners = [...winners].sort((a, b) => b.kills - a.kills);
      
      setVictoryData(victory);
      setWinningPlayers(sortedWinners);
      setLoading(false);

      setTimeout(() => setShowPlayers(true), 2000);
    } catch (error) {
      console.error('Failed to load victory data:', error);
      setVictoryData({
        winningTeam: 'unknown',
        team1Score: 0,
        team2Score: 0,
        mvp: { name: 'N/A', kills: 0 }
      });
      setWinningPlayers([]);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <motion.div 
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-red-500 text-4xl font-bold"
        >
          PROCESSING RESULTS...
        </motion.div>
      </div>
    );
  }

  const teamName = victoryData.winningTeam === 'team1' ? 'TEAM HEARTS' : 
                   victoryData.winningTeam === 'team2' ? 'TEAM SPADES' : 'NO VICTOR';
  const isTie = victoryData.winningTeam === 'tie';
  const teamEmoji = victoryData.winningTeam === 'team1' ? '♥️' : '♠️';

  return (
    <div 
      className="min-h-screen relative overflow-y-auto"
      style={{
        backgroundImage: 'url(https://images.immediate.co.uk/production/volatile/sites/3/2025/02/Alice-in-Borderlands-27ad01d.jpg?quality=90&resize=556,505)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      <div className="absolute inset-0 bg-black/85" />

      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 bg-red-900/70"
            style={{
              left: `${Math.random() * 100}%`,
              height: `${Math.random() * 200 + 100}px`
            }}
            animate={{
              y: ['0vh', '100vh'],
              opacity: [0, 0.8, 0]
            }}
            transition={{
              duration: Math.random() * 2 + 2,
              delay: Math.random() * 3,
              repeat: Infinity,
              ease: 'linear'
            }}
          />
        ))}
      </div>

      <div className="absolute inset-0 pointer-events-none">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-red-900/30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`
            }}
            animate={{
              y: [0, -30, 0],
              rotate: [0, 15, -15, 0],
              opacity: [0.2, 0.4, 0.2]
            }}
            transition={{
              duration: 4 + Math.random() * 3,
              delay: Math.random() * 2,
              repeat: Infinity
            }}
          >
            <Skull size={60} />
          </motion.div>
        ))}
      </div>

      

      <div className="relative z-10 px-8 py-16 max-w-6xl mx-auto">
        
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          className="text-center mb-12"
        >
          <motion.div
            animate={{ 
              textShadow: [
                '0 0 20px rgba(139, 0, 0, 0.8)',
                '0 0 40px rgba(139, 0, 0, 1)',
                '0 0 20px rgba(139, 0, 0, 0.8)'
              ]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <h1 className="text-9xl font-black text-red-600 mb-4 tracking-wider">
              {isTie ? 'STALEMATE' : 'GAME CLEAR'}
            </h1>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-4xl text-gray-300 mb-6"
          >
            <span className="text-red-500">◆</span> THE BATTLE HAS CONCLUDED <span className="text-red-500">◆</span>
          </motion.div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-6xl font-black text-white mb-4"
          >
            {!isTie && teamEmoji} {teamName} {!isTie && teamEmoji}
          </motion.div>

          <div className="text-5xl font-bold text-yellow-500 mb-8">
            {victoryData.team1Score} <span className="text-red-700">:</span> {victoryData.team2Score}
          </div>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 1.2, duration: 0.8 }}
            className="w-full h-1 bg-gradient-to-r from-transparent via-red-600 to-transparent mb-12"
          />
        </motion.div>

        {!isTie && showPlayers && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-black/80 border-4 border-red-900 rounded-lg p-8 mb-12 backdrop-blur-sm"
          >
            <div className="flex items-center justify-center gap-4 mb-6">
              <Swords className="w-12 h-12 text-red-500" />
              <h2 className="text-4xl font-black text-red-500 text-center">
                SURVIVING WARRIORS
              </h2>
              <Swords className="w-12 h-12 text-red-500" />
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <AnimatePresence>
                {winningPlayers.map((player, idx) => (
                  <motion.div
                    key={player.rfid}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.2 }}
                    className="bg-gradient-to-r from-red-950/70 to-black/70 border-2 border-red-800 rounded-lg p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 flex items-center justify-center rounded-full bg-red-900 border-2 border-red-600 text-white font-bold text-xl">
                        {idx + 1}
                      </div>
                      <div>
                        <div className="text-xl font-bold text-white">{player.name}</div>
                        <div className="text-sm text-gray-400">RFID: {player.rfid}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-400">{player.kills}</div>
                      <div className="text-xs text-gray-500">ELIMINATIONS</div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {victoryData.mvp && victoryData.mvp.kills > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.5 }}
            className="relative bg-gradient-to-b from-yellow-900/40 via-red-900/60 to-black/80 border-4 rounded-xl p-12 backdrop-blur-md overflow-hidden"
            style={{
              borderImage: 'linear-gradient(45deg, #FFD700, #FF0000, #FFD700) 1',
              boxShadow: '0 0 60px rgba(255, 215, 0, 0.4), inset 0 0 60px rgba(139, 0, 0, 0.3)'
            }}
          >
            <motion.div
              className="absolute inset-0 pointer-events-none"
              animate={{
                boxShadow: [
                  '0 0 30px rgba(255, 215, 0, 0.5)',
                  '0 0 60px rgba(255, 215, 0, 0.8)',
                  '0 0 30px rgba(255, 215, 0, 0.5)'
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            />

            <div className="relative z-10">
              <motion.div
                animate={{ 
                  y: [0, -10, 0],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 4, repeat: Infinity }}
                className="flex justify-center mb-6"
              >
                <Crown className="w-24 h-24 text-yellow-400" style={{ 
                  filter: 'drop-shadow(0 0 20px rgba(255, 215, 0, 1))'
                }} />
              </motion.div>

              <motion.div
                animate={{
                  textShadow: [
                    '0 0 20px rgba(255, 215, 0, 0.8)',
                    '0 0 40px rgba(255, 215, 0, 1)',
                    '0 0 20px rgba(255, 215, 0, 0.8)'
                  ]
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-center"
              >
                <div className="text-yellow-400 text-2xl font-bold mb-4 tracking-widest">
                  ◈ THE REAPER ◈
                </div>
                <div className="text-red-400 text-lg mb-6 italic">
                  "Death's Architect - The One Who Culled The Most"
                </div>
                
                <div className="bg-black/60 rounded-lg p-6 border-2 border-yellow-600/50 mb-6">
                  <div className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-red-500 to-yellow-400 mb-4">
                    {victoryData.mvp.name}
                  </div>
                  <div className="text-gray-400 text-sm mb-4">RFID: {victoryData.mvp.rfid || 'CLASSIFIED'}</div>
                  
                  <div className="flex justify-center gap-12 text-center">
                    <div>
                      <div className="text-5xl font-black text-red-500 mb-2">
                        {victoryData.mvp.kills}
                      </div>
                      <div className="text-yellow-400 text-lg font-bold tracking-wider">
                        SOULS REAPED
                      </div>
                    </div>
                    <div>
                      <div className="text-5xl font-black text-yellow-400 mb-2">
                        {victoryData.mvp.deaths || 0}
                      </div>
                      <div className="text-gray-400 text-lg font-bold tracking-wider">
                        TIMES FALLEN
                      </div>
                    </div>
                    <div>
                      <div className="text-5xl font-black text-green-400 mb-2">
                        {(victoryData.mvp.deaths > 0 ? victoryData.mvp.kills / victoryData.mvp.deaths : victoryData.mvp.kills).toFixed(2)}
                      </div>
                      <div className="text-gray-400 text-lg font-bold tracking-wider">
                        K/D RATIO
                      </div>
                    </div>
                  </div>
                </div>

                <motion.div
                  animate={{ opacity: [0.6, 1, 0.6] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="text-red-500 text-xl italic font-semibold"
                >
                  "In this game of death, only the ruthless survive."
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="text-center mt-12"
        >
          <motion.a
            href="/"
            whileHover={{ scale: 1.05, boxShadow: '0 0 50px rgba(139, 0, 0, 1)' }}
            whileTap={{ scale: 0.95 }}
            className="inline-block bg-gradient-to-r from-red-900 to-black border-4 border-red-600 text-white text-2xl font-black py-5 px-16 rounded-lg transition-all duration-300"
          >
            RETURN TO THE BORDERLAND
          </motion.a>
        </motion.div>
      </div>
    </div>
  );
};

export default Victory;