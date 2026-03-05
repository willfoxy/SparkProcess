import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SparkProcess — Autonomous AI Innovation",
  description: "Double Diamond AI orchestration powered by LangGraph + AWS Bedrock",
  icons: { icon: "/favicon.svg" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#050816",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-dvh bg-bg-deep text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
