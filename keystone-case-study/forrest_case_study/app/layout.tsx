import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "How We'd Rebuild a $2.1M Plumbing Company with AI | Forrest Intelligence",
  description:
    "A full AI implementation case study: four AI products built on Keystone Plumbing's real operational data. Voice receptionist, review replies, re-engagement engine, and daily briefing — with full ROI math.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
