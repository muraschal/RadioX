"use client"

import { useState, useEffect } from "react"
import type { Tweet } from "@/lib/types"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, ExternalLink, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"

interface NewsFeedProps {
  tweets?: Tweet[]  // Optional - wird von API überschrieben
  className?: string
  isArchiveView?: boolean
  persona?: string  // Neu: Persona für News-Filter
}

export default function NewsFeed({ tweets: initialTweets, className, isArchiveView = false, persona = "zueri_style" }: NewsFeedProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [tweets, setTweets] = useState<Tweet[]>(initialTweets || [])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  // Live-News laden
  const fetchNews = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/news?persona=${persona}&limit=10`)
      const data = await response.json()
      
      if (data.success && data.news) {
        setTweets(data.news)
        setLastUpdate(new Date())
      } else {
        console.warn('News API Error:', data.error)
        // Fallback zu initialTweets oder Mock-Data
        if (!tweets.length && initialTweets) {
          setTweets(initialTweets)
        }
      }
    } catch (error) {
      console.error('Failed to fetch news:', error)
      // Fallback zu initialTweets
      if (!tweets.length && initialTweets) {
        setTweets(initialTweets)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Initial load und Auto-Refresh
  useEffect(() => {
    fetchNews()
    
    // Auto-Refresh alle 5 Minuten
    const interval = setInterval(fetchNews, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [persona])

  if (!tweets || tweets.length === 0) {
    return (
      <div className="text-sm text-slate-500 p-2 text-center">
        {isLoading ? (
          <div className="flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Lade News...</span>
          </div>
        ) : (
          <div>
            <p>Keine aktuellen Nachrichten...</p>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={fetchNews}
              className="mt-2 text-purple-400 hover:text-purple-300"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Neu laden
            </Button>
          </div>
        )}
      </div>
    )
  }

  const handlePrev = () => {
    setCurrentIndex((prevIndex) => (prevIndex === 0 ? tweets.length - 1 : prevIndex - 1))
  }

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex === tweets.length - 1 ? 0 : prevIndex + 1))
  }

  const currentTweet = tweets[currentIndex]

  // Listenansicht für das Archiv-Panel
  if (isArchiveView) {
    return (
      <div
        className={cn(
          "space-y-3 overflow-y-auto max-h-[calc(100vh-150px)] scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent pr-1",
          className,
        )}
      >
        {tweets.map((tweet) => (
          <div
            key={tweet.id}
            className="bg-slate-700/40 p-3 rounded-lg shadow-md border border-slate-600/30 hover:border-purple-500/40 transition-colors"
          >
            <div className="flex items-start space-x-2 sm:space-x-3">
              <Image
                src={tweet.avatar || `/placeholder.svg?height=32&width=32&query=${tweet.user}+icon`}
                alt={`${tweet.user} Avatar`}
                width={32}
                height={32}
                className="rounded-full border border-purple-500/50 flex-shrink-0 mt-0.5"
              />
              <div>
                <div className="flex items-baseline space-x-1 sm:space-x-1.5">
                  <span className="font-semibold text-xs sm:text-sm text-purple-300">{tweet.user}</span>
                  <span className="text-[10px] sm:text-xs text-slate-500">{tweet.timestamp}</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed mt-0.5">{tweet.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Swipe-Ansicht für den Haupt-Feed
  return (
    <div className={cn("relative flex flex-col items-center", className)}>
      <div className="w-full bg-slate-700/30 p-3 sm:p-4 rounded-lg shadow-md border border-slate-600/30 min-h-[120px] flex flex-col justify-between">
        <div>
          <div className="flex items-start space-x-2 sm:space-x-3">
            <Image
              src={currentTweet.avatar || `/placeholder.svg?height=32&width=32&query=${currentTweet.user}+icon`}
              alt={`${currentTweet.user} Avatar`}
              width={32}
              height={32}
              className="rounded-full border border-purple-500/50 flex-shrink-0 mt-0.5"
            />
            <div>
              <div className="flex items-baseline space-x-1 sm:space-x-1.5">
                <span className="font-semibold text-xs sm:text-sm text-purple-300">{currentTweet.user}</span>
                <span className="text-[10px] sm:text-xs text-slate-500">{currentTweet.timestamp}</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed mt-0.5 line-clamp-3 sm:line-clamp-none">
                {currentTweet.content}
              </p>
            </div>
          </div>
        </div>
        <a
          href="#"
          onClick={(e) => e.preventDefault()} // Placeholder link
          className="text-purple-400 hover:text-purple-300 text-[10px] sm:text-xs mt-2 inline-flex items-center self-start"
        >
          Mehr lesen <ExternalLink className="w-2.5 h-2.5 sm:w-3 sm:h-3 ml-1" />
        </a>
      </div>

      <div className="flex justify-between items-center w-full mt-2 sm:mt-3 px-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={handlePrev}
          className="text-slate-400 hover:text-purple-400 hover:bg-purple-500/10 rounded-full p-1.5 sm:p-2"
          aria-label="Vorherige Nachricht"
        >
          <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
        </Button>
        
        <div className="flex flex-col items-center space-y-1">
          <span className="text-[10px] sm:text-xs text-slate-500">
            {currentIndex + 1} / {tweets.length}
          </span>
          {lastUpdate && (
            <span className="text-[8px] sm:text-[10px] text-slate-600">
              {lastUpdate.toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={fetchNews}
            disabled={isLoading}
            className="text-slate-400 hover:text-purple-400 hover:bg-purple-500/10 rounded-full p-1.5 sm:p-2"
            aria-label="News aktualisieren"
          >
            <RefreshCw className={cn("w-3 h-3 sm:w-4 sm:h-4", isLoading && "animate-spin")} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleNext}
            className="text-slate-400 hover:text-purple-400 hover:bg-purple-500/10 rounded-full p-1.5 sm:p-2"
            aria-label="Nächste Nachricht"
          >
            <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
