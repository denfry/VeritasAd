import { UnifiedLayout } from "@/components/UnifiedLayout"

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <UnifiedLayout>{children}</UnifiedLayout>
}
