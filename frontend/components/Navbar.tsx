"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getToken } from "@/lib/api";

export default function Navbar() {
  const [authed, setAuthed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setAuthed(!!getToken());
  }, [pathname]);

  return (
    <header className="border-b border-border bg-panel">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-accent font-bold text-lg tracking-tight">GARUDA</span>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Construct Analysis Platform
          </span>
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/dashboard" className="hover:text-accent">
            Dashboard
          </Link>
          {authed ? (
            <button
              className="btn-secondary btn"
              onClick={() => {
                clearToken();
                setAuthed(false);
                router.push("/login");
              }}
            >
              Log out
            </button>
          ) : (
            <Link href="/login" className="btn">
              Log in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
