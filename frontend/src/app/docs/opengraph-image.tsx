import { ImageResponse } from "next/og"

export const runtime = "edge"
export const size = {
  width: 1200,
  height: 630,
}

export const contentType = "image/png"

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "64px",
          background: "linear-gradient(135deg, hsl(187, 100%, 50%), hsl(24, 100%, 50%))",
          color: "white",
          fontFamily: "Arial, sans-serif",
        }}
      >
        <div style={{ fontSize: "24px", opacity: 0.9 }}>VeritasAd</div>
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div style={{ fontSize: "60px", fontWeight: 800, lineHeight: 1.05 }}>Documentation</div>
          <div style={{ fontSize: "24px", opacity: 0.9 }}>Self-hosted setup guide</div>
        </div>
        <div style={{ fontSize: "16px", opacity: 0.72 }}>veritasad.ai</div>
      </div>
    ),
    size,
  )
}
