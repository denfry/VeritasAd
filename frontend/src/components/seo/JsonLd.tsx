"use client"

import Script from "next/script"

type JsonLdData = Record<string, unknown> | Array<Record<string, unknown>>

export function JsonLd({ data }: { data: JsonLdData }) {
  const id = `jsonld-${JSON.stringify(data).length}`
  return (
    <Script
      id={id}
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}
