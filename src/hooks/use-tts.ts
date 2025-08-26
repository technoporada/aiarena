"use client";

import { useState, useRef, useEffect } from "react";

interface TTSOptions {
  voiceId?: string;
  speed?: number;
  pitch?: number;
  emotion?: string;
  volume?: number;
}

interface VoiceConfig {
  voice_id: string;
  name: string;
  language: string;
  gender: string;
  description: string;
  preview_text: string;
}

export function useTTS() {
  const [isLoading, setIsLoading] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<VoiceConfig[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Initialize available voices
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const response = await fetch("/api/tts/voices");
        if (response.ok) {
          const data = await response.json();
          setAvailableVoices(data.voices || []);
        }
      } catch (error) {
        console.error("Failed to fetch TTS voices:", error);
      }
    };

    fetchVoices();
  }, []);

  const speak = async (
    text: string,
    options: TTSOptions = {}
  ): Promise<boolean> => {
    if (!text.trim()) return false;

    setIsLoading(true);
    try {
      const response = await fetch("/api/tts/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          voice_id: options.voiceId || "adam",
          speed: options.speed || 1.0,
          pitch: options.pitch || 1.0,
          emotion: options.emotion || "neutral",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate speech");
      }

      const data = await response.json();
      
      // Create audio element and play
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(`data:audio/mp3;base64,${data.audio_data}`);
      audioRef.current = audio;
      
      // Set volume if specified
      if (options.volume) {
        audio.volume = options.volume;
      }

      setIsPlaying(true);
      
      return new Promise((resolve) => {
        audio.onended = () => {
          setIsPlaying(false);
          resolve(true);
        };
        
        audio.onerror = () => {
          setIsPlaying(false);
          resolve(false);
        };
        
        audio.play().catch((error) => {
          console.error("Audio playback failed:", error);
          setIsPlaying(false);
          resolve(false);
        });
      });

    } catch (error) {
      console.error("TTS error:", error);
      setIsLoading(false);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const previewVoice = async (voiceId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/tts/preview/${voiceId}`);
      if (!response.ok) {
        throw new Error("Failed to preview voice");
      }

      const data = await response.json();
      
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(`data:audio/mp3;base64,${data.audio_data}`);
      audioRef.current = audio;

      setIsPlaying(true);
      
      return new Promise((resolve) => {
        audio.onended = () => {
          setIsPlaying(false);
          resolve(true);
        };
        
        audio.onerror = () => {
          setIsPlaying(false);
          resolve(false);
        };
        
        audio.play().catch((error) => {
          console.error("Audio playback failed:", error);
          setIsPlaying(false);
          resolve(false);
        });
      });

    } catch (error) {
      console.error("Voice preview error:", error);
      return false;
    }
  };

  const getVoiceForAgent = (agent: string): string => {
    const agentVoiceMap: Record<string, string> = {
      adam: "adam",
      beata: "beata",
      wapiacy: "wapiacy",
      normal: "adam",
    };
    return agentVoiceMap[agent] || "adam";
  };

  const getEmotionForText = (text: string): string => {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes("!") || lowerText.includes("great") || lowerText.includes("awesome")) {
      return "happy";
    } else if (lowerText.includes("?") || lowerText.includes("maybe") || lowerText.includes("perhaps")) {
      return "doubtful";
    } else if (lowerText.includes("angry") || lowerText.includes("mad") || lowerText.includes("upset")) {
      return "angry";
    } else if (lowerText.includes("wow") || lowerText.includes("amazing") || lowerText.includes("surprised")) {
      return "surprised";
    } else if (lowerText.includes("sad") || lowerText.includes("unhappy") || lowerText.includes("sorry")) {
      return "sad";
    }
    
    return "neutral";
  };

  return {
    speak,
    stop,
    previewVoice,
    availableVoices,
    isLoading,
    isPlaying,
    getVoiceForAgent,
    getEmotionForText,
  };
}