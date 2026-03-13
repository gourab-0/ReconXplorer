/**
 * Admin Layout with Auth Guard
 * Protects admin routes and ensures only admins can access
 */

"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminLayout } from "@/components/admin/layout/AdminLayout";
import { LoadingState } from "@/components/admin/common/LoadingState";

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayoutWrapper({ children }: AdminLayoutProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Simulate session check
    // In production, this would validate the user's admin status
    const checkAdminStatus = async () => {
      try {
        // For now, we'll assume the user is admin (development mode)
        // In production, check with your auth backend
        
        // Simulated delay to show loading state
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Mock admin check
        const mockIsAdmin = true; // Change to false to test redirect

        if (!mockIsAdmin) {
          router.push("/");
          return;
        }

        setIsAdmin(true);
        setIsLoading(false);
      } catch (error) {
        console.error("[v0] Admin auth check failed:", error);
        router.push("/");
      }
    };

    checkAdminStatus();
  }, [router]);

  // Loading Gate
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black/95">
        <LoadingState message="Verifying admin access..." fullScreen={false} />
      </div>
    );
  }

  // Not Admin Redirect (handled in useEffect)
  if (!isAdmin) {
    return null;
  }

  // Render Admin Layout
  return <AdminLayout>{children}</AdminLayout>;
}
