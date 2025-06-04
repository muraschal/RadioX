"use client"

import { useState, useEffect } from "react"
import PlayerArea from "@/components/player-area"
import SidebarArea from "@/components/sidebar-area"
import type { Song, Playlist, Tweet, Persona } from "@/lib/types"
import { UserCircle } from "lucide-react"

const initialPlaylists: Playlist[] = [
  {
    id: "pl1",
    name: "Cyberpunk Beats 🔥",
    songs: [
      { id: "s1", title: "Resonance", artist: "Home", albumArt: "/placeholder.svg?height=100&width=100" },
      { id: "s2", title: "Nightcall", artist: "Kavinsky", albumArt: "/placeholder.svg?height=100&width=100" },
    ],
  },
  {
    id: "pl2",
    name: "Bitcoin Maximalist Anthems 🚀",
    songs: [
      { id: "s3", title: "Stack Sats", artist: "Crypto Crew", albumArt: "/placeholder.svg?height=100&width=100" },
      {
        id: "s4",
        title: "Digital Gold",
        artist: "Satoshi's Disciples",
        albumArt: "/placeholder.svg?height=100&width=100",
      },
    ],
  },
  {
    id: "pl3",
    name: "Retro Wave Classics 📼",
    songs: [
      { id: "s5", title: "Blade Runner Blues", artist: "Vangelis", albumArt: "/placeholder.svg?height=100&width=100" },
      { id: "s6", title: "Turbo Killer", artist: "Carpenter Brut", albumArt: "/placeholder.svg?height=100&width=100" },
    ],
  },
]

const initialTweets: Tweet[] = [
  {
    id: "t1",
    user: "@tech_crunch",
    content: "Neues KI-Modell revolutioniert die Softwareentwicklung. Mehr Details in Kürze!",
    timestamp: "Vor 5 Min.",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "t2",
    user: "@global_news",
    content: "Wichtige Entwicklungen auf der internationalen Bühne. Analysten diskutieren die Auswirkungen.",
    timestamp: "Vor 12 Min.",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "t3",
    user: "@art_updates",
    content: "Spannende neue Ausstellung im digitalen Kunstmuseum eröffnet heute.",
    timestamp: "Vor 25 Min.",
    avatar: "/placeholder.svg?height=40&width=40",
  },
]

const initialPersonas: Persona[] = [
  {
    id: "p1",
    name: "Maximalist Max",
    description: "Frech, direkt, Bitcoin-maximalistisch",
    icon: <UserCircle className="w-5 h-5 mr-2 text-orange-400" />,
  },
  {
    id: "p2",
    name: "Cyberpunk Cyra",
    description: "Dystopisch, tech-fokussiert, Matrix-Style",
    icon: <UserCircle className="w-5 h-5 mr-2 text-cyan-400" />,
  },
  {
    id: "p3",
    name: "Retro Rick",
    description: "80s Nostalgie mit Bitcoin-Twist",
    icon: <UserCircle className="w-5 h-5 mr-2 text-pink-400" />,
  },
]

export default function RadioInterface() {
  const [currentSong, setCurrentSong] = useState<Song | null>(initialPlaylists[0].songs[0])
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [volume, setVolume] = useState<number>(0.7)
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist>(initialPlaylists[0])
  const [tweets, setTweets] = useState<Tweet[]>(initialTweets)
  const [selectedPersona, setSelectedPersona] = useState<Persona>(initialPersonas[1]) // Cyberpunk Cyra default

  const handlePlayPause = () => setIsPlaying(!isPlaying)
  const handleNextSong = () => {
    if (!currentSong) return
    const currentPlaylist = initialPlaylists.find((p) => p.id === selectedPlaylist.id)
    if (!currentPlaylist) return
    const currentIndex = currentPlaylist.songs.findIndex((s) => s.id === currentSong.id)
    const nextIndex = (currentIndex + 1) % currentPlaylist.songs.length
    setCurrentSong(currentPlaylist.songs[nextIndex])
  }
  const handlePrevSong = () => {
    if (!currentSong) return
    const currentPlaylist = initialPlaylists.find((p) => p.id === selectedPlaylist.id)
    if (!currentPlaylist) return
    const currentIndex = currentPlaylist.songs.findIndex((s) => s.id === currentSong.id)
    const prevIndex = (currentIndex - 1 + currentPlaylist.songs.length) % currentPlaylist.songs.length
    setCurrentSong(currentPlaylist.songs[prevIndex])
  }

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume)
    // Hier würde die Logik zur Lautstärkeregelung des Audio-Players stehen
    console.log("Volume changed to:", newVolume)
  }

  const handlePlaylistSelect = (playlistId: string) => {
    const playlist = initialPlaylists.find((p) => p.id === playlistId)
    if (playlist) {
      setSelectedPlaylist(playlist)
      setCurrentSong(playlist.songs[0] || null)
      setIsPlaying(true) // Auto-play new playlist
    }
  }

  const handlePersonaSelect = (personaId: string) => {
    const persona = initialPersonas.find((p) => p.id === personaId)
    if (persona) {
      setSelectedPersona(persona)
      // Hier könnte Logik stehen, um den Radiostil basierend auf der Persona zu ändern
      console.log("Persona selected:", persona.name)
    }
  }

  // Simulate new tweets appearing
  useEffect(() => {
    const interval = setInterval(() => {
      const newTweet: Tweet = {
        id: `t${Date.now()}`,
        user: "@random_updates",
        content: `Interessante Neuigkeiten aus aller Welt! (Simulierter Tweet #${Math.floor(Math.random() * 100)})`,
        timestamp: "Gerade eben",
        avatar: "/placeholder.svg?height=40&width=40",
      }
      setTweets((prevTweets) => [newTweet, ...prevTweets.slice(0, 4)])
    }, 30000) // Alle 30 Sekunden ein neuer Tweet
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="w-full max-w-5xl bg-slate-800/50 backdrop-blur-md shadow-2xl shadow-purple-500/30 rounded-xl overflow-hidden border border-slate-700">
      <div className="p-2 bg-slate-900/70 text-center">
        <h1 className="text-2xl font-bold tracking-wider text-cyan-400 uppercase">
          RadioX <span className="text-xs text-pink-500 align-super">AI</span>
        </h1>
        <p className="text-xs text-slate-400">
          Persona: {selectedPersona.name} - {selectedPersona.description}
        </p>
      </div>
      <div className="md:flex">
        <PlayerArea
          currentSong={currentSong}
          isPlaying={isPlaying}
          volume={volume}
          onPlayPause={handlePlayPause}
          onNext={handleNextSong}
          onPrev={handlePrevSong}
          onVolumeChange={handleVolumeChange}
        />
        <SidebarArea
          playlists={initialPlaylists}
          selectedPlaylistId={selectedPlaylist.id}
          onPlaylistSelect={handlePlaylistSelect}
          tweets={tweets}
          personas={initialPersonas}
          selectedPersonaId={selectedPersona.id}
          onPersonaSelect={handlePersonaSelect}
        />
      </div>
    </div>
  )
}
