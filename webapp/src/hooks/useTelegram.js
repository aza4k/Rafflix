import { useEffect, useState } from 'react';

const webApp = window.Telegram?.WebApp;

export function useTelegram() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        if (webApp) {
            webApp.ready();
            webApp.expand();
            setUser(webApp.initDataUnsafe?.user);
        }
    }, []);

    const onClose = () => {
        webApp?.close();
    };

    const onToggleButton = () => {
        if (webApp?.MainButton.isVisible) {
            webApp.MainButton.hide();
        } else {
            webApp?.MainButton.show();
        }
    };

    return {
        onClose,
        onToggleButton,
        tg: webApp,
        user: user || webApp?.initDataUnsafe?.user,
        queryId: webApp?.initDataUnsafe?.query_id,
        initData: webApp?.initData,
    };
}
