"use client"

import { useState, useEffect, useRef } from "react"
import {
  PlayCircle,
  PauseCircle,
  Volume2,
  Volume1,
  VolumeX,
  Info,
  ListMusic,
  Rss,
  Landmark,
  Bitcoin,
  TrendingUp,
  AlertTriangle,
  Cpu,
  Mountain,
  Settings2,
  CloudSun,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import ApiInfoModal from "@/components/api-info-modal"
import StartupAnimation from "@/components/startup-animation"
import AudioVisualizerLine from "@/components/audio-visualizer-line"
import SidePanel from "@/components/side-panel"
import PlaylistSelector from "@/components/playlist-selector"
import NewsFeed from "@/components/news-feed"
import PersonaSelectorModal from "@/components/persona-selector-modal"
import type { Persona, ApiStatus, Playlist, Tweet } from "@/lib/types"
import { cn } from "@/lib/utils"

// Personas (Breaking News an Position 1)
const personas: Persona[] = [
  {
    id: "p4", // ID von Breaking News
    name: "Breaking News",
    description: "Welt, Schweiz & Wirtschaft",
    icon: <AlertTriangle className="w-5 h-5" />,
    accentColor: "text-red-500",
    bgColor: "bg-red-600/10",
    borderColor: "border-red-600/30",
    hoverBgColor: "hover:bg-red-600/20",
    glowColor: "bg-red-700",
    secondaryGlowColor: "bg-orange-500",
    visualizerColor: "stroke-red-600",
  },
  {
    id: "p1",
    name: "Züri Style",
    description: "Lokales, Wirtschaft & BTC",
    icon: <Landmark className="w-5 h-5" />,
    accentColor: "text-teal-400",
    bgColor: "bg-teal-500/10",
    borderColor: "border-teal-500/30",
    hoverBgColor: "hover:bg-teal-500/20",
    glowColor: "bg-teal-600",
    secondaryGlowColor: "bg-amber-500",
    visualizerColor: "stroke-teal-500",
  },
  {
    id: "p2",
    name: "Bitcoin OG",
    description: "BTC, Wirtschaft & Tech",
    icon: <Bitcoin className="w-5 h-5" />,
    accentColor: "text-orange-400",
    bgColor: "bg-orange-500/10",
    borderColor: "border-orange-500/30",
    hoverBgColor: "hover:bg-orange-500/20",
    glowColor: "bg-orange-600",
    secondaryGlowColor: "bg-yellow-500",
    visualizerColor: "stroke-orange-500",
  },
  {
    id: "p3",
    name: "TradFi News",
    description: "Wirtschaft, Politik & BTC",
    icon: <TrendingUp className="w-5 h-5" />,
    accentColor: "text-sky-400",
    bgColor: "bg-sky-500/10",
    borderColor: "border-sky-500/30",
    hoverBgColor: "hover:bg-sky-500/20",
    glowColor: "bg-sky-600",
    secondaryGlowColor: "bg-slate-400",
    visualizerColor: "stroke-sky-500",
  },
  {
    id: "p5",
    name: "Tech Insider",
    description: "Tech, BTC & Wirtschaft",
    icon: <Cpu className="w-5 h-5" />,
    accentColor: "text-cyan-400",
    bgColor: "bg-cyan-500/10",
    borderColor: "border-cyan-500/30",
    hoverBgColor: "hover:bg-cyan-500/20",
    glowColor: "bg-cyan-600",
    secondaryGlowColor: "bg-purple-500",
    visualizerColor: "stroke-cyan-500",
  },
  {
    id: "p6",
    name: "Swiss Local",
    description: "Schweiz, Sport & Wirtschaft",
    icon: <Mountain className="w-5 h-5" />,
    accentColor: "text-emerald-500",
    bgColor: "bg-emerald-600/10",
    borderColor: "border-emerald-600/30",
    hoverBgColor: "hover:bg-emerald-600/20",
    glowColor: "bg-emerald-700",
    secondaryGlowColor: "bg-lime-500",
    visualizerColor: "stroke-emerald-600",
  },
]

const initialDefaultPersona = personas[0]

const mockPlaylists: Playlist[] = [
  { id: "pl1", name: "Breaking News Mix", songs: [] },
  { id: "pl2", name: "Züri Beats", songs: [] },
  { id: "pl3", name: "Bitcoin Focus", songs: [] },
  { id: "pl4", name: "Tech Trends Audio", songs: [] },
]

const generateMockNews = (count: number): Tweet[] => {
  const newsSources = [
    { user: "@GlobalTimes", avatarQuery: "global news icon" },
    { user: "@TechReport", avatarQuery: "tech news icon" },
    { user: "@FinanceDaily", avatarQuery: "finance news icon" },
    { user: "@SwissUpdate", avatarQuery: "swiss flag icon" },
    { user: "@CryptoNews", avatarQuery: "bitcoin icon" },
  ]
  const newsItems: Tweet[] = []
  for (let i = 0; i < count; i++) {
    const source = newsSources[i % newsSources.length]
    newsItems.push({
      id: `n${Date.now() + i}`,
      user: source.user,
      content: `Schlagzeile ${i + 1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.`,
      timestamp: `${Math.floor(Math.random() * 50) + 1}m`,
      avatar: `/placeholder.svg?height=32&width=32&query=${source.avatarQuery}`,
    })
  }
  return newsItems
}

const mockNews = generateMockNews(10)

const zurichWeather = {
  temp: "18°C",
  condition: "Sonnig",
  icon: <CloudSun className="w-5 h-5 text-yellow-400" />, // Icon-Größe angepasst für Info-Block
}

const bitcoinPrice = {
  price: "68,420 USD",
  change: "+2.5%",
  changeColor: "text-green-400",
  icon: <Bitcoin className="w-5 h-5 text-yellow-500" />, // Icon-Größe angepasst für Info-Block
}

export default function RadioAppFullscreen() {
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [currentPersona, setCurrentPersona] = useState<Persona>(initialDefaultPersona)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [volume, setVolume] = useState<number>(0.75)
  const [progress, setProgress] = useState<number>(0)
  const [currentShow, setCurrentShow] = useState({
    title: `${initialDefaultPersona.name} Stream`,
    artist: "RadioX AI",
  })
  const [isApiModalOpen, setIsApiModalOpen] = useState<boolean>(false)
  const [isPlaylistPanelOpen, setIsPlaylistPanelOpen] = useState<boolean>(false)
  const [isNewsPanelOpen, setIsNewsPanelOpen] = useState<boolean>(false)
  const [isPersonaModalOpen, setIsPersonaModalOpen] = useState<boolean>(false)

  const appRef = useRef<HTMLDivElement>(null)
  const targetMousePosition = useRef({ x: 0.5, y: 0.5 })
  const animatedGlow1Position = useRef({ x: 0.5, y: 0.5 })
  const animatedGlow2Position = useRef({ x: 0.5, y: 0.5 })
  const [, forceRender] = useState({})

  const apiStatus: ApiStatus = {
    spotify: { connected: true, lastChecked: new Date().toLocaleTimeString() },
    twitter: { connected: true, message: "Streaming live updates", lastChecked: new Date().toLocaleTimeString() },
    elevenLabs: { connected: false, error: "API Key not set", lastChecked: new Date().toLocaleTimeString() },
  }

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 2500)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying && !isLoading) {
      interval = setInterval(() => {
        setProgress((p) => (p >= 100 ? 0 : p + 1))
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying, isLoading])

  const handlePersonaSelect = (persona: Persona) => {
    setCurrentPersona(persona)
    setCurrentShow({ title: `${persona.name} Stream`, artist: "RadioX AI" })
    setIsPlaying(true)
    setProgress(0)
    console.log(
      `%c[RadioX AI]%c Playing ${persona.name} persona audio cue... (Simulated - Intro: "${getPersonaIntro(persona.name)}")`,
      "color: #8B5CF6; font-weight: bold;",
      "color: inherit;",
    )
    setIsPersonaModalOpen(false)
  }

  const getPersonaIntro = (personaName: string): string => {
    switch (personaName) {
      case "Züri Style":
        return "Grüezi Zürich! Hier sind eure lokalen News..."
      case "Bitcoin OG":
        return "Stack sats, stay humble! Hier sind die Bitcoin News..."
      case "TradFi News":
        return "Willkommen zu Ihrem Finanzüberblick."
      case "Breaking News":
        return "Breaking: Hier sind die neuesten Entwicklungen..."
      case "Tech Insider":
        return "Hey Tech Community! Hier sind die neuesten Updates..."
      case "Swiss Local":
        return "Hallo Schweiz! Hier sind eure lokalen Nachrichten..."
      default:
        return "RadioX AI startet..."
    }
  }

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (appRef.current) {
        const rect = appRef.current.getBoundingClientRect()
        targetMousePosition.current = {
          x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
          y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
        }
      } else {
        targetMousePosition.current = {
          x: Math.max(0, Math.min(1, event.clientX / window.innerWidth)),
          y: Math.max(0, Math.min(1, event.clientY / window.innerHeight)),
        }
      }
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  useEffect(() => {
    let animationFrameId: number
    const animateGlows = () => {
      const easingFactor1 = 0.05
      const easingFactor2 = 0.025
      animatedGlow1Position.current.x +=
        (targetMousePosition.current.x - animatedGlow1Position.current.x) * easingFactor1
      animatedGlow1Position.current.y +=
        (targetMousePosition.current.y - animatedGlow1Position.current.y) * easingFactor1
      animatedGlow2Position.current.x +=
        (targetMousePosition.current.x - animatedGlow2Position.current.x) * easingFactor2
      animatedGlow2Position.current.y +=
        (targetMousePosition.current.y - animatedGlow2Position.current.y) * easingFactor2
      forceRender({})
      animationFrameId = requestAnimationFrame(animateGlows)
    }
    if (!isLoading) {
      animationFrameId = requestAnimationFrame(animateGlows)
    }
    return () => cancelAnimationFrame(animationFrameId)
  }, [isLoading])

  const VolumeIcon = volume === 0 ? VolumeX : volume < 0.5 ? Volume1 : Volume2
  if (isLoading) {
    return <StartupAnimation />
  }

  const glow1Dx = animatedGlow1Position.current.x - 0.5
  const glow1Dy = animatedGlow1Position.current.y - 0.5
  const glow1Transform = `translate(${glow1Dx * 70}px, ${glow1Dy * 70}px) scale(1.15)`
  const glow2Dx = animatedGlow2Position.current.x - 0.5
  const glow2Dy = animatedGlow2Position.current.y - 0.5
  const glow2Transform = `translate(${glow2Dx * 40}px, ${glow2Dy * 40}px) scale(0.95)`
  const currentVisualizerBgClass = personas
    .find((p) => p.id === currentPersona.id)
    ?.visualizerColor?.replace("stroke-", "bg-")
  const currentVisualizerBorderClass = personas
    .find((p) => p.id === currentPersona.id)
    ?.visualizerColor?.replace("stroke-", "border-")

  return (
    <div
      ref={appRef}
      className="flex flex-col h-full p-3 sm:p-4 md:p-6 items-center justify-between relative font-sans overflow-hidden"
    >
      {/* Background Glows */}
      <div
        className={cn(
          "absolute w-1/2 h-1/2 rounded-full opacity-15 sm:opacity-20 blur-[100px] sm:blur-[150px] transition-colors duration-1000",
          currentPersona.glowColor,
        )}
        style={{ top: "20%", left: "20%", transform: glow1Transform }}
      />
      <div
        className={cn(
          "absolute w-1/2 h-1/2 rounded-full opacity-15 sm:opacity-20 blur-[100px] sm:blur-[150px] transition-colors duration-1000",
          currentPersona.secondaryGlowColor,
        )}
        style={{ bottom: "20%", right: "20%", transform: glow2Transform }}
      />

      {/* Header */}
      <header className="w-full max-w-5xl grid grid-cols-[1fr_auto_1fr] items-center gap-2 sm:gap-4 z-10 pt-2 md:pt-0 flex-shrink-0 px-1">
        {/* Empty Left Block (for spacing, keeps logo centered) */}
        <div className="w-10 sm:w-16"></div> {/* Placeholder for width of old info block */}
        {/* Logo Block - Centered by the grid structure */}
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tighter text-slate-100 relative">
            RADIO<span className={cn("transition-colors duration-500", currentPersona.accentColor)}>X</span>
            <span
              className={cn(
                "absolute -top-1 -right-3 text-sm font-mono transition-colors duration-500",
                currentPersona.accentColor,
              )}
            >
              AI
            </span>
          </h1>
        </div>
        {/* Right Settings Button */}
        <div className="flex justify-end">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsPersonaModalOpen(true)}
            className={cn(
              "text-slate-300 hover:text-white transition-colors rounded-lg bg-slate-800/50 hover:bg-slate-700/70 backdrop-blur-sm border border-slate-700/50 p-2",
              currentPersona.accentColor,
            )}
            title="Sender wechseln"
          >
            <Settings2 className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
        </div>
      </header>
      <p className="text-slate-400 mt-1 text-xs text-center z-10 sm:hidden">
        Now: <span className={cn("font-semibold", currentPersona.accentColor)}>{currentPersona.name}</span>
      </p>

      {/* Main Content Area */}
      <main className="flex flex-col items-center space-y-3 sm:space-y-4 md:space-y-6 z-10 w-full max-w-md sm:max-w-lg md:max-w-xl overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 hover:scrollbar-thumb-slate-600 scrollbar-track-transparent py-2 sm:py-4 flex-grow">
        {/* Player Section */}
        <section className="w-full bg-slate-800/60 backdrop-blur-lg p-3 sm:p-4 md:p-6 rounded-xl shadow-2xl border border-slate-700/50 flex-shrink-0">
          <div className="text-center mb-2 sm:mb-3">
            <p className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider">Now Playing</p>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold text-slate-100 mt-0.5 sm:mt-1">
              {currentShow.title}
            </h2>
            <p className={cn("text-xs sm:text-sm transition-colors duration-500", currentPersona.accentColor)}>
              {currentShow.artist}
            </p>
          </div>
          <AudioVisualizerLine
            isPlaying={isPlaying}
            className={cn("my-2 sm:my-3 h-8 sm:h-10 w-full", currentPersona.visualizerColor)}
          />
          <div className="w-full h-1 sm:h-1.5 bg-slate-700 rounded-full overflow-hidden my-2 sm:my-3">
            <div
              className={cn("h-full transition-all duration-500 ease-linear", currentVisualizerBgClass)}
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4">
            <span>{new Date(progress * 1000).toISOString().substr(14, 5)}</span>
            <span>{new Date(100 * 1000).toISOString().substr(14, 5)}</span>
          </div>
          <div className="flex items-center justify-center space-x-4 sm:space-x-6">
            <Button
              variant="ghost"
              size="icon"
              className="text-slate-400 hover:text-white transition-colors"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? (
                <PauseCircle className="w-12 h-12 sm:w-16 sm:h-16" />
              ) : (
                <PlayCircle className="w-12 h-12 sm:w-16 sm:h-16" />
              )}
            </Button>
          </div>
          <div className="flex items-center space-x-1.5 sm:space-x-2 mt-3 sm:mt-4">
            <VolumeIcon className="w-4 h-4 sm:w-5 sm:h-5 text-slate-400" />
            <Slider
              defaultValue={[volume * 100]}
              max={100}
              step={1}
              onValueChange={(value) => setVolume(value[0] / 100)}
              className={cn(
                "[&>span:first-child]:h-full",
                "[&>.rc-slider-track]:h-full",
                `[&>span:first-child]:${currentVisualizerBgClass}`,
                `[&>.rc-slider-handle]:${currentVisualizerBorderClass}`,
              )}
            />
            <span className="text-[10px] sm:text-xs text-slate-400 w-7 sm:w-8 text-right">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </section>

        {/* Info Block (Wetter & Preis) - NEU */}
        <section className="w-full max-w-xs sm:max-w-sm bg-slate-800/50 backdrop-blur-sm p-3 sm:p-4 rounded-lg border border-slate-700/50 flex-shrink-0">
          <div className="flex justify-around items-center text-xs sm:text-sm text-slate-300">
            <div className="flex items-center" title={`Wetter in Zürich: ${zurichWeather.condition}`}>
              {zurichWeather.icon}
              <span className="ml-1.5 sm:ml-2">
                {zurichWeather.temp}, {zurichWeather.condition}
              </span>
            </div>
            <div className="border-l border-slate-600 h-5 sm:h-6 mx-2 sm:mx-3"></div>
            <div className="flex items-center" title={`Bitcoin Preis: ${bitcoinPrice.price} (${bitcoinPrice.change})`}>
              {bitcoinPrice.icon}
              <span className="ml-1.5 sm:ml-2">{bitcoinPrice.price}</span>
              <span className={cn("ml-1 sm:ml-1.5 text-[10px] sm:text-xs", bitcoinPrice.changeColor)}>
                {bitcoinPrice.change}
              </span>
            </div>
          </div>
        </section>

        {/* News Feed Section (Swipeable) */}
        <section className="w-full bg-slate-800/50 backdrop-blur-md p-3 sm:p-4 rounded-xl shadow-lg border border-slate-700/40 flex-shrink-0">
          <h3 className="text-base sm:text-lg font-semibold text-purple-400 mb-2 sm:mb-3 flex items-center justify-between">
            <span className="flex items-center">
              <Rss className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
              Aktuelle Stunde
            </span>
          </h3>
          <NewsFeed tweets={mockNews} />
        </section>

        <div className="w-full max-w-md text-center bg-slate-800/70 backdrop-blur-sm py-1 px-2 sm:py-1.5 sm:px-3 rounded-md border border-slate-700 flex-shrink-0">
          <p className="text-[10px] sm:text-xs text-slate-300">Demo Mode - Pre-generated Shows Only</p>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-5xl flex flex-col sm:flex-row justify-center sm:justify-between items-center gap-2 text-xs text-slate-400 border-t border-slate-700/50 pt-2 sm:pt-3 mt-auto z-10 pb-2 md:pb-0 flex-shrink-0">
        <p className="hidden sm:block text-slate-500 text-[10px]">
          RadioX AI - Persona:{" "}
          <span className={cn("font-semibold", currentPersona.accentColor)}>{currentPersona.name}</span>
        </p>
        <div className="flex items-center space-x-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPlaylistPanelOpen(true)}
            className="text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors px-1.5 sm:px-2 py-1"
          >
            <ListMusic className="w-3 h-3 sm:w-3.5 sm:h-3.5 mr-1" />{" "}
            <span className="text-[10px] sm:text-xs">Playlists</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsNewsPanelOpen(true)}
            className="text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors px-1.5 sm:px-2 py-1"
          >
            <Rss className="w-3 h-3 sm:w-3.5 sm:h-3.5 mr-1" />{" "}
            <span className="text-[10px] sm:text-xs">News Archiv</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsApiModalOpen(true)}
            className="text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors px-1.5 sm:px-2 py-1"
          >
            <Info className="w-3 h-3 sm:w-3.5 sm:h-3.5 mr-1" />{" "}
            <span className="text-[10px] sm:text-xs">API Status</span>
          </Button>
        </div>
      </footer>

      <ApiInfoModal isOpen={isApiModalOpen} onClose={() => setIsApiModalOpen(false)} apiStatus={apiStatus} />
      <PersonaSelectorModal
        isOpen={isPersonaModalOpen}
        onClose={() => setIsPersonaModalOpen(false)}
        personas={personas}
        currentPersonaId={currentPersona.id}
        onPersonaSelect={handlePersonaSelect}
      />
      <SidePanel
        title="Playlists"
        isOpen={isPlaylistPanelOpen}
        onClose={() => setIsPlaylistPanelOpen(false)}
        position="left"
      >
        <PlaylistSelector
          playlists={mockPlaylists}
          selectedPlaylistId={""}
          onSelect={(id) => console.log("Playlist selected:", id)}
        />
      </SidePanel>
      <SidePanel
        title="Nachrichten-Archiv"
        isOpen={isNewsPanelOpen}
        onClose={() => setIsNewsPanelOpen(false)}
        position="right"
      >
        <NewsFeed tweets={generateMockNews(20)} isArchiveView={true} />
      </SidePanel>
    </div>
  )
}
