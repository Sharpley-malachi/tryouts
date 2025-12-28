const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = {
    // Temporal / Ledger
    getPointInTimeState: async (timestamp, instrument, timeframe) => {
        const response = await fetch(`${API_BASE_URL}/ledger/pit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ timestamp_utc: timestamp, instrument, timeframe }),
        });
        if (!response.ok) throw new Error("PIT Query Failed");
        return response.json();
    },

    // Pipeline / Analysis
    uploadContextCSV: async (file, timeframe) => {
        // Hypothetical endpoint based on architecture
        const formData = new FormData();
        formData.append("file", file);
        formData.append("timeframe", timeframe);

        const response = await fetch(`${API_BASE_URL}/pipeline/ingest/csv`, {
            method: "POST",
            body: formData,
        });
        return response.json();
    },

    triggerAnalysis: async (params) => {
        const response = await fetch(`${API_BASE_URL}/general/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params),
        });
        return response.json();
    },

    submitFeedback: async (tradeId, candles) => {
        const response = await fetch(`${API_BASE_URL}/general/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ trade_id: tradeId, outcome_candles: candles }),
        });
        return response.json();
    }
};
