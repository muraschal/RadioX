import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { persona } = await request.json()
    
    // Backend-URL (anpassbar je nach Environment)
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    // Backend-Request für Live-Broadcast
    const response = await fetch(`${backendUrl}/api/generate-broadcast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        persona: persona || 'zueri_style',
        format: 'mp3',
        include_cover: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    
    return NextResponse.json({
      success: true,
      broadcast: {
        url: data.mp3_url,
        cover: data.cover_url,
        duration: data.duration,
        segments: data.segments,
        timestamp: data.timestamp
      }
    })
    
  } catch (error) {
    console.error('Broadcast API Error:', error)
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to generate broadcast',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Status-Endpoint für Frontend
  return NextResponse.json({
    status: 'ready',
    available_personas: [
      'zueri_style',
      'breaking_news', 
      'bitcoin_og',
      'tradfi_news',
      'tech_insider',
      'swiss_local'
    ],
    backend_url: process.env.BACKEND_URL || 'http://localhost:8000'
  })
} 