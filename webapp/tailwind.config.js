/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#0F0F0F",
                card: "#1C1C1E",
                elevated: "#2C2C2E",
                accent: "#FFD60A",
                "accent-soft": "rgba(255, 214, 10, 0.14)",
                secondary: "#AEAEB2",
                muted: "#636366",
                success: "#30D158",
                danger: "#FF453A",
                border: "#38383A",
            },
            borderRadius: {
                card: "16px",
                btn: "12px",
            },
        },
    },
    plugins: [],
}
