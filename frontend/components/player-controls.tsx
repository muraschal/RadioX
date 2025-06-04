"use client"

import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Play, Pause, SkipForward, SkipBack, Volume1, Volume2, VolumeX } from "lucide-react"

interface PlayerControlsProps {
  isPlaying: boolean
  volume: number
  onPlayPause: () => void
  onNext: () => void
  onPrev: () => void
  onVolumeChange: (volume: number) => void
}

export default function PlayerControls({
  isPlaying,
  volume,
  onPlayPause,
  onNext,
  onPrev,
  onVolumeChange,
}: PlayerControlsProps) {
  const VolumeIcon = volume === 0 ? VolumeX : volume < 0.5 ? Volume1 : Volume2

  return (
    <div className="w-full max-w-md space-y-4">
      <div className="flex justify-center items-center space-x-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onPrev}
          className="text-slate-300 hover:text-cyan-400 hover:bg-slate-700/50 rounded-full"
        >
          <SkipBack className="w-7 h-7" />
          <span className="sr-only">Vorheriger Song</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onPlayPause}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 rounded-full w-16 h-16"
        >
          {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" />}
          <span className="sr-only">{isPlaying ? "Pause" : "Play"}</span>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onNext}
          className="text-slate-300 hover:text-cyan-400 hover:bg-slate-700/50 rounded-full"
        >
          <SkipForward className="w-7 h-7" />
          <span className="sr-only">Nächster Song</span>
        </Button>
      </div>
      <div className="flex items-center space-x-2">
        <VolumeIcon className="w-5 h-5 text-slate-400" />
        <Slider
          defaultValue={[volume * 100]}
          max={100}
          step={1}
          onValueChange={(value) => onVolumeChange(value[0] / 100)}
          className="[&>span:first-child]:h-full [&>span:first-child]:bg-cyan-500"
          aria-label="Lautstärkeregler"
        />
      </div>
    </div>
  )
}
