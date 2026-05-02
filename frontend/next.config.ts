import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  env: {
    ATLASMIND_API_URL: process.env.ATLASMIND_API_URL ?? "",
  },
};

export default config;
