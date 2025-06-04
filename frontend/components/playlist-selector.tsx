"use client"

import type { Playlist } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ListMusic, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface PlaylistSelectorProps {
  playlists: Playlist[]
  selectedPlaylistId: string
  onSelect: (playlistId: string) => void
  className?: string
}

export default function PlaylistSelector({
  playlists,
  selectedPlaylistId,
  onSelect,
  className,
}: PlaylistSelectorProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {/* Removed max-h and overflow-y-auto, SidePanel handles scrolling */}
      <div className="space-y-1 pr-1">
        {playlists.map((playlist) => (
          <Button
            key={playlist.id}
            variant={"ghost"}
            onClick={() => onSelect(playlist.id)}
            className={cn(
              `w-full justify-start text-left h-auto py-2.5 px-3 rounded-md transition-all duration-150 ease-in-out
                        text-slate-300 hover:bg-purple-500/20 hover:text-purple-300 focus:bg-purple-500/30 focus:text-purple-200`,
              selectedPlaylistId === playlist.id
                ? "bg-purple-600/30 text-purple-200 border border-purple-500/70"
                : "border border-transparent",
            )}
          >
            {selectedPlaylistId === playlist.id && (
              <CheckCircle2 className="w-4 h-4 mr-2 text-purple-300 flex-shrink-0" />
            )}
            {!selectedPlaylistId && <ListMusic className="w-4 h-4 mr-2 text-slate-400 flex-shrink-0" />}
            {playlist.name}
          </Button>
        ))}
        {playlists.length === 0 && <p className="text-sm text-slate-500 p-2">Keine Playlists verfügbar.</p>}
      </div>
    </div>
  )
}
