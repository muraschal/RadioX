"use client"
import type React from "react"
import { useEffect, useRef } from "react"
import { cn } from "@/lib/utils"

interface AudioVisualizerLineProps {
  isPlaying: boolean
  className?: string
}

const AudioVisualizerLine: React.FC<AudioVisualizerLineProps> = ({ isPlaying, className }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationFrameId: number
    const numBars = 64 // Number of bars in the visualizer
    const barWidth = canvas.width / numBars

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Get stroke color from parent SVG or default
      const strokeColor = canvas.parentElement?.classList.contains("stroke-orange-500")
        ? "#F97316"
        : canvas.parentElement?.classList.contains("stroke-purple-500")
          ? "#A855F7"
          : canvas.parentElement?.classList.contains("stroke-pink-500")
            ? "#EC4899"
            : "#60A5FA" // Default blue
      ctx.strokeStyle = strokeColor
      ctx.lineWidth = 2

      ctx.beginPath()
      ctx.moveTo(0, canvas.height / 2)

      for (let i = 0; i < numBars; i++) {
        const barHeight = isPlaying ? Math.random() * (canvas.height * 0.8) + canvas.height * 0.1 : canvas.height * 0.1
        const x = i * barWidth + barWidth / 2
        const y = (canvas.height - barHeight) / 2

        // Simple wave form
        const waveY =
          canvas.height / 2 +
          (isPlaying ? Math.sin(i * 0.2 + Date.now() * 0.005) * (canvas.height * 0.3) * Math.random() : 0)
        ctx.lineTo(x, waveY)
      }
      ctx.lineTo(canvas.width, canvas.height / 2)
      ctx.stroke()

      animationFrameId = requestAnimationFrame(draw)
    }

    // Set canvas dimensions based on its container
    const resizeCanvas = () => {
      if (canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth
        canvas.height = canvas.parentElement.clientHeight
      }
      draw() // Redraw on resize
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    draw()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener("resize", resizeCanvas)
    }
  }, [isPlaying]) // Redraw when isPlaying changes or persona color changes

  return <canvas ref={canvasRef} className={cn("w-full h-full", className)} />
}

export default AudioVisualizerLine
