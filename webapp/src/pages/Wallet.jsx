import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegram } from '../hooks/useTelegram';
import { useUserStore } from '../store/userStore';
import { ChevronLeft, Ticket, Star, CreditCard, Clock } from 'lucide-react';

export default function Wallet() {
    const navigate = useNavigate();
    const { tg } = useTelegram();
    const { tickets } = useUserStore();
    const [selectedQty, setSelectedQty] = useState(1);

    const options = [1, 5, 10, 25, 50, 100];

    const handlePurchase = () => {
        if (!tg) return;

        // In TWA, we use openInvoice with a URL or handle it via bot.
        // According to plan.md, we call a bot helper or just open the invoice if we have a URL.
        // For TWA Stars, usually the bot sends the invoice.
        // We can simulate this by sending a message to the bot or calling an API that triggers sendInvoice.

        tg.showConfirm(`Buy ${selectedQty} tickets for ${selectedQty} Stars?`, (ok) => {
            if (ok) {
                // In a real app, you'd call:
                // api.post('/wallet/buy', { qty: selectedQty }).then(res => tg.openInvoice(res.data.url))
                tg.showAlert("Stars Invoice would open here! (Integration requires a live bot token and domain)");
            }
        });
    };

    return (
        <div className="flex-1 flex flex-col p-4 animate-fadeIn">
            <header className="flex items-center gap-4 mb-8">
                <button onClick={() => navigate(-1)} className="p-2 bg-card rounded-full border border-border">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-xl font-bold">Rafflix Wallet</h1>
            </header>

            <div className="bg-gradient-to-br from-accent to-yellow-600 p-6 rounded-card mb-8 shadow-xl shadow-accent/10">
                <div className="flex items-center gap-2 text-primary font-bold uppercase text-xs tracking-widest mb-1 opacity-80">
                    <CreditCard size={14} />
                    <span>Current Balance</span>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-black text-primary">{tickets}</span>
                    <span className="text-xl font-bold text-primary opacity-80">TICKETS</span>
                </div>
            </div>

            <section className="mb-8">
                <h3 className="font-bold mb-4 flex items-center gap-2">
                    <Star size={18} className="text-accent" />
                    Buy Tickets
                </h3>
                <div className="grid grid-cols-3 gap-3 mb-6">
                    {options.map(qty => (
                        <button
                            key={qty}
                            onClick={() => setSelectedQty(qty)}
                            className={`p-4 rounded-btn border transition-all ${selectedQty === qty
                                    ? 'bg-accent-soft border-accent text-accent'
                                    : 'bg-card border-border text-secondary'
                                }`}
                        >
                            <div className="text-lg font-bold">{qty}</div>
                            <div className="text-[10px]">⭐ {qty}</div>
                        </button>
                    ))}
                </div>
                <button
                    onClick={handlePurchase}
                    className="w-full twa-button-primary"
                >
                    Pay with Stars
                </button>
            </section>

            <section className="flex-1">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold flex items-center gap-2">
                        <Clock size={18} className="text-accent" />
                        Recent History
                    </h3>
                    <button className="text-accent text-xs font-bold">See All</button>
                </div>

                <div className="space-y-3 opacity-60 italic text-sm text-center py-8 border border-border border-dashed rounded-card">
                    Transaction history will appear here after your first activity.
                </div>
            </section>
        </div>
    );
}
