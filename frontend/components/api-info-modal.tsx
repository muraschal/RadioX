"use client"

import type React from "react"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import type { ApiStatus } from "@/lib/types"
import { CheckCircle, XCircle, AlertTriangle } from "lucide-react"

interface ApiInfoModalProps {
  isOpen: boolean
  onClose: () => void
  apiStatus: ApiStatus
}

const StatusIndicator: React.FC<{ connected: boolean; message?: string; error?: string }> = ({
  connected,
  message,
  error,
}) => {
  if (connected) {
    return (
      <span className="flex items-center text-green-400">
        <CheckCircle className="w-4 h-4 mr-2" />
        Connected {message && `(${message})`}
      </span>
    )
  }
  if (error) {
    return (
      <span className="flex items-center text-red-400">
        <XCircle className="w-4 h-4 mr-2" />
        Error: {error}
      </span>
    )
  }
  return (
    <span className="flex items-center text-yellow-400">
      <AlertTriangle className="w-4 h-4 mr-2" />
      Status Unknown
    </span>
  )
}

export default function ApiInfoModal({ isOpen, onClose, apiStatus }: ApiInfoModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-slate-100 shadow-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl text-purple-400">API Connection Status</DialogTitle>
          <DialogDescription className="text-slate-400">
            Current status of integrated services. Last checked: {new Date().toLocaleTimeString()}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <h4 className="font-semibold text-slate-300 mb-1">Spotify API</h4>
            <StatusIndicator
              connected={apiStatus.spotify.connected}
              message={`Last checked: ${apiStatus.spotify.lastChecked}`}
            />
          </div>
          <div>
            <h4 className="font-semibold text-slate-300 mb-1">News Feed API (e.g. X/Twitter)</h4>
            <StatusIndicator
              connected={apiStatus.twitter.connected} // 'twitter' key used for general news API status
              message={apiStatus.twitter.message}
              error={apiStatus.twitter.error}
            />
          </div>
          <div>
            <h4 className="font-semibold text-slate-300 mb-1">ElevenLabs TTS API</h4>
            <StatusIndicator
              connected={apiStatus.elevenLabs.connected}
              message={apiStatus.elevenLabs.message}
              error={apiStatus.elevenLabs.error}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            onClick={onClose}
            variant="outline"
            className="text-purple-400 border-purple-400 hover:bg-purple-500/10 hover:text-purple-300"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
