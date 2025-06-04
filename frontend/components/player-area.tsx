import NowPlayingInfoDisplay from "@/components/now-playing-info-display"
import PlayerControls from "@/components/player-controls"
import type { Song } from "@/lib/types"

interface PlayerAreaProps {
  currentSong: Song | null
  isPlaying: boolean
  volume: number
  onPlayPause: () => void
  onNext: () => void
  onPrev: () => void
  onVolumeChange: (volume: number) => void
}

export default function PlayerArea({
  currentSong,
  isPlaying,
  volume,
  onPlayPause,
  onNext,
  onPrev,
  onVolumeChange,
}: PlayerAreaProps) {
  return (
    <div className="w-full md:w-2/3 bg-slate-800/70 p-6 flex flex-col justify-between items-center space-y-6 border-b md:border-b-0 md:border-r border-slate-700">
      <NowPlayingInfoDisplay currentSong={currentSong} />
      <PlayerControls
        isPlaying={isPlaying}
        volume={volume}
        onPlayPause={onPlayPause}
        onNext={onNext}
        onPrev={onPrev}
        onVolumeChange={onVolumeChange}
      />
    </div>
  )
}
