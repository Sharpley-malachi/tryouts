import React, { useState, useEffect } from 'react';
import FinancialChart from '../charts/FinancialChart';
import PedagogicalPopup from '../common/PedagogicalPopup';
import { api } from '../../services/api';
import { ArrowUp, ArrowDown } from 'lucide-react';

const TimeframeCard = ({ timeframe, data, prediction, onHover }) => {
    // Mock data generation if empty
    const chartData = data || generateMockData();

    return (
        <div style={{ backgroundColor: '#1e293b', borderRadius: '0.75rem', padding: '1rem', marginBottom: '1.5rem', border: '1px solid #334155' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#f1f5f9' }}>{timeframe} Prediction</h3>
                {prediction && (
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <div style={{
                            backgroundColor: prediction.direction === 'BUY' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                            color: prediction.direction === 'BUY' ? '#4ade80' : '#f87171',
                            padding: '0.5rem 1rem', borderRadius: '0.5rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem'
                        }}>
                            {prediction.direction === 'BUY' ? <ArrowUp size={18} /> : <ArrowDown size={18} />}
                            {prediction.direction}
                        </div>
                        <div style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
                            Entry: <span style={{ fontFamily: 'monospace' }}>{prediction.entry}</span> |
                            TP: <span style={{ fontFamily: 'monospace' }}>{prediction.tp}</span> |
                            SL: <span style={{ fontFamily: 'monospace' }}>{prediction.sl}</span>
                        </div>
                    </div>
                )}
            </div>

            <FinancialChart
                data={chartData}
                height={350}
                onCrosshairMove={onHover}
            />
        </div>
    );
};

const PredictionView = ({ analysisResult }) => {
    const [hoverData, setHoverData] = useState(null);
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });

    const handleChartHover = async (param) => {
        if (!param.point || !param.time) {
            setHoverData(null);
            return;
        }

        // 1. Capture Position for Popup
        setCursorPos({ x: param.point.x, y: param.point.y });

        // 2. PIT Query (Simulated or Real)
        try {
            // Note: In real app, convert lightweight-chart time to UTC ISO string
            // Here we just mock the fetch call
            const timestamp = new Date(param.time * 1000).toISOString();

            // Debounce or direct call? Direct for now.
            // const result = await api.getPointInTimeState(timestamp, "EURUSD", "4H");

            // Mock response for UI demo if API fails or backend not running
            const result = {
                timestamp_utc: timestamp,
                internal_brain_state: { notes: "Price approaching FVG. 4H aligned with Daily bias." },
                verification_status: "VERIFIED",
                session_root: "a1b2c3d4..."
            };

            setHoverData(result);
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div style={{ padding: '0 1rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#38bdf8' }}>Market Intelligence Visualization</h2>

            <TimeframeCard
                timeframe="4H (Short-Term)"
                data={analysisResult?.h4?.data}
                prediction={analysisResult?.h4?.prediction}
                onHover={handleChartHover}
            />

            <TimeframeCard
                timeframe="Daily (Swing)"
                data={analysisResult?.daily?.data}
                prediction={analysisResult?.daily?.prediction}
                onHover={handleChartHover}
            />

            <TimeframeCard
                timeframe="Weekly (Macro)"
                data={analysisResult?.weekly?.data}
                prediction={analysisResult?.weekly?.prediction}
                onHover={handleChartHover}
            />

            <PedagogicalPopup data={hoverData} position={cursorPos} />
        </div>
    );
};

// Helper for Mock Data
function generateMockData() {
    // Generate simple sine wave candles
    const result = [];
    let date = new Date();
    date.setDate(date.getDate() - 100);
    let price = 1.0500;

    for (let i = 0; i < 100; i++) {
        const open = price;
        const close = price + (Math.random() - 0.5) * 0.0050;
        const high = Math.max(open, close) + Math.random() * 0.0020;
        const low = Math.min(open, close) - Math.random() * 0.0020;

        result.push({
            time: date.getTime() / 1000,
            open, high, low, close
        });

        price = close;
        date.setDate(date.getDate() + 1);
    }
    return result;
}

export default PredictionView;
