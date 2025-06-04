import type { Song } from "@/lib/types"
import Image from "next/image"
import { Disc3 } from "lucide-react"

interface NowPlayingInfoDisplayProps {
  currentSong: Song | null
}

export default function NowPlayingInfoDisplay({ currentSong }: NowPlayingInfoDisplayProps) {
  if (!currentSong) {
    return (
      <div className="text-center p-8 flex flex-col items-center justify-center h-64">
        <Disc3 className="w-24 h-24 text-slate-600 animate-pulse" />
        <p className="mt-4 text-slate-400">Kein Song ausgewählt</p>
        <p className="text-xs text-slate-500">Wähle eine Playlist, um zu starten.</p>
      </div>
    )
  }

  return (
    <div className="text-center space-y-4">
      <div className="relative w-64 h-64 mx-auto rounded-lg overflow-hidden shadow-lg shadow-cyan-500/30 border-2 border-cyan-500/50">
        <Image
          src={currentSong.albumArt || "/placeholder.svg"}
          alt={currentSong.title || "Album Cover"}
          width={256}
          height={256}
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors"></div>
      </div>
      <div>
        <h2 className="text-3xl font-semibold text-cyan-300 tracking-wide">{currentSong.title}</h2>
        <p className="text-lg text-slate-300">{currentSong.artist}</p>
      </div>
    </div>
  )
}
