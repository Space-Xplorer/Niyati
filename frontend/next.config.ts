import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // For Docker deployment, use standalone output
  output: process.env.DOCKER_BUILD === "true" ? "standalone" : "export",

  // Clean URLs on static hosting
  trailingSlash: true,

  // Image optimization
  images: {
    unoptimized: process.env.DOCKER_BUILD !== "true",
  },

  // React compiler for performance
  reactCompiler: true,
};

export default nextConfig;
