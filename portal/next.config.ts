import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static HTML export — no Node.js server needed
  output: "export",

  // Clean URLs on static hosting (e.g., /dashboard/ instead of /dashboard)
  trailingSlash: true,

  // Required for static export — skip server-side image optimization
  images: {
    unoptimized: true,
  },

  // React compiler for performance
  reactCompiler: true,
};

export default nextConfig;
