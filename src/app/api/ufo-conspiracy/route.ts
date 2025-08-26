import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, session_id, winner } = body;

    let url;
    let options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    };

    switch (action) {
      case 'start':
        url = `${BACKEND_URL}/api/ufo-conspiracy/start-ufo-conspiracy`;
        break;
      
      case 'next_round':
        if (!session_id) {
          return NextResponse.json({ error: 'Session ID required' }, { status: 400 });
        }
        url = `${BACKEND_URL}/api/ufo-conspiracy/next-ufo-round`;
        options.body = JSON.stringify({ session_id });
        break;
      
      case 'vote':
        if (!session_id || !winner) {
          return NextResponse.json({ error: 'Session ID and winner required' }, { status: 400 });
        }
        url = `${BACKEND_URL}/api/ufo-conspiracy/vote-conspiracy-master`;
        options.body = JSON.stringify({ session_id, winner });
        break;
      
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('UFO Conspiracy API error:', error);
    return NextResponse.json(
      { error: 'Failed to process UFO conspiracy request' },
      { status: 500 }
    );
  }
}