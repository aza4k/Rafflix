import axios from 'axios';
import { useTelegram } from './useTelegram';

export function useApi() {
    const { initData } = useTelegram();

    const api = axios.create({
        baseURL: import.meta.env.VITE_API_URL || '/api',
        headers: {
            'X-Telegram-Init-Data': initData,
        },
    });

    return api;
}
