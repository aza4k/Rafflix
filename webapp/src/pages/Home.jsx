import React, { useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { useUserStore } from '../store/userStore';
import RaffleCard from '../components/RaffleCard';
import { Ticket, History, Wallet, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
    const [raffles, setRaffles] = useState([]);
    const [loading, setLoading] = useState(true);
    const { tickets, setUser } = useUserStore();
    const api = useApi();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [userRes, rafflesRes] = await Promise.all([
                    api.get('/me'),
                    api.get('/raffles')
                ]);
                setUser(userRes.data);
                setRaffles(rafflesRes.data);
            } catch (err) {
                console.error("Failed to fetch data", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="flex-1 p-4 overflow-y-auto">
            <header className="flex justify-between items-center mb-8">
                <h1 className="text-2xl font-black italic tracking-tighter">
                    RAFF<span className="text-accent">LIX</span>
                </h1>
                <div
                    onClick={() => navigate('/wallet')}
                    className="bg-card px-3 py-1.5 rounded-full border border-border flex items-center gap-2 text-sm font-bold active:scale-95 transition-transform"
                >
                    <Ticket size={18} className="text-accent" />
                    <span>{tickets} tickets</span>
                </div>
            </header>

            <section className="mb-8">
                <div className="flex items-center gap-2 mb-4 text-secondary font-semibold uppercase text-xs tracking-widest">
                    <History size={14} />
                    <span>Active Raffles</span>
                </div>

                {raffles.length === 0 ? (
                    <div className="twa-card text-center py-8">
                        <Users size={48} className="mx-auto mb-3 text-muted" />
                        <p className="text-secondary">No active raffles yet.</p>
                    </div>
                ) : (
                    raffles.map(raffle => (
                        <RaffleCard
                            key={raffle.id}
                            raffle={raffle}
                            onEnter={(id) => navigate(`/raffle/${id}`)}
                        />
                    ))
                )}
            </section>

            {/* Quick Nav (Temporary or fixed bottom) */}
            <footer className="grid grid-cols-3 gap-2 mt-auto pb-4">
                <button onClick={() => navigate('/wallet')} className="flex flex-col items-center gap-1 text-muted hover:text-white transition-colors">
                    <Wallet size={20} />
                    <span className="text-[10px]">Wallet</span>
                </button>
                <button onClick={() => navigate('/')} className="flex flex-col items-center gap-1 text-accent">
                    <Trophy size={20} />
                    <span className="text-[10px]">Play</span>
                </button>
                <button onClick={() => navigate('/referral')} className="flex flex-col items-center gap-1 text-muted hover:text-white transition-colors">
                    <Users size={20} />
                    <span className="text-[10px]">Friends</span>
                </button>
            </footer>
        </div>
    );
}

// Dummy Trophy import fix
const Trophy = (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" /><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" /><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" /></svg>;
