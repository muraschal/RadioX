"use client"

import type { Persona } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { UserCircle, CheckCircle } from "lucide-react" // UserCircle already imported in RadioInterface, ensure consistency or remove if not used here directly

interface PersonaSelectorProps {
  personas: Persona[]
  selectedPersonaId: string
  onSelect: (personaId: string) => void
}

export default function PersonaSelector({ personas, selectedPersonaId, onSelect }: PersonaSelectorProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-pink-400 flex items-center">
        <UserCircle className="w-5 h-5 mr-2" /> {/* Using generic UserCircle here */}
        Radio Persona
      </h3>
      <div className="space-y-1 max-h-48 overflow-y-auto pr-2">
        {personas.map((persona) => (
          <Button
            key={persona.id}
            variant={selectedPersonaId === persona.id ? "secondary" : "ghost"}
            onClick={() => onSelect(persona.id)}
            className={`w-full justify-start text-left h-auto py-2 px-3 rounded-md transition-all duration-150 ease-in-out
                        ${
                          selectedPersonaId === persona.id
                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50"
                            : "text-slate-300 hover:bg-slate-700/50 hover:text-cyan-400"
                        }`}
          >
            <div className="flex items-center">
              {selectedPersonaId === persona.id && <CheckCircle className="w-4 h-4 mr-2 text-cyan-400 flex-shrink-0" />}
              {persona.icon} {/* Render the icon passed with the persona data */}
              <div className="flex flex-col">
                <span className="font-medium">{persona.name}</span>
                <span className="text-xs text-slate-400">{persona.description}</span>
              </div>
            </div>
          </Button>
        ))}
      </div>
    </div>
  )
}
