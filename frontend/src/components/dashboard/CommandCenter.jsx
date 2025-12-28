import React, { useState } from 'react';
import './CommandCenter.css';
import { Upload, FileUp, AlertTriangle } from 'lucide-react';

const CommandCenter = ({ onAnalyze }) => {
    const [domain, setDomain] = useState('FOREX'); // FOREX or INDICES
    const [files, setFiles] = useState({ monthly: null, weekly: null, daily: null, h4: null });
    const [priceData, setPriceData] = useState({ current: '', buy: '', sell: '' });
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleFileChange = (e, timeframe) => {
        setFiles({ ...files, [timeframe]: e.target.files[0] });
    };

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        // Simulate API call delay
        await new Promise(r => setTimeout(r, 2000));
        onAnalyze({ domain, files, priceData });
        setIsAnalyzing(false);
    };

    return (
        <div className="command-center">
            <div className="card">
                <h2 className="card-title">1. Domain Selection</h2>
                <div className="domain-toggle">
                    <button
                        className={`toggle-btn ${domain === 'FOREX' ? 'active' : ''}`}
                        onClick={() => setDomain('FOREX')}
                    >
                        CURRENCIES / FOREX
                    </button>
                    <button
                        className={`toggle-btn ${domain === 'INDICES' ? 'active' : ''}`}
                        onClick={() => setDomain('INDICES')}
                    >
                        INDICES / STOCKS
                    </button>
                </div>
            </div>

            <div className="card">
                <h2 className="card-title">2. Data Ingestion (CSV)</h2>
                <div className="upload-grid">
                    {['monthly', 'weekly', 'daily', 'h4'].map((tf) => (
                        <div key={tf} className="upload-zone">
                            <input
                                type="file"
                                id={`file-${tf}`}
                                hidden
                                onChange={(e) => handleFileChange(e, tf)}
                                accept=".csv"
                            />
                            <label htmlFor={`file-${tf}`} style={{ cursor: 'pointer' }}>
                                {files[tf] ? (
                                    <div style={{ color: '#4ade80' }}>
                                        <FileUp size={32} style={{ margin: '0 auto 0.5rem' }} />
                                        <p>{files[tf].name}</p>
                                    </div>
                                ) : (
                                    <div style={{ color: '#94a3b8' }}>
                                        <Upload size={32} style={{ margin: '0 auto 0.5rem' }} />
                                        <p>Upload {tf.toUpperCase()}</p>
                                    </div>
                                )}
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            <div className="card">
                <h2 className="card-title">3. Entry Synchronization</h2>
                <div className="input-row">
                    <div className="input-group">
                        <label>Current Broker Price</label>
                        <input
                            type="number"
                            step="0.00001"
                            value={priceData.current}
                            onChange={(e) => setPriceData({ ...priceData, current: e.target.value })}
                            placeholder="e.g. 1.0950"
                        />
                    </div>
                    <div className="input-group">
                        <label>Target Buy (Optional)</label>
                        <input
                            type="number"
                            step="0.00001"
                            value={priceData.buy}
                            onChange={(e) => setPriceData({ ...priceData, buy: e.target.value })}
                        />
                    </div>
                    <div className="input-group">
                        <label>Target Sell (Optional)</label>
                        <input
                            type="number"
                            step="0.00001"
                            value={priceData.sell}
                            onChange={(e) => setPriceData({ ...priceData, sell: e.target.value })}
                        />
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fbbf24', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
                    <AlertTriangle size={16} />
                    <span>Warning: System expects price drift between upload and submission. This is normal.</span>
                </div>

                <button
                    className="analyze-btn"
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !files.h4}
                >
                    {isAnalyzing ? 'Processing Intelligence...' : 'ANALYZE & PREDICT'}
                </button>
            </div>
        </div>
    );
};

export default CommandCenter;
