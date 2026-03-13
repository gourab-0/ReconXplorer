/**
 * Loading State Component
 * Displayed while data is loading or being fetched
 */

import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  fullScreen?: boolean;
}

export function LoadingState({
  message = "Loading...",
  fullScreen = false,
}: LoadingStateProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
      <p className="text-gray-300 text-sm">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-12">
      {content}
    </div>
  );
}

/**
 * Skeleton loader for data tables
 */
export function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-800/50 rounded-lg animate-pulse" />
      ))}
    </div>
  );
}

/**
 * Skeleton loader for stats cards
 */
export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="h-32 bg-gray-800/50 rounded-lg animate-pulse"
        />
      ))}
    </div>
  );
}
