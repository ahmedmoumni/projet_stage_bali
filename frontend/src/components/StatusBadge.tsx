import React from 'react';
import type { Status } from '../types';

interface StatusBadgeProps {
  status: Status;
}

const statusColors: Record<Status, string> = {
  validated: 'bg-green-100 text-green-800',
  pending_review: 'bg-orange-100 text-orange-800',
};

const statusLabels: Record<Status, string> = {
  validated: 'Validated',
  pending_review: 'Pending Review',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${statusColors[status]}`}>
      {statusLabels[status]}
    </span>
  );
};
