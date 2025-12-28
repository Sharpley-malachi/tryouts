import React, { useState } from 'react';
import { CheckCircle, Clock } from 'lucide-react';
import { api } from '../../services/api';

const PendingGateway = () => {
    const [selectedTrade, setSelectedTrade] = useState(null);
    const [pnlInput, setPnlInput] = useState('');

    // Mock Trades
    const trades = [
        { id: 'T001', pair: 'EURUSD', type: 'BUY', entry: 1.0500, status: 'PENDING' },
        { id: 'T002', pair: 'NAS100', type: 'SELL', entry: 15400, status: 'PENDING' },
    ];

    const handleSubmitFeedback = async () => {
        if (!selectedTrade) return;
        alert(`Feedback Loop Closed for ${selectedTrade.id}. Truth Ledger Updated.`);
        setSelectedTrade(null);
    };

    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '2rem', color: '#f59e0b' }}>Pending Feedback Gateway</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <div className="card" style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem' }}>
                    <h3 style={{ marginBottom: '1rem', color: '#94a3b8' }}>Awaiting Reality</h3>
                    {trades.map(trade => (
                        <div
                            key={trade.id}
                            onClick={() => setSelectedTrade(trade)}
                            style={{
                                padding: '1rem',
                                border: '1px solid #334155',
                                marginBottom: '0.5rem',
                                borderRadius: '0.5rem',
                                cursor: 'pointer',
                                backgroundColor: selectedTrade?.id === trade.id ? '#334155' : 'transparent',
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                            }}
                        >
                            <span style={{ fontWeight: 'bold' }}>{trade.pair}</span>
                            <span style={{ color: trade.type === 'BUY' ? '#4ade80' : '#f87171' }}>{trade.type}</span>
                            <Clock size={16} />
                        </div>
                    ))}
                </div>

                {selectedTrade && (
                    <div className="card" style={{ backgroundColor: '#1e293b', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid #38bdf8' }}>
                        <h3 style={{ marginBottom: '1rem', color: '#38bdf8' }}>Close Loop: {selectedTrade.pair}</h3>
                        <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '1rem' }}>
                            Upload outcome candles or enter result to update Strategy DNA.
                        </p>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <textarea
                                placeholder="Paste OCHL Feedback Data..."
                                style={{ width: '100%', height: '100px', backgroundColor: '#0f172a', border: '1px solid #475569', color: 'white', padding: '0.5rem' }}
                            />
                            <button
                                onClick={handleSubmitFeedback}
                                style={{ padding: '0.75rem', backgroundColor: '#22c55e', color: 'white', border: 'none', borderRadius: '0.5rem', fontWeight: 'bold', cursor: 'pointer' }}
                            >
                                <CheckCircle size={18} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                                Confirm Reality
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PendingGateway;
