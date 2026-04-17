/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export for deploy-frontend hosting (no Node server).
  output: "export",
  trailingSlash: true,
  images: {
    remotePatterns: [],
    unoptimized: true,
  },
};

export default nextConfig;
