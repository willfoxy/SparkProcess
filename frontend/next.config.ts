import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Rewrites are only used in local dev when NEXT_PUBLIC_API_URL is not set.
  // On Vercel the client calls the backend directly (see lib/api.ts) so that
  // SSE (EventSource) streaming is not buffered by Vercel's rewrite layer.
  ...(!process.env.NEXT_PUBLIC_API_URL && {
    async rewrites() {
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    },
  }),
};

export default nextConfig;
