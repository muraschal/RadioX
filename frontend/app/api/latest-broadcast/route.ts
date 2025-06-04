import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Backend-URL
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    // Backend-Request für neueste Broadcast-Datei
    const response = await fetch(`${backendUrl}/api/latest-broadcast`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Vollständige URLs für Frontend erstellen
    const result = {
      success: true,
      broadcast: {
        filename: data.mp3_file,
        audioUrl: `${backendUrl}${data.mp3_path}`,
        coverUrl: data.cover_path ? `${backendUrl}${data.cover_path}` : null,
        fileSize: data.file_size,
        timestamp: data.timestamp,
        metadata: data.metadata || {}
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