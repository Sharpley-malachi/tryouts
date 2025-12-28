import React from 'react';
import { FileText, Download } from 'lucide-react';

const LivingLibrary = () => {
    const docs = [
        { title: 'The Architect\'s Journal - Vol 1', type: 'PDF', date: '2025-12-20' },
        { title: 'Strategy DNA: FVG Reversals', type: 'PDF', date: '2025-12-22' },
        { title: 'Market Regime Report: Q4', type: 'DOCX', date: '2025-12-25' },
    ];

    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '2rem', color: '#818cf8' }}>Epistemic Living Library</h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1.5rem' }}>
                {docs.map((doc, idx) => (
                    <div key={idx} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ padding: '0.5rem', backgroundColor: '#312e81', borderRadius: '0.5rem', width: 'fit-content' }}>
                            <FileText size={24} color="#a5b4fc" />
                        </div>
                        <div>
                            <h4 style={{ fontWeight: 'bold', color: '#e2e8f0', marginBottom: '0.25rem' }}>{doc.title}</h4>
                            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{doc.date} • {doc.type}</span>
                        </div>
                        <button style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem', border: '1px solid #475569', backgroundColor: 'transparent', color: '#cbd5e1', borderRadius: '0.5rem', cursor: 'pointer' }}>
                            <Download size={16} /> Download
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LivingLibrary;
