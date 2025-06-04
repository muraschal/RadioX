import type { Tweet } from "@/lib/types"
import Image from "next/image"
import { MessageSquare } from "lucide-react"

interface TwitterFeedProps {
  tweets: Tweet[]
}

export default function TwitterFeed({ tweets }: TwitterFeedProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-pink-400 flex items-center">
        <MessageSquare className="w-5 h-5 mr-2" />
        Nachrichten-Ticker
      </h3>
      <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
        {tweets.length === 0 && <p className="text-sm text-slate-400">Keine aktuellen Tweets...</p>}
        {tweets.map((tweet) => (
          <div
            key={tweet.id}
            className="bg-slate-700/50 p-3 rounded-lg shadow-md border border-slate-600/50 hover:border-pink-500/50 transition-colors"
          >
            <div className="flex items-start space-x-3">
              <Image
                src={tweet.avatar || "/placeholder.svg"}
                alt={`${tweet.user} Avatar`}
                width={32}
                height={32}
                className="rounded-full border-2 border-pink-500/70"
              />
              <div>
                <div className="flex items-baseline space-x-1">
                  <span className="font-semibold text-sm text-cyan-300">{tweet.user}</span>
                  <span className="text-xs text-slate-500">{tweet.timestamp}</span>
                </div>
                <p className="text-sm text-slate-200 leading-relaxed">{tweet.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
