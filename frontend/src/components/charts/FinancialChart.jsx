import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const FinancialChart = ({ data, markers, onCrosshairMove, height = 400 }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef();

    useEffect(() => {
        const handleResize = () => {
            if (chartRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: '#1e293b' },
                textColor: '#94a3b8',
            },
            width: chartContainerRef.current.clientWidth,
            height: height,
            grid: {
                vertLines: { color: '#334155' },
                horzLines: { color: '#334155' },
            },
            crosshair: {
                mode: 1, // CrosshairMode.Normal
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        });
        chartRef.current = chart;

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#22c55e',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        });

        candlestickSeries.setData(data);
        if (markers) {
            candlestickSeries.setMarkers(markers);
        }

        chart.subscribeCrosshairMove(onCrosshairMove);

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data, height]); // Re-create on data change (simplified)

    return (
        <div ref={chartContainerRef} style={{ position: 'relative' }} />
    );
};

export default FinancialChart;
