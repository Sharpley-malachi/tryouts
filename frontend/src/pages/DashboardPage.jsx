import React, { useState } from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';
import CommandCenter from '../components/dashboard/CommandCenter';
import PredictionView from '../components/dashboard/PredictionView';
import PendingGateway from '../components/dashboard/PendingGateway';
import LivingLibrary from '../components/dashboard/LivingLibrary';
import EpistemicArchive from '../components/dashboard/EpistemicArchive';
import { api } from '../services/api';

const DashboardPage = () => {
    const [activeTab, setActiveTab] = useState('command'); // command, pending, archive, library
    const [analysisResult, setAnalysisResult] = useState(null);

    const handleAnalyze = async (data) => {
        // Trigger Analysis via API (Simulated)
        console.log("Analyzing...", data);
        try {
            // const result = await api.triggerAnalysis(data); // Real call

            // Mock Response for UI Demo
            const mockResult = {
                h4: { prediction: { direction: 'BUY', entry: '1.0520', tp: '1.0580', sl: '1.0490' }, data: null },
                daily: { prediction: { direction: 'BUY', entry: '1.0500', tp: '1.0650', sl: '1.0450' }, data: null },
                weekly: { prediction: { direction: 'NEUTRAL', entry: '-', tp: '-', sl: '-' }, data: null },
            };

            setAnalysisResult(mockResult);
            // Stay on command center but show prediction below? 
            // Or switch to a result view? The prompt implies a flow.
            // Let's scroll down or replace view?
            // "Prediction Presentation View" is View 2. 
            // Let's render it below the command center or instead of it.
        } catch (e) {
            console.error(e);
        }
    };

    const renderContent = () => {
        if (activeTab === 'command') {
            return (
                <div>
                    <CommandCenter onAnalyze={handleAnalyze} />
                    {analysisResult && (
                        <div style={{ marginTop: '3rem', borderTop: '1px solid #334155', paddingTop: '2rem' }}>
                            <PredictionView analysisResult={analysisResult} />
                        </div>
                    )}
                </div>
            );
        }
        if (activeTab === 'pending') return <PendingGateway />;
        if (activeTab === 'library') return <LivingLibrary />;
        if (activeTab === 'archive') return <EpistemicArchive />;
        return null;
    };

    return (
        <DashboardLayout activeTab={activeTab} setActiveTab={setActiveTab}>
            {renderContent()}
        </DashboardLayout>
    );
};

export default DashboardPage;
