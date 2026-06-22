import React from 'react';
import { Trophy, Users, Ticket, ArrowRight } from 'lucide-react';

export default function RaffleCard({ raffle, onEnter }) {
    const progress = Math.min(100, (raffle.collected_stars / raffle.target_stars) * 100);

    return (
        <div className="twa-card mb-4 animate-fadeIn">
            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-accent-soft rounded-full flex items-center justify-center text-accent">
                        <Trophy size={24} />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg">{raffle.title}</h3>
                        <p className="text-secondary text-sm">{raffle.gift_name}</p>
                    </div>
                </div>
                <div className="bg-elevated px-2 py-1 rounded-md text-xs font-semibold text-accent">
                    {raffle.gift_price} ⭐
                </div>
            </div>

            <div className="space-y-2 mb-4">
                <div className="flex justify-between text-xs text-secondary">
                    <span>Progress</span>
                    <span>{progress.toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-elevated rounded-full overflow-hidden">
                    <div
                        className="h-full bg-accent transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div className="flex items-center gap-2 text-secondary">
                    <Ticket size={16} />
                    <span>{raffle.target_stars} Target</span>
                </div>
                <div className="flex items-center gap-2 text-secondary">
                    <Users size={16} />
                    <span>{raffle.collected_stars} Sold</span>
                </div>
            </div>

            <button
                onClick={() => onEnter(raffle.id)}
                className="w-full twa-button-primary flex items-center justify-center gap-2"
            >
                Enter Raffle <ArrowRight size={18} />
            </button>
        </div>
    );
}
