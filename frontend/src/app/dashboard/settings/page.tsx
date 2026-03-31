"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Tabs } from "@/components/ui/Tabs"
import { ThreeScene } from "@/components/three/ThreeScene"
import {
  Bell,
  Palette,
  Plug,
  Globe,
  Moon,
  Sun,
  Monitor,
  Mail,
  Smartphone,
  Webhook,
  Shield,
  Database,
  Code,
} from "lucide-react"
import { cn } from "@/lib/utils"

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("notifications")

  const tabs = [
    { id: "notifications", label: "Notifications", icon: <Bell className="h-4 w-4" /> },
    { id: "preferences", label: "Preferences", icon: <Palette className="h-4 w-4" /> },
    { id: "integrations", label: "Integrations", icon: <Plug className="h-4 w-4" /> },
  ]

  return (
    <ThreeScene type="neural" intensity="light">
      <motion.div
        initial="hidden"
        animate="show"
        variants={container}
        className="space-y-6"
      >
        <motion.div variants={item}>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage your account preferences and integrations.</p>
        </motion.div>

        <motion.div variants={item}>
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        </motion.div>

        <motion.div variants={item}>
          <div className="rounded-2xl border bg-card/60 backdrop-blur-sm p-6">
            {activeTab === "notifications" && <NotificationsTab />}
            {activeTab === "preferences" && <PreferencesTab />}
            {activeTab === "integrations" && <IntegrationsTab />}
          </div>
        </motion.div>
      </motion.div>
    </ThreeScene>
  )
}

function NotificationsTab() {
  const [toggles, setToggles] = useState({
    emailReports: true,
    emailAlerts: false,
    pushNotifications: true,
    weeklyDigest: true,
    analysisComplete: true,
    securityAlerts: true,
  })

  const toggle = (key: keyof typeof toggles) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const options = [
    { key: "emailReports" as const, label: "Email Reports", description: "Receive detailed analysis reports via email", icon: <Mail className="h-5 w-5" /> },
    { key: "emailAlerts" as const, label: "Email Alerts", description: "Get notified about critical findings immediately", icon: <Mail className="h-5 w-5" /> },
    { key: "pushNotifications" as const, label: "Push Notifications", description: "Browser notifications for real-time updates", icon: <Smartphone className="h-5 w-5" /> },
    { key: "weeklyDigest" as const, label: "Weekly Digest", description: "Summary of all analyses performed each week", icon: <Mail className="h-5 w-5" /> },
    { key: "analysisComplete" as const, label: "Analysis Complete", description: "Notify when video analysis finishes processing", icon: <Smartphone className="h-5 w-5" /> },
    { key: "securityAlerts" as const, label: "Security Alerts", description: "Alerts for suspicious login attempts", icon: <Shield className="h-5 w-5" /> },
  ]

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Notification Preferences</h2>
        <p className="text-muted-foreground text-sm mt-1">Choose how and when you want to be notified.</p>
      </div>
      <div className="divide-y">
        {options.map((opt) => (
          <div key={opt.key} className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-muted/50 text-muted-foreground">
                {opt.icon}
              </div>
              <div>
                <p className="font-medium text-sm">{opt.label}</p>
                <p className="text-muted-foreground text-xs">{opt.description}</p>
              </div>
            </div>
            <button
              onClick={() => toggle(opt.key)}
              className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              aria-pressed={toggles[opt.key]}
            >
              <span
                className={cn(
                  "inline-block h-4 w-4 rounded-full bg-background shadow-sm transition-transform",
                  toggles[opt.key] ? "translate-x-6 bg-primary" : "translate-x-1 bg-muted-foreground"
                )}
              />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function PreferencesTab() {
  const [theme, setTheme] = useState("system")
  const [language, setLanguage] = useState("en")

  const themes = [
    { id: "light", label: "Light", icon: <Sun className="h-4 w-4" /> },
    { id: "dark", label: "Dark", icon: <Moon className="h-4 w-4" /> },
    { id: "system", label: "System", icon: <Monitor className="h-4 w-4" /> },
  ]

  const languages = [
    { id: "en", label: "English" },
    { id: "zh", label: "中文" },
    { id: "es", label: "Español" },
    { id: "fr", label: "Français" },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Appearance & Language</h2>
        <p className="text-muted-foreground text-sm mt-1">Customize the look and feel of your dashboard.</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-3 block">Theme</label>
          <div className="grid grid-cols-3 gap-2">
            {themes.map((t) => (
              <button
                key={t.id}
                onClick={() => setTheme(t.id)}
                className={cn(
                  "flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium transition-all",
                  theme === t.id
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-transparent text-muted-foreground hover:bg-muted/50"
                )}
              >
                {t.icon}
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium mb-3 block">Language</label>
          <div className="grid grid-cols-2 gap-2">
            {languages.map((l) => (
              <button
                key={l.id}
                onClick={() => setLanguage(l.id)}
                className={cn(
                  "flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium transition-all",
                  language === l.id
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-transparent text-muted-foreground hover:bg-muted/50"
                )}
              >
                <Globe className="h-4 w-4" />
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function IntegrationsTab() {
  const integrations = [
    { name: "Slack", description: "Send analysis reports to Slack channels", icon: <Webhook className="h-6 w-6" />, connected: false },
    { name: "Discord", description: "Post notifications to Discord servers", icon: <Webhook className="h-6 w-6" />, connected: false },
    { name: "Google Drive", description: "Save reports directly to Google Drive", icon: <Database className="h-6 w-6" />, connected: true },
    { name: "Zapier", description: "Automate workflows with Zapier", icon: <Code className="h-6 w-6" />, connected: false },
  ]

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Connected Integrations</h2>
        <p className="text-muted-foreground text-sm mt-1">Connect third-party services to extend functionality.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {integrations.map((integration) => (
          <div
            key={integration.name}
            className="flex items-center justify-between rounded-xl border bg-muted/20 p-4"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-muted/50 text-muted-foreground">
                {integration.icon}
              </div>
              <div>
                <p className="font-medium text-sm">{integration.name}</p>
                <p className="text-muted-foreground text-xs">{integration.description}</p>
              </div>
            </div>
            <button
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                integration.connected
                  ? "bg-primary/10 text-primary hover:bg-primary/20"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              )}
            >
              {integration.connected ? "Connected" : "Connect"}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
