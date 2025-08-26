import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { theme, participants, max_songs } = body;

    if (!theme) {
      return NextResponse.json(
        { error: "Theme is required" },
        { status: 400 }
      );
    }

    // Forward the request to the Python backend
    const backendResponse = await fetch("http://localhost:8000/api/karaoke/start-night", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        theme,
        participants: participants || ["Adam", "Beata", "Wątpiący"],
        max_songs: max_songs || 3,
      }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { error: errorData.error || "Backend request failed" },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Karaoke night API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}