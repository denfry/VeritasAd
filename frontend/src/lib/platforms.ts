import { Youtube, Send, Instagram, Video, Globe } from 'lucide-react'
import { LucideIcon } from 'lucide-react'

export type PlatformType = 'youtube' | 'telegram' | 'instagram' | 'tiktok' | 'vk' | 'url' | 'file'

export function getPlatformType(url: string | null): PlatformType {
  if (!url) return 'file'
  
  const lower = url.toLowerCase()
  if (lower.includes('youtube.com') || lower.includes('youtu.be')) return 'youtube'
  if (lower.includes('t.me') || lower.includes('telegram.org')) return 'telegram'
  if (lower.includes('instagram.com') || lower.includes('instagr.am')) return 'instagram'
  if (lower.includes('tiktok.com')) return 'tiktok'
  if (lower.includes('vk.com') || lower.includes('vk.ru')) return 'vk'
  return 'url'
}

export function getPlatformInfo(type: PlatformType): { name: string; icon: LucideIcon; color: string } {
  switch (type) {
    case 'youtube':
      return { name: 'YouTube', icon: Youtube, color: 'text-red-500' }
    case 'telegram':
      return { name: 'Telegram', icon: Send, color: 'text-blue-500' }
    case 'instagram':
      return { name: 'Instagram', icon: Instagram, color: 'text-pink-500' }
    case 'tiktok':
      return { name: 'TikTok', icon: Video, color: 'text-cyan-500' }
    case 'vk':
      return { name: 'VK', icon: Globe, color: 'text-indigo-500' }
    default:
      return { name: 'URL', icon: Globe, color: 'text-muted-foreground' }
  }
}

export function getPlatformIcon(url: string | null): { icon: LucideIcon; color: string; name: string } {
  const type = getPlatformType(url)
  return getPlatformInfo(type)
}
