import React from 'react';
import type { Domain } from '../types';

interface DomainBadgeProps {
  domain: Domain | null;
}

const domainColors: Record<Domain, string> = {
  social: 'bg-blue-100 text-blue-800',
  economy: 'bg-green-100 text-green-800',
  infrastructure: 'bg-orange-100 text-orange-800',
  health: 'bg-red-100 text-red-800',
  culture_art: 'bg-purple-100 text-purple-800',
};

const domainLabels: Record<Domain, string> = {
  social: 'Social',
  economy: 'Economy',
  infrastructure: 'Infrastructure',
  health: 'Health',
  culture_art: 'Culture & Art',
};

export const DomainBadge: React.FC<DomainBadgeProps> = ({ domain }) => {
  if (!domain) {
    return <span className="text-gray-500 text-sm">Unknown</span>;
  }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${domainColors[domain]}`}>
      {domainLabels[domain]}
    </span>
  );
};
