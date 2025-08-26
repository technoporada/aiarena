"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface AnimatedAvatarProps {
  agent: "adam" | "beata" | "wapiacy";
  size?: "sm" | "md" | "lg" | "xl";
  emotion?: "happy" | "sad" | "angry" | "surprised" | "doubtful" | "neutral" | "talking";
  isTalking?: boolean;
  className?: string;
  onClick?: () => void;
}

export function AnimatedAvatar({
  agent,
  size = "md",
  emotion = "neutral",
  isTalking = false,
  className,
  onClick,
}: AnimatedAvatarProps) {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);
  const [animationFrame, setAnimationFrame] = useState(0);

  const agentConfig = {
    adam: {
      baseColor: "bg-blue-500",
      hoverColor: "bg-blue-600",
      emoji: "🧠",
      name: "Adam",
      animations: {
        happy: "animate-bounce",
        sad: "animate-pulse",
        angry: "animate-shake",
        surprised: "animate-jump",
        doubtful: "animate-wiggle",
        talking: "animate-pulse",
        neutral: "",
      },
    },
    beata: {
      baseColor: "bg-red-500",
      hoverColor: "bg-red-600",
      emoji: "🔍",
      name: "Beata",
      animations: {
        happy: "animate-bounce",
        sad: "animate-pulse",
        angry: "animate-shake",
        surprised: "animate-jump",
        doubtful: "animate-wiggle",
        talking: "animate-pulse",
        neutral: "",
      },
    },
    wapiacy: {
      baseColor: "bg-yellow-500",
      hoverColor: "bg-yellow-600",
      emoji: "❓",
      name: "Wątpiący",
      animations: {
        happy: "animate-bounce",
        sad: "animate-pulse",
        angry: "animate-shake",
        surprised: "animate-jump",
        doubtful: "animate-wiggle",
        talking: "animate-pulse",
        neutral: "",
      },
    },
  };

  const sizeClasses = {
    sm: "w-12 h-12 text-lg",
    md: "w-16 h-16 text-2xl",
    lg: "w-24 h-24 text-4xl",
    xl: "w-32 h-32 text-6xl",
  };

  const config = agentConfig[agent];
  const animationClass = config.animations[currentEmotion];

  // Animation effects
  useEffect(() => {
    if (isTalking) {
      setCurrentEmotion("talking");
      const interval = setInterval(() => {
        setAnimationFrame((frame) => (frame + 1) % 4);
      }, 200);
      return () => clearInterval(interval);
    } else {
      setCurrentEmotion(emotion);
      setAnimationFrame(0);
    }
  }, [isTalking, emotion]);

  // Talking animation effect
  const talkingEffect = isTalking ? {
    transform: `scale(${1 + Math.sin(animationFrame * 0.5) * 0.1})`,
  } : {};

  return (
    <div
      className={cn(
        "relative cursor-pointer transition-all duration-300 hover:scale-105",
        className
      )}
      onClick={onClick}
    >
      {/* Avatar Container */}
      <div
        className={cn(
          "rounded-full flex items-center justify-center font-bold text-white shadow-lg transition-all duration-300",
          config.baseColor,
          "hover:" + config.hoverColor,
          sizeClasses[size],
          animationClass
        )}
        style={talkingEffect}
      >
        {/* Base Emoji */}
        <span className="select-none">{config.emoji}</span>
        
        {/* Talking Effect */}
        {isTalking && (
          <div className="absolute -top-1 -right-1 flex space-x-0.5">
            <div className="w-1 h-1 bg-white rounded-full animate-ping"></div>
            <div className="w-1 h-1 bg-white rounded-full animate-ping" style={{ animationDelay: "0.2s" }}></div>
          </div>
        )}
      </div>

      {/* Emotion Indicator */}
      {currentEmotion !== "neutral" && (
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
          <div className="bg-white dark:bg-gray-800 rounded-full px-2 py-1 shadow-md">
            <span className="text-xs">
              {currentEmotion === "happy" && "😊"}
              {currentEmotion === "sad" && "😢"}
              {currentEmotion === "angry" && "😠"}
              {currentEmotion === "surprised" && "😲"}
              {currentEmotion === "doubtful" && "🤔"}
              {currentEmotion === "talking" && "💬"}
            </span>
          </div>
        </div>
      )}

      {/* Name Badge */}
      <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          {config.name}
        </span>
      </div>

      {/* Status Ring */}
      {isTalking && (
        <div className="absolute inset-0 rounded-full border-2 border-green-400 animate-ping"></div>
      )}
    </div>
  );
}

// Special animated components for different contexts
export function TalkingAvatar({ agent, ...props }: Omit<AnimatedAvatarProps, "emotion">) {
  return (
    <AnimatedAvatar
      agent={agent}
      emotion="talking"
      isTalking={true}
      {...props}
    />
  );
}

export function EmotionalAvatar({ 
  agent, 
  emotion, 
  ...props 
}: Omit<AnimatedAvatarProps, "isTalking">) {
  return (
    <AnimatedAvatar
      agent={agent}
      emotion={emotion}
      isTalking={false}
      {...props}
    />
  );
}

// Avatar group for multiple agents
interface AvatarGroupProps {
  agents: Array<{
    id: string;
    type: "adam" | "beata" | "wapiacy";
    emotion?: string;
    isTalking?: boolean;
  }>;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function AvatarGroup({ agents, size = "md", className }: AvatarGroupProps) {
  return (
    <div className={cn("flex items-center space-x-2", className)}>
      {agents.map((agent, index) => (
        <div key={agent.id} className={index > 0 ? "-ml-2" : ""}>
          <AnimatedAvatar
            agent={agent.type}
            size={size}
            emotion={agent.emotion}
            isTalking={agent.isTalking}
          />
        </div>
      ))}
    </div>
  );
}

// Dancing avatar for entertainment
export function DancingAvatar({ agent, ...props }: Omit<AnimatedAvatarProps, "emotion">) {
  return (
    <div className="animate-spin-slow">
      <AnimatedAvatar
        agent={agent}
        emotion="happy"
        isTalking={false}
        {...props}
      />
    </div>
  );
}