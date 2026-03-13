/**
 * Admin Page Container
 * Standard wrapper for all admin pages ensuring consistent layout and spacing
 */

import { ReactNode } from "react";
import { UI_CONSTANTS } from "@/lib/constants";

interface AdminPageContainerProps {
  children: ReactNode;
  title?: string;
  description?: string;
  icon?: ReactNode;
}

export function AdminPageContainer({
  children,
  title,
  description,
  icon,
}: AdminPageContainerProps) {
  return (
    <main className={`${UI_CONSTANTS.PADDING.PAGE} mx-auto ${UI_CONSTANTS.CONTENT_MAX_WIDTH}`}>
      {/* Page Header */}
      {(title || description) && (
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            {icon && <div className="text-2xl text-cyan-400">{icon}</div>}
            {title && (
              <h1 className="text-3xl font-bold text-white">{title}</h1>
            )}
          </div>
          {description && (
            <p className="text-gray-400 text-sm">{description}</p>
          )}
        </div>
      )}

      {/* Page Content */}
      <div className="space-y-6">{children}</div>
    </main>
  );
}
