import React from 'react';
import { Pie } from 'react-chartjs-2';
import { ArcElement, CategoryScale, Chart, PieController } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(PieController, ArcElement, CategoryScale);
Chart.unregister(ChartDataLabels);
Chart.register(ChartDataLabels);
export interface PieChartProps {
    data: {
        labels: string[];
        datasets: {
            data: number[];
            backgroundColor: string[];
        }[];
    };
    options: {
        plugins: {
            datalabels: {
                color: string;
                formatter: (value: number, ctx: any) => string;
            };
        };
    };
    title: string;
}

const PieChart: React.FC<PieChartProps> = ({ data, options, title }) => {
    return (
        <div className="p-4 flex flex-col justify-center items-center shadow-md bg-white rounded-lg max-w-sm mx-auto">
            <Pie data={data} options={options} />
            <p className="text-lg font-bold">{title}</p>
        </div>
    );
};

export default PieChart;