import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Quick and dirty: Direkte Referenz auf statische Datei
    const result = {
      success: true,
      broadcast: {
        filename: "latest-show.mp3",
        audioUrl: "/latest-show.mp3", // Statische Datei im public Ordner
        coverUrl: null, // Erstmal ohne Cover
        fileSize: 439000, // Ungefähre Größe in Bytes
        timestamp: new Date().toISOString(),
        metadata: {
          title: "RadioX 8:00 Enhanced Show",
          duration: "00:03:30", // Ungefähre Dauer
          timestamp: new Date().toISOString()
        }
      }
    }
    
    return NextResponse.json(result)
    
  } catch (error) {
    console.error('Latest Broadcast API Error:', error)
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to load latest broadcast',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 