import type { MetadataRoute } from "next"

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "VeritasAd",
    short_name: "VeritasAd",
    description: "AI advertising detection for video and social content",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a0a",
    theme_color: "#06b6d4",
    icons: [
      {
        src: "/icon",
        sizes: "192x192",
        type: "image/png",
      },
      {
        src: "/icon",
        sizes: "512x512",
        type: "image/png",
      },
    ],
  }
}
