"use client"

import PlaylistSelector from "@/components/playlist-selector"
import TwitterFeed from "@/components/twitter-feed"
import PersonaSelector from "@/components/persona-selector"
import type { Playlist, Tweet, Persona } from "@/lib/types"

interface SidebarAreaProps {
  playlists: Playlist[]
  selectedPlaylistId: string
  onPlaylistSelect: (playlistId: string) => void
  tweets: Tweet[]
  personas: Persona[]
  selectedPersonaId: string
  onPersonaSelect: (personaId: string) => void
}

export default function SidebarArea({
  playlists,
  selectedPlaylistId,
  onPlaylistSelect,
  tweets,
  personas,
  selectedPersonaId,
  onPersonaSelect,
}: SidebarAreaProps) {
  return (
    <div className="w-full md:w-1/3 bg-slate-800/40 p-4 space-y-6 overflow-y-auto max-h-[calc(100vh-100px)] md:max-h-none md:h-auto">
      <PlaylistSelector playlists={playlists} selectedPlaylistId={selectedPlaylistId} onSelect={onPlaylistSelect} />
      <PersonaSelector personas={personas} selectedPersonaId={selectedPersonaId} onSelect={onPersonaSelect} />
      <TwitterFeed tweets={tweets} />
    </div>
  )
}
