import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { voiceId: string } }
) {
  try {
    const { voiceId } = params;

    if (!voiceId) {
      return NextResponse.json(
        { error: "Voice ID is required" },
        { status: 400 }
      );
    }

    // Forward the request to the Python backend
    const backendResponse = await fetch(`http://localhost:8000/api/tts/preview/${voiceId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
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
    console.error("TTS Preview API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}