import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useTelegram } from '../hooks/useTelegram';
import { useUserStore } from '../store/userStore';
import { ChevronLeft, Ticket, Zap, ShieldCheck } from 'lucide-react';

export default function RaffleDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const api = useApi();
    const { tg } = useTelegram();
    const { tickets, setTickets } = useUserStore();

    const [raffle, setRaffle] = useState(null);
    const [count, setCount] = useState(1);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchRaffle = async () => {
            try {
                const res = await api.get(`/raffles/${id}`);
                setRaffle(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchRaffle();
    }, [id]);

    useEffect(() => {
        if (raffle && tg) {
            tg.MainButton.setText(`ENTER WITH ${count * raffle.ticket_price} TICKETS`);
            tg.MainButton.color = "#FFD60A";
            tg.MainButton.textColor = "#0F0F0F";
            tg.MainButton.show();

            const handleClick = () => handleEnter();
            tg.onEvent('mainButtonClicked', handleClick);

            return () => {
                tg.offEvent('mainButtonClicked', handleClick);
                tg.MainButton.hide();
            };
        }
    }, [raffle, count]);

    const handleEnter = async () => {
        if (count * raffle.ticket_price > tickets) {
            tg.showAlert("Not enough tickets! Buy more in the wallet.");
            return;
        }

        setSubmitting(true);
        try {
            await api.post(`/raffles/${id}/enter`, { tickets: count });
            tg.HapticFeedback.notificationOccurred('success');
            tg.showConfirm("Successfully joined the raffle! Good luck 🍀", () => {
                navigate('/');
            });
            // Refresh user balance (simplified)
            const userRes = await api.get('/me');
            setTickets(userRes.data.ticket_balance);
        } catch (err) {
            tg.showAlert("Failed to enter raffle. Please try again.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading || !raffle) return <div className="flex-1 flex items-center justify-center"><div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div></div>;

    return (
        <div className="flex-1 flex flex-col p-4">
            <header className="flex items-center gap-4 mb-6">
                <button onClick={() => navigate(-1)} className="p-2 bg-card rounded-full border border-border">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-xl font-bold">Raffle Details</h1>
            </header>

            <div className="flex-1 overflow-y-auto space-y-6">
                <div className="text-center p-8 bg-accent-soft rounded-card border border-accent border-dashed">
                    <div className="text-6xl mb-4">🎁</div>
                    <h2 className="text-2xl font-black">{raffle.title}</h2>
                    <p className="text-accent font-bold mt-1">Value: {raffle.gift_price} ⭐</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-card p-4 rounded-card border border-border text-center">
                        <p className="text-secondary text-xs mb-1 uppercase">Ticket Price</p>
                        <p className="text-xl font-bold flex items-center justify-center gap-1">
                            {raffle.ticket_price} <Ticket size={18} className="text-accent" />
                        </p>
                    </div>
                    <div className="bg-card p-4 rounded-card border border-border text-center">
                        <p className="text-secondary text-xs mb-1 uppercase">Your Balance</p>
                        <p className="text-xl font-bold flex items-center justify-center gap-1">
                            {tickets} <Ticket size={18} className="text-accent" />
                        </p>
                    </div>
                </div>

                <div className="twa-card">
                    <h3 className="font-bold mb-4 flex items-center gap-2">
                        <Zap size={18} className="text-accent" />
                        Choose Ticket Count
                    </h3>

                    <div className="flex items-center justify-between bg-elevated p-4 rounded-btn border border-border">
                        <button
                            onClick={() => setCount(Math.max(1, count - 1))}
                            className="w-10 h-10 bg-card rounded-md flex items-center justify-center text-2xl font-bold border border-border active:bg-border"
                        >
                            −
                        </button>
                        <span className="text-3xl font-black">{count}</span>
                        <button
                            onClick={() => setCount(count + 1)}
                            className="w-10 h-10 bg-card rounded-md flex items-center justify-center text-2xl font-bold border border-border active:bg-border"
                        >
                            +
                        </button>
                    </div>

                    <p className="text-center text-secondary text-xs mt-4 flex items-center justify-center gap-1">
                        <ShieldCheck size={14} />
                        Entries are final and cannot be refunded.
                    </p>
                </div>
            </div>
        </div>
    );
}
