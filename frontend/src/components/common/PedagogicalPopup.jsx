import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';

const PedagogicalPopup = ({ data, position }) => {
    if (!data) return null;

    const {
        timestamp_utc,
        internal_brain_state,
        verification_status,
        session_root
    } = data;

    const isVerified = verification_status === "VERIFIED";

    return (
        <div style={{
            position: 'absolute',
            left: position.x + 20,
            top: position.y,
            width: '320px',
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            border: `1px solid ${isVerified ? '#22c55e' : '#ef4444'}`,
            borderRadius: '0.5rem',
            padding: '1rem',
            zIndex: 100,
            backdropFilter: 'blur(8px)',
            color: '#f8fafc',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{timestamp_utc}</span>
                {isVerified ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#22c55e', fontSize: '0.75rem', fontWeight: 'bold' }}>
                        <ShieldCheck size={14} />
                        <span>VERIFIED TRUTH</span>
                    </div>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#ef4444', fontSize: '0.75rem', fontWeight: 'bold' }}>
                        <ShieldAlert size={14} />
                        <span>UNVERIFIED</span>
                    </div>
                )}
            </div>

            <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#38bdf8', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Cpu size={14} />
                    Active Strategy Logic
                </h4>
                <p style={{ fontSize: '0.875rem', lineHeight: '1.4', color: '#cbd5e1' }}>
                    {internal_brain_state.notes || "No logic active at this timestamp."}
                </p>
                {internal_brain_state.active_strategies && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                        {internal_brain_state.active_strategies.map(strat => (
                            <span key={strat} style={{ fontSize: '0.7rem', backgroundColor: '#334155', padding: '2px 6px', borderRadius: '4px' }}>
                                {strat}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            <div style={{ borderTop: '1px solid #334155', paddingTop: '0.5rem', fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace' }}>
                ROOT: {session_root ? session_root.substring(0, 16) + '...' : 'N/A'}
            </div>
        </div>
    );
};

export default PedagogicalPopup;
