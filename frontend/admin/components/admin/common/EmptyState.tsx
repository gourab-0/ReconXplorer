/**
 * Empty State Component
 * Displayed when no data is available
 */

import { ReactNode } from "react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-4xl text-cyan-400/30 mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-500 text-sm text-center max-w-md mb-6">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="outline" size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
