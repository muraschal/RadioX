"use client"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type React from "react"

interface SidePanelProps {
  title: string
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  position?: "left" | "right"
}

export default function SidePanel({ title, isOpen, onClose, children, position = "right" }: SidePanelProps) {
  return (
    <>
      {/* Overlay */}
      <div
        className={cn(
          "fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300 ease-in-out",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
        )}
        onClick={onClose}
      />
      {/* Panel */}
      <div
        className={cn(
          "fixed top-0 h-full w-full max-w-md bg-slate-800/80 backdrop-blur-xl shadow-2xl z-50 transition-transform duration-300 ease-in-out flex flex-col border-slate-700",
          position === "left" ? "left-0 border-r" : "right-0 border-l",
          isOpen ? "translate-x-0" : position === "left" ? "-translate-x-full" : "translate-x-full",
        )}
      >
        <header className="flex items-center justify-between p-4 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-purple-400">{title}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
            <span className="sr-only">Panel schließen</span>
          </Button>
        </header>
        <div className="p-4 overflow-y-auto flex-grow">{children}</div>
        <footer className="p-3 border-t border-slate-700 text-center">
          <p className="text-xs text-slate-500">&copy; RadioX AI - {new Date().getFullYear()}</p>
        </footer>
      </div>
    </>
  )
}
