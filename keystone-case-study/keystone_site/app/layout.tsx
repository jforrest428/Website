import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Keystone Plumbing & Drain — Philadelphia's Trusted Plumber",
  description:
    "Philadelphia's trusted plumber since 2014. Serving the Main Line and western suburbs for plumbing, drain cleaning, water heaters, sewer, sump pumps, and light HVAC.",
  keywords: "plumber Philadelphia, drain cleaning Main Line, water heater replacement PA, emergency plumber Wayne Ardmore",
  openGraph: {
    title: "Keystone Plumbing & Drain",
    description: "Philadelphia's trusted plumber since 2014.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
