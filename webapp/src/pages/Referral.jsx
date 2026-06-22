import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegram } from '../hooks/useTelegram';
import { ChevronLeft, Share2, Copy, Users, Gift, CheckCircle } from 'lucide-react';
import { useUserStore } from '../store/userStore';
import { settings } from '../../../core/config'; // Relative import might fail in build, better hardcode or use env

export default function Referral() {
    const navigate = useNavigate();
    const { tg, user } = useTelegram();
    const botUsername = "RafflixBot"; // Should come from config
    const referralLink = `t.me/${botUsername}?start=ref_${user?.id || 'id'}`;

    const handleCopy = () => {
        navigator.clipboard.writeText(referralLink);
        tg.HapticFeedback.notificationOccurred('success');
        tg.showAlert("Link copied to clipboard!");
    };

    const handleShare = () => {
        const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=${encodeURIComponent("Join Rafflix and win Telegram Gifts! 🎁")}`;
        tg.openTelegramLink(shareUrl);
    };

    return (
        <div className="flex-1 flex flex-col p-4 animate-fadeIn">
            <header className="flex items-center gap-4 mb-8">
                <button onClick={() => navigate(-1)} className="p-2 bg-card rounded-full border border-border">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-xl font-bold">Invite Friends</h1>
            </header>

            <div className="bg-card p-6 rounded-card border border-border text-center mb-8">
                <div className="w-16 h-16 bg-accent-soft rounded-full flex items-center justify-center text-accent mx-auto mb-4">
                    <Users size={32} />
                </div>
                <h2 className="text-xl font-black mb-2">Earn Free Tickets</h2>
                <p className="text-secondary text-sm">
                    Get <span className="text-accent font-bold">+1 ticket</span> for every friend who joins and makes their first purchase.
                </p>
            </div>

            <div className="space-y-4 mb-8">
                <div className="flex items-center gap-2 p-3 bg-elevated rounded-btn border border-border">
                    <code className="flex-1 text-xs truncate text-secondary">{referralLink}</code>
                    <button onClick={handleCopy} className="p-2 text-accent">
                        <Copy size={18} />
                    </button>
                </div>
                <button
                    onClick={handleShare}
                    className="w-full twa-button-primary flex items-center justify-center gap-2"
                >
                    <Share2 size={18} /> Share with Friends
                </button>
            </div>

            <section className="space-y-6">
                <h3 className="font-bold border-b border-border pb-2">How it works</h3>
                <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-accent text-primary flex items-center justify-center font-black flex-shrink-0">1</div>
                    <div>
                        <h4 className="font-bold text-sm">Send your link</h4>
                        <p className="text-secondary text-xs">Share your unique referral link with friends.</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-accent text-primary flex items-center justify-center font-black flex-shrink-0">2</div>
                    <div>
                        <h4 className="font-bold text-sm">Friend buys tickets</h4>
                        <p className="text-secondary text-xs">Your friend joins Rafflix and buys their first tickets.</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-accent text-primary flex items-center justify-center font-black flex-shrink-0">3</div>
                    <div>
                        <h4 className="font-bold text-sm">Get rewarded</h4>
                        <p className="text-secondary text-xs">You both receive bonus tickets instantly!</p>
                    </div>
                </div>
            </section>
        </div>
    );
}
