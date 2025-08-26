"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useTTS } from "@/hooks/use-tts";
import { AnimatedAvatar } from "@/components/ui/avatars/AnimatedAvatar";

interface TTSPlayerProps {
  text: string;
  agent?: "adam" | "beata" | "wapiacy" | "normal";
  autoPlay?: boolean;
  className?: string;
}

export function TTSPlayer({
  text,
  agent = "normal",
  autoPlay = false,
  className,
}: TTSPlayerProps) {
  const {
    speak,
    stop,
    previewVoice,
    availableVoices,
    isLoading,
    isPlaying,
    getVoiceForAgent,
    getEmotionForText,
  } = useTTS();

  const [selectedVoice, setSelectedVoice] = useState(getVoiceForAgent(agent));
  const [speed, setSpeed] = useState([1.0]);
  const [pitch, setPitch] = useState([1.0]);
  const [emotion, setEmotion] = useState(getEmotionForText(text));
  const [volume, setVolume] = useState([1.0]);

  const emotions = [
    { value: "neutral", label: "Neutral 😐", color: "bg-gray-500" },
    { value: "happy", label: "Happy 😊", color: "bg-green-500" },
    { value: "sad", label: "Sad 😢", color: "bg-blue-500" },
    { value: "angry", label: "Angry 😠", color: "bg-red-500" },
    { value: "surprised", label: "Surprised 😲", color: "bg-yellow-500" },
    { value: "doubtful", label: "Doubtful 🤔", color: "bg-purple-500" },
  ];

  const handlePlay = async () => {
    const success = await speak(text, {
      voiceId: selectedVoice,
      speed: speed[0],
      pitch: pitch[0],
      emotion,
      volume: volume[0],
    });
    
    if (!success) {
      console.error("Failed to play text-to-speech");
    }
  };

  const handlePreviewVoice = async (voiceId: string) => {
    await previewVoice(voiceId);
  };

  const selectedVoiceConfig = availableVoices.find((v) => v.voice_id === selectedVoice);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AnimatedAvatar
            agent={agent as any}
            size="sm"
            emotion={emotion as any}
            isTalking={isPlaying}
          />
          Text-to-Speech Player
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Text Preview */}
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            "{text.length > 100 ? text.substring(0, 100) + "..." : text}"
          </p>
        </div>

        {/* Voice Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Voice</label>
          <Select value={selectedVoice} onValueChange={setSelectedVoice}>
            <SelectTrigger>
              <SelectValue placeholder="Select a voice" />
            </SelectTrigger>
            <SelectContent>
              {availableVoices.map((voice) => (
                <SelectItem key={voice.voice_id} value={voice.voice_id}>
                  <div className="flex items-center gap-2">
                    <span>{voice.name}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreviewVoice(voice.voice_id);
                      }}
                    >
                      ▶️
                    </Button>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Emotion Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Emotion</label>
          <Select value={emotion} onValueChange={(value) => setEmotion(value as any)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {emotions.map((emo) => (
                <SelectItem key={emo.value} value={emo.value}>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={emo.color}>
                      {emo.label}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-2 gap-4">
          {/* Speed Control */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Speed: {speed[0]}x</label>
            <Slider
              value={speed}
              onValueChange={setSpeed}
              min={0.5}
              max={2.0}
              step={0.1}
              className="w-full"
            />
          </div>

          {/* Pitch Control */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Pitch: {pitch[0]}</label>
            <Slider
              value={pitch}
              onValueChange={setPitch}
              min={0.5}
              max={2.0}
              step={0.1}
              className="w-full"
            />
          </div>
        </div>

        {/* Volume Control */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Volume: {Math.round(volume[0] * 100)}%</label>
          <Slider
            value={volume}
            onValueChange={setVolume}
            min={0}
            max={1}
            step={0.1}
            className="w-full"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handlePlay}
            disabled={isLoading || isPlaying || !text.trim()}
            className="flex-1"
          >
            {isLoading ? "Generating..." : isPlaying ? "Playing..." : "▶️ Play"}
          </Button>
          {isPlaying && (
            <Button onClick={stop} variant="outline">
              ⏹️ Stop
            </Button>
          )}
        </div>

        {/* Voice Info */}
        {selectedVoiceConfig && (
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-sm space-y-1">
              <p><strong>Voice:</strong> {selectedVoiceConfig.name}</p>
              <p><strong>Language:</strong> {selectedVoiceConfig.language}</p>
              <p><strong>Gender:</strong> {selectedVoiceConfig.gender}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Simple TTS button for quick access
interface TTSButtonProps {
  text: string;
  agent?: "adam" | "beata" | "wapiacy" | "normal";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function TTSButton({ text, agent = "normal", size = "sm", className }: TTSButtonProps) {
  const { speak, isLoading, isPlaying, getVoiceForAgent, getEmotionForText } = useTTS();

  const handlePlay = async () => {
    await speak(text, {
      voiceId: getVoiceForAgent(agent),
      emotion: getEmotionForText(text),
    });
  };

  const sizeClasses = {
    sm: "w-6 h-6 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-10 h-10 text-base",
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handlePlay}
      disabled={isLoading || isPlaying || !text.trim()}
      className={className}
    >
      {isLoading ? "⏳" : isPlaying ? "🔊" : "🔈"}
    </Button>
  );
}

// TTS-enabled message component
interface TTSMessageProps {
  text: string;
  agent: "adam" | "beata" | "wapiacy" | "normal";
  timestamp?: Date;
  className?: string;
}

export function TTSMessage({ text, agent, timestamp, className }: TTSMessageProps) {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <AnimatedAvatar
            agent={agent}
            size="sm"
            emotion="neutral"
          />
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {agent === "adam" && "Adam"}
            {agent === "beata" && "Beata"}
            {agent === "wapiacy" && "Wątpiący"}
            {agent === "normal" && "AI"}
          </span>
          {timestamp && (
            <span className="text-xs text-gray-500">
              {timestamp.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
          <p className="text-sm">{text}</p>
        </div>
      </div>
      <TTSButton text={text} agent={agent} />
    </div>
  );
}