import "./globals.css";
import type { ReactNode } from "react";
export const metadata = { title: "RepoLens", description: "Understand repositories with AI" };
export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
