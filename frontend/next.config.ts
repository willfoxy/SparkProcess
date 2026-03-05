import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

// Rewrites are only used in local dev when NEXT_PUBLIC_API_URL is not set.
// On Vercel the client calls the backend directly (see lib/api.ts) so that
// SSE (EventSource) streaming is not buffered by Vercel's rewrite layer.
if (!process.env.NEXT_PUBLIC_API_URL) {
  nextConfig.rewrites = async () => [
    { source: "/api/:path*", destination: "http://localhost:8000/api/:path*" },
  ];
}

export default nextConfig;
