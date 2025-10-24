import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UserPlus } from 'lucide-react';

const API_URL = 'http://localhost:5000';
const POLL_INTERVAL = 2000;

const BlazeLeaderboard = () => {
  const [team1, setTeam1] = useState([]);
  const [team2, setTeam2] = useState([]);
  const [bloodSplatter, setBloodSplatter] = useState(false);
  const [bloodDrips, setBloodDrips] = useState([]);
  const [screenShake, setScreenShake] = useState(false);
  const [laserEffect, setLaserEffect] = useState(null);
  const [lastKillCount, setLastKillCount] = useState(0);
  const [lastDeathCount, setLastDeathCount] = useState(0);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch(`${API_URL}/api/players`);
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();

        const allPlayers = [...data.team1, ...data.team2];
        const totalKills = allPlayers.reduce((sum, p) => sum + p.kills, 0);
        const totalDeaths = allPlayers.reduce((sum, p) => sum + p.deaths, 0);

        if (totalKills > lastKillCount) {
          triggerKillEffects();
          setLastKillCount(totalKills);
        }

        if (totalDeaths > lastDeathCount) {
          triggerDeathEffects();
          setLastDeathCount(totalDeaths);
        }

        setTeam1(data.team1);
        setTeam2(data.team2);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      }
    };

    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [lastKillCount, lastDeathCount]);

  useEffect(() => {
    const checkMatchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/match_status`);
        if (!response.ok) return;
        const data = await response.json();
        //if (data.ended) {
          //window.location.href = `${API_URL}/victory`;
           //}
      } catch (error) {
        console.error('Error checking match status:', error);
      }
    };
    const interval = setInterval(checkMatchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const triggerKillEffects = () => {
    setBloodSplatter(true);
    const newDrips = Array.from({ length: 8 }, (_, i) => ({
      id: Date.now() + i,
      left: Math.random() * 100,
      delay: Math.random() * 0.3
    }));
    setBloodDrips(prev => [...prev, ...newDrips]);
    setScreenShake(true);

    setTimeout(() => {
      setBloodSplatter(false);
      setScreenShake(false);
    }, 1000);

    setTimeout(() => {
      setBloodDrips(prev => prev.filter(d => !newDrips.find(nd => nd.id === d.id)));
    }, 3000);
  };

  const triggerDeathEffects = () => {
    const angle = Math.random() * 360;
    setLaserEffect(angle);
    setTimeout(() => setLaserEffect(null), 1500);
  };

  const calculateKD = (kills, deaths) => {
    return deaths === 0 ? kills.toFixed(2) : (kills / deaths).toFixed(2);
  };

  const sortPlayers = (players) => {
    return [...players].sort((a, b) => {
      const kdA = a.deaths === 0 ? a.kills : a.kills / a.deaths;
      const kdB = b.deaths === 0 ? b.kills : b.kills / b.deaths;
      return kdB - kdA;
    });
  };

  const sortedTeam1 = sortPlayers(team1);
  const sortedTeam2 = sortPlayers(team2);

  const PlayerRow = ({ player, rank, isTop }) => (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`relative flex items-center justify-between p-4 mb-2 rounded-lg border-2 backdrop-blur-sm ${
        isTop ? 'bg-red-900/70 border-yellow-500' : 'bg-black/50 border-red-800/50'
      }`}
    >
      <div className="flex items-center gap-4 flex-1">
        <div className={`w-10 h-10 flex items-center justify-center rounded-full font-bold ${
          rank === 1 ? 'bg-yellow-500 text-black' : 
          rank === 2 ? 'bg-gray-400 text-black' : 
          rank === 3 ? 'bg-orange-700 text-white' : 
          'bg-red-900 text-white'
        }`}>
          {rank}
        </div>
        <span className="text-lg font-bold text-white">{player.name}</span>
      </div>

      <div className="flex gap-6 text-center">
        <div>
          <div className="text-xs text-gray-400">KILLS</div>
          <div className="text-xl font-bold text-green-400">{player.kills}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">DEATHS</div>
          <div className="text-xl font-bold text-red-400">{player.deaths}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">K/D</div>
          <div className="text-xl font-bold text-yellow-400">
            {calculateKD(player.kills, player.deaths)}
          </div>
        </div>
      </div>
    </motion.div>
  );

  const TeamLeaderboard = ({ team, teamName }) => (
    <div className="flex-1">
      <div className="bg-gradient-to-r from-red-600 to-yellow-600 p-4 rounded-t-lg backdrop-blur-sm">
        <h2 className="text-2xl font-bold text-center text-black">{teamName}</h2>
      </div>
      <div className="bg-black/40 backdrop-blur-md p-6 rounded-b-lg border-2 border-red-800 min-h-[400px]">
        {team.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">Waiting for players...</div>
        ) : (
          <AnimatePresence mode="popLayout">
            {team.map((player, idx) => (
              <PlayerRow key={player.rfid} player={player} rank={idx + 1} isTop={idx === 0} />
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );

  return (
    <motion.div
      className="min-h-screen relative overflow-hidden"
      animate={screenShake ? {
        x: [0, -15, 15, -15, 15, 0],
        y: [0, -15, 15, -10, 10, 0]
      } : {}}
      transition={{ duration: 0.6 }}
      style={{
        backgroundImage: 'url(https://ih1.redbubble.net/image.4618897255.3650/flat,750x,075,f-pad,750x1000,f8f8f8.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      <div className="absolute inset-0 bg-black/50 z-0" />

      {bloodSplatter && (
        <>
          {[0, 1, 2, 3].map(i => (
            <motion.div
              key={i}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 0.8 }}
              exit={{ opacity: 0 }}
              className={`absolute w-64 h-64 pointer-events-none z-40 ${
                i === 0 ? 'top-0 left-0' : i === 1 ? 'top-0 right-0' : 
                i === 2 ? 'bottom-0 left-0' : 'bottom-0 right-0'
              }`}
              style={{
                background: `radial-gradient(circle, rgba(139, 0, 0, 0.9) 0%, transparent 60%)`
              }}
            />
          ))}

          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute bg-red-900 rounded-full pointer-events-none z-40"
              style={{
                width: Math.random() * 80 + 30,
                height: Math.random() * 80 + 30,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: [0, 1.5, 1], opacity: [0, 0.9, 0.6] }}
              transition={{ duration: 0.8, delay: Math.random() * 0.2 }}
            />
          ))}
        </>
      )}

      <AnimatePresence>
        {bloodDrips.map(drip => (
          <motion.div
            key={drip.id}
            className="absolute top-0 w-2 bg-red-900 pointer-events-none z-40"
            style={{ left: `${drip.left}%` }}
            initial={{ height: 0, opacity: 0.8 }}
            animate={{ height: '100vh', opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 2, delay: drip.delay, ease: 'easeIn' }}
          />
        ))}
      </AnimatePresence>

      {laserEffect !== null && (
        <motion.div
          className="absolute inset-0 pointer-events-none z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 1.5 }}
        >
          <motion.div
            className="absolute w-full h-2 bg-gradient-to-r from-transparent via-red-500 to-transparent"
            style={{
              top: '50%',
              left: '50%',
              transformOrigin: 'center',
              transform: `translate(-50%, -50%) rotate(${laserEffect}deg)`,
              width: '200%',
              boxShadow: '0 0 30px 10px rgba(255,0,0,0.8)'
            }}
            animate={{ scaleX: [0, 1, 0] }}
            transition={{ duration: 1.5, ease: 'easeInOut' }}
          />
        </motion.div>
      )}

      <motion.a
        href="/register"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-8 right-8 z-50 bg-gradient-to-r from-purple-900 to-blue-900 hover:from-purple-900 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-full shadow-[0_0_30px_rgba(168,85,247,0.6)] flex items-center gap-3 transition-all"
      >
        <UserPlus className="w-6 h-6" />
        <span>REGISTER</span>
      </motion.a>

      <motion.a
        href="/victory"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-8 left-8 z-50 bg-gradient-to-r from-yellow-900 to-orange-900 hover:from-yellow-700 hover:to-orange-700 text-white font-bold py-4 px-6 rounded-full shadow-[0_0_30px_rgba(251,146,60,0.6)] flex items-center gap-3 transition-all"
      >
        <span className="text-2xl">🏆</span>
        <span>VICTORY</span>
      </motion.a>

      <div className="max-w-7xl mx-auto p-8 relative z-10">
        <motion.div 
          initial={{ y: -50, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }} 
          className="text-center mb-8"
        >
          <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-yellow-500 to-red-500 mb-2 drop-shadow-[0_0_10px_rgba(255,0,0,0.8)]">
            ⚡ BLAZE ⚡
          </h1>
          <p className="text-xl text-yellow-500 font-bold drop-shadow-[0_0_5px_rgba(255,255,0,0.8)]">
            WELCOME TO THE BORDERLAND
          </p>
        </motion.div>

        <div className="flex gap-6">
          <TeamLeaderboard team={sortedTeam1} teamName="TEAM HEARTS ♥️" />
          <TeamLeaderboard team={sortedTeam2} teamName="TEAM SPADES ♠️" />
        </div>
      </div>
    </motion.div>
  );
};

export default BlazeLeaderboard;