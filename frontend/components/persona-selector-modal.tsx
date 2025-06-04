"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import type { Persona } from "@/lib/types"
import { cn } from "@/lib/utils"

interface PersonaSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  personas: Persona[]
  currentPersonaId: string
  onPersonaSelect: (persona: Persona) => void
}

export default function PersonaSelectorModal({
  isOpen,
  onClose,
  personas,
  currentPersonaId,
  onPersonaSelect,
}: PersonaSelectorModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800/90 backdrop-blur-md border-slate-700 text-slate-100 shadow-2xl sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="text-2xl text-purple-400">Wähle deinen Sender</DialogTitle>
          <DialogDescription className="text-slate-400">
            Passe deinen RadioX AI Stream an deine aktuellen Interessen an.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 max-h-[60vh] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent">
          {personas.map((persona) => (
            <Button
              key={persona.id}
              variant="outline"
              onClick={() => onPersonaSelect(persona)}
              className={cn(
                "flex flex-col items-center justify-center p-4 rounded-lg h-auto text-center transition-all duration-300 ease-in-out transform hover:scale-[1.03] min-h-[120px]", // Reduced scale effect
                "border-2 bg-slate-700/50 backdrop-blur-sm",
                currentPersonaId === persona.id
                  ? `${persona.borderColor} ${persona.bgColor} shadow-lg scale-[1.03] ring-2 ${persona.borderColor?.replace("border-", "ring-")}` // Apply consistent scale on active
                  : "border-slate-600/50 hover:border-slate-500",
                currentPersonaId === persona.id ? persona.accentColor : "text-slate-300",
                persona.hoverBgColor,
              )}
            >
              <div className={cn("mb-1.5", currentPersonaId === persona.id && persona.accentColor)}>{persona.icon}</div>
              <span className="font-semibold text-sm md:text-base whitespace-nowrap">{persona.name}</span>
              <span className="text-xs text-slate-400 mt-0.5 leading-tight">{persona.description}</span>
            </Button>
          ))}
        </div>
        {/* Optional: Footer im Modal, z.B. für einen Schließen-Button, falls kein onOpenChange genutzt wird */}
        {/* <DialogFooter>
        <Button onClick={onClose} variant="ghost">Schließen</Button>
      </DialogFooter> */}
      </DialogContent>
    </Dialog>
  )
}
