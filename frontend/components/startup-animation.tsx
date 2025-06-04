"use client"
import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

export default function StartupAnimation() {
  const [rings, setRings] = useState<number[]>([])

  useEffect(() => {
    const timers: NodeJS.Timeout[] = []
    for (let i = 0; i < 5; i++) {
      timers.push(
        setTimeout(() => {
          setRings((prev) => [...prev, i])
        }, i * 200),
      )
    }
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-slate-950 overflow-hidden">
      <div className="relative flex items-center justify-center w-64 h-64">
        {rings.map((ringIndex) => (
          <div
            key={ringIndex}
            className={cn(
              "absolute border-2 border-purple-500 rounded-full animate-ping-slow opacity-0",
              `animation-delay-${ringIndex * 200}`, // Custom animation delay utility needed
            )}
            style={{
              width: `${(ringIndex + 1) * 20}%`,
              height: `${(ringIndex + 1) * 20}%`,
              animationName: "pingCustom",
              animationDuration: "2s",
              animationIterationCount: "1", // Only ping once effectively
              animationTimingFunction: "ease-out",
              opacity: 1 - (ringIndex / 5) * 0.8, // Fade out outer rings
            }}
          />
        ))}
        <h1 className="text-6xl font-bold tracking-tighter text-slate-100 z-10 relative">
          RADIO<span className="text-purple-400">X</span>
          <span className="absolute -top-2 -right-5 text-lg font-mono text-purple-400">AI</span>
        </h1>
      </div>
      <style jsx global>{`
        @keyframes pingCustom {
          0% {
            transform: scale(0.5);
            opacity: 0.8;
          }
          80% {
            transform: scale(1.5); // Expand more
            opacity: 0;
          }
          100% {
            transform: scale(1.5);
            opacity: 0;
          }
        }
        .animation-delay-0 { animation-delay: 0ms !important; }
        .animation-delay-200 { animation-delay: 200ms !important; }
        .animation-delay-400 { animation-delay: 400ms !important; }
        .animation-delay-600 { animation-delay: 600ms !important; }
        .animation-delay-800 { animation-delay: 800ms !important; }
      `}</style>
    </div>
  )
}
