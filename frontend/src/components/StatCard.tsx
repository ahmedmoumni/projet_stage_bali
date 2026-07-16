import React from 'react';
import './StatCard.css';

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  variant: 'blue' | 'teal' | 'green' | 'orange';
}

export const StatCard: React.FC<StatCardProps> = ({ icon, label, value, variant }) => {
  return (
    <div className={`stat-card stat-card-${variant}`}>
      <div className="stat-card-icon">
        {icon}
      </div>
      <div className="stat-card-value">
        {value.toLocaleString()}
      </div>
      <div className="stat-card-label">
        {label}
      </div>
    </div>
  );
};
