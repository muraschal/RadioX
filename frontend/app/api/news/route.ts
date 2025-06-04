import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const persona = searchParams.get('persona') || 'zueri_style'
    const limit = parseInt(searchParams.get('limit') || '10')
    
    // Backend-URL
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    // Backend-Request für News
    const response = await fetch(`${backendUrl}/api/news?persona=${persona}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Transform für Frontend-Format
    const transformedNews = data.news?.map((item: any, index: number) => ({
      id: `news_${Date.now()}_${index}`,
      user: `@${item.source || 'RadioX'}`,
      content: `${item.title}\n\n${item.summary?.substring(0, 200)}...`,
      timestamp: `${Math.floor(Math.random() * 60) + 1}m`,
      avatar: `/placeholder.svg?height=32&width=32&query=${item.source || 'news'} icon`,
    })) || []
    
    return NextResponse.json({
      success: true,
      news: transformedNews,
      total: data.total || transformedNews.length,
      persona: persona
    })
    
  } catch (error) {
    console.error('News API Error:', error)
    
    // Fallback Mock-News bei Fehler
    const mockNews = [
      {
        id: `mock_${Date.now()}_1`,
        user: '@RadioX',
        content: 'Willkommen bei RadioX! Live-News werden geladen...',
        timestamp: '1m',
        avatar: '/placeholder.svg?height=32&width=32&query=radio icon',
      },
      {
        id: `mock_${Date.now()}_2`,
        user: '@ZurichNews',
        content: 'Zürich aktuell: Backend-Verbindung wird hergestellt...',
        timestamp: '2m',
        avatar: '/placeholder.svg?height=32&width=32&query=zurich icon',
      }
    ]
    
    return NextResponse.json({
      success: false,
      news: mockNews,
      error: 'Backend not available - showing mock data',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 