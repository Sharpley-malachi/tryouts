import React, { useState } from 'react';
import './DashboardLayout.css';
import { LayoutDashboard, Clock, History, BookOpen, ShieldCheck } from 'lucide-react';

const DashboardLayout = ({ children, activeTab, setActiveTab }) => {
    return (
        <div className="layout-container">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <ShieldCheck size={24} />
                    <span>Truth Engine</span>
                </div>

                <nav>
                    <div
                        className={`nav-item ${activeTab === 'command' ? 'active' : ''}`}
                        onClick={() => setActiveTab('command')}
                    >
                        <LayoutDashboard size={20} />
                        <span>Command Center</span>
                    </div>

                    <div
                        className={`nav-item ${activeTab === 'pending' ? 'active' : ''}`}
                        onClick={() => setActiveTab('pending')}
                    >
                        <Clock size={20} />
                        <span>Pending Gateway</span>
                    </div>

                    <div
                        className={`nav-item ${activeTab === 'archive' ? 'active' : ''}`}
                        onClick={() => setActiveTab('archive')}
                    >
                        <History size={20} />
                        <span>Epistemic Archive</span>
                    </div>

                    <div
                        className={`nav-item ${activeTab === 'library' ? 'active' : ''}`}
                        onClick={() => setActiveTab('library')}
                    >
                        <BookOpen size={20} />
                        <span>Living Library</span>
                    </div>
                </nav>
            </aside>
            <main className="main-content">
                {children}
            </main>
        </div>
    );
};

export default DashboardLayout;
