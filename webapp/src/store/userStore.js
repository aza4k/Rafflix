import { create } from 'zustand';

export const useUserStore = create((set) => ({
    user: null,
    tickets: 0,
    setUser: (user) => set({ user, tickets: user.ticket_balance }),
    setTickets: (tickets) => set({ tickets }),
    addTickets: (amount) => set((state) => ({ tickets: state.tickets + amount })),
}));
