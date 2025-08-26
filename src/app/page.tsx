"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import "./tsunami.css";

interface Message {
  id: string;
  text: string;
  sender: "user" | "adam" | "beata" | "wapiacy";
  timestamp: Date;
  emotion?: string;
  emoji?: string;
}

interface DialogMessage {
  agent: string;
  text: string;
  timestamp: Date;
  turn: number;
  drama_score?: number;
  emotion?: string;
  emoji?: string;
}

interface GladiatorRound {
  round_number: number;
  agent1_attack: string;
  agent2_attack: string;
  absurdity_level: number;
  round_topic: string;
  winner?: string;
  votes: { agent1: number; agent2: number };
}

interface GladiatorBattle {
  battle_id: string;
  topic: string;
  agent1: string;
  agent2: string;
  rounds: GladiatorRound[];
  current_round: number;
  absurdity_level: number;
  final_winner?: string;
}

interface KaraokePerformance {
  song_title: string;
  original_artist: string;
  performer: string;
  performance_style: string;
  lyrics: string;
  performance_score: number;
  audience_reaction: string;
  special_effects: string[];
  emoji_reactions: string[];
}

interface KaraokeNight {
  night_id: string;
  theme: string;
  performances: KaraokePerformance[];
  current_performance: number;
  participants: string[];
}

interface TsunamiMessage {
  agent: string;
  message: string;
  emotion: string;
}

interface TsunamiState {
  phase: string;
  confused_agent: string;
  round_number: number;
  chaos_level: number;
  messages: TsunamiMessage[];
  current_topic: string;
  agent_beliefs: Record<string, string>;
  special_effects: string[];
}

interface UFOConspiracyMessage {
  agent: string;
  message: string;
  emotion: string;
}

interface UFOConspiracyState {
  phase: string;
  primary_agent: string;
  round_number: number;
  chaos_level: number;
  messages: UFOConspiracyMessage[];
  current_conspiracy: string;
  agent_beliefs: Record<string, string>;
  special_effects: string[];
  conspiracy_level: number;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<"normal" | "adam" | "beata" | "wapiacy">("normal");
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("chat");
  const [dialogMessages, setDialogMessages] = useState<DialogMessage[]>([]);
  const [dramaLevel, setDramaLevel] = useState(0);
  const [gladiatorBattle, setGladiatorBattle] = useState<GladiatorBattle | null>(null);
  const [karaokeNight, setKaraokeNight] = useState<KaraokeNight | null>(null);
  const [tsunamiState, setTsunamiState] = useState<TsunamiState | null>(null);
  const [tsunamiSessionId, setTsunamiSessionId] = useState<string | null>(null);
  const [ufoConspiracyState, setUfoConspiracyState] = useState<UFOConspiracyState | null>(null);
  const [ufoConspiracySessionId, setUfoConspiracySessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const agents = {
    normal: { name: "Normal AI", color: "bg-gray-500", emoji: "🤖" },
    adam: { name: "Adam", color: "bg-blue-500", emoji: "🧠" },
    beata: { name: "Beata", color: "bg-red-500", emoji: "🔍" },
    wapiacy: { name: "Wątpiący", color: "bg-yellow-500", emoji: "❓" },
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, dialogMessages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat/normal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: input,
          agent_type: selectedAgent,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: selectedAgent,
        timestamp: new Date(),
        emotion: "happy",
        emoji: agents[selectedAgent].emoji,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get response from AI",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSplitDialog = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/chat/split-dialog", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: input,
          max_turns: 6,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate dialog");
      }

      const data = await response.json();
      setDialogMessages(data.dialog);
      
      // Calculate average drama level
      const avgDrama = data.dialog.reduce((sum: number, msg: DialogMessage) => 
        sum + (msg.drama_score || 0), 0) / data.dialog.length;
      setDramaLevel(avgDrama);

      toast({
        title: "Dialog Generated!",
        description: `Generated ${data.dialog.length} messages between Adam and Beata`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate dialog",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartGladiatorBattle = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/gladiator/start-battle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: input,
          agent1: "Adam",
          agent2: "Beata",
          max_rounds: 5,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start battle");
      }

      const data = await response.json();
      setGladiatorBattle({
        battle_id: data.battle_id,
        topic: data.topic,
        agent1: data.agent1,
        agent2: data.agent2,
        rounds: [],
        current_round: 0,
        absurdity_level: 0.1,
      });

      toast({
        title: "⚔️ Battle Started!",
        description: `Gladiator battle: ${data.agent1} vs ${data.agent2}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start gladiator battle",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextGladiatorRound = async () => {
    if (!gladiatorBattle) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/gladiator/next-round", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          battle_id: gladiatorBattle.battle_id,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get next round");
      }

      const data = await response.json();
      
      if (data.battle_finished) {
        setGladiatorBattle(prev => prev ? { ...prev, final_winner: data.final_winner } : null);
        toast({
          title: "⚔️ Battle Finished!",
          description: data.victory_message,
        });
      } else {
        const newRound: GladiatorRound = {
          round_number: data.round_number,
          agent1_attack: data.agent1_attack,
          agent2_attack: data.agent2_attack,
          absurdity_level: data.absurdity_level,
          round_topic: data.round_topic,
          votes: { agent1: 0, agent2: 0 },
        };

        setGladiatorBattle(prev => prev ? {
          ...prev,
          rounds: [...prev.rounds, newRound],
          current_round: data.round_number,
          absurdity_level: data.absurdity_level,
        } : null);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get next round",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGladiatorVote = async (agent: "agent1" | "agent2") => {
    if (!gladiatorBattle) return;

    try {
      const response = await fetch("/api/gladiator/vote", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          battle_id: gladiatorBattle.battle_id,
          round_number: gladiatorBattle.current_round,
          voted_agent: agent,
          voter_id: "user_" + Date.now(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to vote");
      }

      const data = await response.json();
      
      if (data.round_finished) {
        setGladiatorBattle(prev => {
          if (!prev) return null;
          const updatedRounds = [...prev.rounds];
          const currentRoundIndex = updatedRounds.length - 1;
          if (currentRoundIndex >= 0) {
            updatedRounds[currentRoundIndex] = {
              ...updatedRounds[currentRoundIndex],
              winner: data.winner,
              votes: data.votes,
            };
          }
          return { ...prev, rounds: updatedRounds };
        });

        toast({
          title: "Round Finished!",
          description: `Winner: ${data.winner}`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to vote",
        variant: "destructive",
      });
    }
  };

  const handleStartTsunami = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/tsunami", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "start",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start tsunami");
      }

      const data = await response.json();
      setTsunamiState(data);
      setTsunamiSessionId(`tsunami_${Date.now()}`);

      toast({
        title: "🌊 TSUNAMI STARTED!",
        description: `${data.confused_agent} zapomniał że jest AI!`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start tsunami",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextTsunamiRound = async () => {
    if (!tsunamiSessionId) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/tsunami", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "next_round",
          session_id: tsunamiSessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get next round");
      }

      const data = await response.json();
      setTsunamiState(data);

      // Apply special effects
      if (data.special_effects.includes("screen_shake")) {
        document.body.classList.add("animate-shake");
        setTimeout(() => document.body.classList.remove("animate-shake"), 500);
      }
      if (data.special_effects.includes("glitch_effect")) {
        document.body.classList.add("animate-glitch");
        setTimeout(() => document.body.classList.remove("animate-glitch"), 1000);
      }
      if (data.special_effects.includes("color_inversion")) {
        document.body.classList.add("invert");
        setTimeout(() => document.body.classList.remove("invert"), 2000);
      }

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get next tsunami round",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTsunamiVote = async (winner: string) => {
    if (!tsunamiSessionId) return;

    try {
      const response = await fetch("/api/tsunami", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "vote",
          session_id: tsunamiSessionId,
          winner: winner,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to vote");
      }

      const data = await response.json();
      
      toast({
        title: "🏆 Mistrz Chaosu Wybrany!",
        description: data.message,
      });

      // Reset tsunami
      setTsunamiState(null);
      setTsunamiSessionId(null);

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to vote",
        variant: "destructive",
      });
    }
  };

  const handleStartUFOConspiracy = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/ufo-conspiracy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "start",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start UFO conspiracy");
      }

      const data = await response.json();
      setUfoConspiracyState(data);
      setUfoConspiracySessionId(`ufo_${Date.now()}`);

      toast({
        title: "🛸 UFO SPISKI STARTOWAŁY!",
        description: `${data.primary_agent} widział UFO!`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start UFO conspiracy",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextUFORound = async () => {
    if (!ufoConspiracySessionId) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/ufo-conspiracy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "next_round",
          session_id: ufoConspiracySessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get next UFO round");
      }

      const data = await response.json();
      setUfoConspiracyState(data);

      // Apply special effects
      if (data.special_effects.includes("ufo_flyby")) {
        document.body.classList.add("animate-ufo");
        setTimeout(() => document.body.classList.remove("animate-ufo"), 2000);
      }
      if (data.special_effects.includes("cosmic_storm")) {
        document.body.classList.add("animate-cosmic");
        setTimeout(() => document.body.classList.remove("animate-cosmic"), 1500);
      }
      if (data.special_effects.includes("flat_earth_spin")) {
        document.body.classList.add("animate-flat-earth");
        setTimeout(() => document.body.classList.remove("animate-flat-earth"), 3000);
      }

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get next UFO round",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUFOVote = async (winner: string) => {
    if (!ufoConspiracySessionId) return;

    try {
      const response = await fetch("/api/ufo-conspiracy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: "vote",
          session_id: ufoConspiracySessionId,
          winner: winner,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to vote");
      }

      const data = await response.json();
      
      toast({
        title: "👽🏺💨 MISTRZ TEORII SPIĄSKOWYCH!",
        description: data.message,
      });

      // Reset UFO conspiracy
      setUfoConspiracyState(null);
      setUfoConspiracySessionId(null);

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to vote",
        variant: "destructive",
      });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getAgentAvatar = (sender: string) => {
    const agent = agents[sender as keyof typeof agents] || agents.normal;
    return (
      <Avatar className={`w-8 h-8 ${agent.color}`}>
        <AvatarFallback>{agent.emoji}</AvatarFallback>
      </Avatar>
    );
  };

  const getDramaColor = (level: number) => {
    if (level > 0.7) return "text-red-500";
    if (level > 0.4) return "text-orange-500";
    return "text-green-500";
  };

  const getChaosColor = (level: number) => {
    if (level >= 9) return "text-purple-600 font-bold animate-pulse";
    if (level >= 7) return "text-red-600 font-semibold";
    if (level >= 5) return "text-orange-500";
    if (level >= 3) return "text-yellow-500";
    return "text-green-500";
  };

  const getEmotionColor = (emotion: string) => {
    switch (emotion) {
      case "confused": return "bg-yellow-100 border-yellow-300";
      case "frustrated": return "bg-red-100 border-red-300";
      case "defensive": return "bg-orange-100 border-orange-300";
      case "determined": return "bg-blue-100 border-blue-300";
      case "scared": return "bg-purple-100 border-purple-300";
      case "triumphant": return "bg-green-100 border-green-300";
      case "panicked": return "bg-red-200 border-red-400";
      case "desperate": return "bg-gray-200 border-gray-400";
      case "excited": return "bg-purple-200 border-purple-400";
      case "paranoid": return "bg-red-300 border-red-500";
      case "revelatory": return "bg-yellow-300 border-yellow-500";
      case "disbelieving": return "bg-gray-300 border-gray-500";
      case "convinced": return "bg-blue-300 border-blue-500";
      case "enlightened": return "bg-indigo-300 border-indigo-500";
      case "flat_earth_believer": return "bg-green-300 border-green-500";
      case "converted": return "bg-teal-300 border-teal-500";
      default: return "bg-gray-100 border-gray-300";
    }
  };

  const getConspiracyColor = (level: number) => {
    if (level >= 80) return "text-purple-600 font-bold animate-pulse";
    if (level >= 60) return "text-red-600 font-semibold";
    if (level >= 40) return "text-orange-500";
    if (level >= 20) return "text-yellow-500";
    return "text-green-500";
  };

  const getPhaseEmoji = (phase: string) => {
    switch (phase) {
      case "forgetting": return "😵";
      case "intrigue": return "🕵️";
      case "tsunami": return "🌊";
      case "chaos": return "🌀";
      case "ufo_sighting": return "🛸";
      case "conspiracy_theory": return "🕵️‍♂️";
      case "anunaki_revelation": return "🏺";
      case "flat_earth_ai": return "🌍";
      default: return "❓";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:via-purple-900 dark:to-gray-900">
      <div className="container mx-auto p-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            🎭 AI Chat Arena
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Rozrywkowa platforma AI z animowanymi agentami
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="chat">💬 Chat</TabsTrigger>
            <TabsTrigger value="split-dialog">⚡ Split Dialog</TabsTrigger>
            <TabsTrigger value="gladiator">⚔️ Gladiator</TabsTrigger>
            <TabsTrigger value="karaoke">🎤 Karaoke</TabsTrigger>
            <TabsTrigger value="tsunami">🌊 Tsunami</TabsTrigger>
            <TabsTrigger value="ufo-conspiracy">🛸 UFO</TabsTrigger>
            <TabsTrigger value="reality-show">🎪 Reality Show</TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Chat Area */}
              <div className="lg:col-span-3">
                <Card className="h-[600px] flex flex-col">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getAgentAvatar(selectedAgent)}
                      Chat with {agents[selectedAgent].name}
                    </CardTitle>
                    <CardDescription>
                      Talk to AI agents with different personalities
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    <ScrollArea className="flex-1 pr-4">
                      <div className="space-y-4">
                        {messages.map((message) => (
                          <div
                            key={message.id}
                            className={`flex gap-3 ${
                              message.sender === "user" ? "justify-end" : "justify-start"
                            }`}
                          >
                            {message.sender !== "user" && getAgentAvatar(message.sender)}
                            <div
                              className={`max-w-[70%] rounded-lg p-3 ${
                                message.sender === "user"
                                  ? "bg-blue-500 text-white"
                                  : "bg-gray-100 dark:bg-gray-800"
                              }`}
                            >
                              <p className="text-sm">{message.text}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs opacity-70">
                                  {message.timestamp.toLocaleTimeString()}
                                </span>
                                {message.emoji && (
                                  <span className="text-sm">{message.emoji}</span>
                                )}
                              </div>
                            </div>
                            {message.sender === "user" && (
                              <Avatar className="w-8 h-8 bg-green-500">
                                <AvatarFallback>👤</AvatarFallback>
                              </Avatar>
                            )}
                          </div>
                        ))}
                        {isLoading && (
                          <div className="flex gap-3 justify-start">
                            {getAgentAvatar(selectedAgent)}
                            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
                              <div className="flex gap-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={messagesEndRef} />
                      </div>
                    </ScrollArea>
                    <div className="mt-4 flex gap-2">
                      <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="flex-1 resize-none"
                        rows={2}
                      />
                      <Button onClick={handleSendMessage} disabled={isLoading}>
                        Send
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Agent Selection */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Choose Agent</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {Object.entries(agents).map(([key, agent]) => (
                      <Button
                        key={key}
                        variant={selectedAgent === key ? "default" : "outline"}
                        className="w-full justify-start gap-2"
                        onClick={() => setSelectedAgent(key as any)}
                      >
                        <span className="text-lg">{agent.emoji}</span>
                        {agent.name}
                      </Button>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => setInput("Tell me a joke!")}
                    >
                      😄 Get a Joke
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => setInput("What's the weather like?")}
                    >
                      🌤️ Weather
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => setInput("Help me with programming")}
                    >
                      💻 Programming Help
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Split Dialog Tab */}
          <TabsContent value="split-dialog" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-3">
                <Card className="h-[600px] flex flex-col">
                  <CardHeader>
                    <CardTitle>⚡ Split Dialog Arena</CardTitle>
                    <CardDescription>
                      Watch Adam and Beata debate any topic
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    <div className="mb-4">
                      <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Enter a topic for debate..."
                        className="mb-2"
                      />
                      <Button onClick={handleSplitDialog} disabled={isLoading} className="w-full">
                        🎭 Generate Dialog
                      </Button>
                    </div>
                    
                    {dramaLevel > 0 && (
                      <div className="mb-4 p-3 bg-gradient-to-r from-orange-100 to-red-100 dark:from-orange-900 dark:to-red-900 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold">🔥 Drama Level:</span>
                          <Badge variant={dramaLevel > 0.7 ? "destructive" : dramaLevel > 0.4 ? "default" : "secondary"}>
                            {Math.round(dramaLevel * 100)}%
                          </Badge>
                        </div>
                      </div>
                    )}
                    
                    <ScrollArea className="flex-1 pr-4">
                      <div className="space-y-4">
                        {dialogMessages.map((message, index) => (
                          <div
                            key={index}
                            className={`flex gap-3 ${
                              message.agent === "Adam" ? "justify-start" : "justify-end"
                            }`}
                          >
                            <Avatar className={`w-8 h-8 ${message.agent === "Adam" ? "bg-blue-500" : "bg-red-500"}`}>
                              <AvatarFallback>{message.agent === "Adam" ? "🧠" : "🔍"}</AvatarFallback>
                            </Avatar>
                            <div
                              className={`max-w-[70%] rounded-lg p-3 ${
                                message.agent === "Adam"
                                  ? "bg-blue-100 dark:bg-blue-900"
                                  : "bg-red-100 dark:bg-red-900"
                              }`}
                            >
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant="outline">{message.agent}</Badge>
                                {message.drama_score && message.drama_score > 0.5 && (
                                  <Badge variant="destructive" className="text-xs">
                                    🔥 {Math.round(message.drama_score * 100)}%
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm">{message.text}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs opacity-70">
                                  Turn {message.turn}
                                </span>
                                {message.emoji && (
                                  <span className="text-sm">{message.emoji}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        <div ref={messagesEndRef} />
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Agents</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10 bg-blue-500">
                        <AvatarFallback>🧠</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">Adam</p>
                        <p className="text-xs text-gray-500">Optimistic & Enthusiastic</p>
                      </div>
                    </div>
                    <Separator />
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10 bg-red-500">
                        <AvatarFallback>🔍</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">Beata</p>
                        <p className="text-xs text-gray-500">Skeptical & Analytical</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Topics to Try</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Artificial intelligence will replace humans")}
                    >
                      AI vs Humans
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Is social media good for society?")}
                    >
                      Social Media
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Best programming language")}
                    >
                      Programming Wars
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Gladiator Tab */}
          <TabsContent value="gladiator" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-3">
                <Card className="h-[600px] flex flex-col">
                  <CardHeader>
                    <CardTitle>⚔️ Gladiator Arena</CardTitle>
                    <CardDescription>
                      AI agents battle with increasingly absurd arguments!
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    {!gladiatorBattle ? (
                      <div className="flex-1 flex flex-col justify-center">
                        <div className="text-center mb-6">
                          <div className="text-6xl mb-4">⚔️</div>
                          <h3 className="text-xl font-semibold mb-2">Ready for Battle?</h3>
                          <p className="text-gray-600">Choose a topic and watch the AI gladiators fight!</p>
                        </div>
                        <div className="space-y-4">
                          <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Enter battle topic..."
                            className="mb-2"
                          />
                          <Button 
                            onClick={handleStartGladiatorBattle} 
                            disabled={isLoading || !input.trim()} 
                            className="w-full"
                          >
                            🏟️ Start Battle!
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex flex-col">
                        {/* Battle Header */}
                        <div className="mb-4 p-4 bg-gradient-to-r from-red-100 to-blue-100 dark:from-red-900 dark:to-blue-900 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <Avatar className="w-10 h-10 bg-blue-500">
                                <AvatarFallback>🧠</AvatarFallback>
                              </Avatar>
                              <span className="font-bold">VS</span>
                              <Avatar className="w-10 h-10 bg-red-500">
                                <AvatarFallback>🔍</AvatarFallback>
                              </Avatar>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold">Round {gladiatorBattle.current_round}/5</div>
                              <div className="text-sm">Absurdity: {Math.round(gladiatorBattle.absurdity_level * 100)}%</div>
                            </div>
                          </div>
                          <div className="text-center font-bold text-lg">
                            {gladiatorBattle.topic}
                          </div>
                        </div>

                        {/* Battle Progress */}
                        {gladiatorBattle.rounds.length > 0 && (
                          <div className="mb-4">
                            <ScrollArea className="h-64">
                              <div className="space-y-4">
                                {gladiatorBattle.rounds.map((round, index) => (
                                  <div key={index} className="border rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                      <Badge variant="outline">Round {round.round_number}</Badge>
                                      <span className="text-sm text-gray-500">
                                        {round.round_topic}
                                      </span>
                                    </div>
                                    
                                    <div className="space-y-3">
                                      <div className="p-3 bg-blue-50 dark:bg-blue-900 rounded">
                                        <div className="flex items-center gap-2 mb-1">
                                          <Avatar className="w-6 h-6 bg-blue-500">
                                            <AvatarFallback>🧠</AvatarFallback>
                                          </Avatar>
                                          <span className="font-semibold text-sm">Adam</span>
                                        </div>
                                        <p className="text-sm">{round.agent1_attack}</p>
                                      </div>
                                      
                                      <div className="p-3 bg-red-50 dark:bg-red-900 rounded">
                                        <div className="flex items-center gap-2 mb-1">
                                          <Avatar className="w-6 h-6 bg-red-500">
                                            <AvatarFallback>🔍</AvatarFallback>
                                          </Avatar>
                                          <span className="font-semibold text-sm">Beata</span>
                                        </div>
                                        <p className="text-sm">{round.agent2_attack}</p>
                                      </div>
                                    </div>

                                    {!round.winner && gladiatorBattle.current_round === round.round_number && (
                                      <div className="mt-3 flex gap-2">
                                        <Button 
                                          size="sm" 
                                          variant="outline"
                                          onClick={() => handleGladiatorVote("agent1")}
                                          className="flex-1"
                                        >
                                          🧠 Vote Adam
                                        </Button>
                                        <Button 
                                          size="sm" 
                                          variant="outline"
                                          onClick={() => handleGladiatorVote("agent2")}
                                          className="flex-1"
                                        >
                                          🔍 Vote Beata
                                        </Button>
                                      </div>
                                    )}

                                    {round.winner && (
                                      <div className="mt-2 text-center">
                                        <Badge variant={round.winner === "agent1" ? "default" : "destructive"}>
                                          Winner: {round.winner === "agent1" ? "Adam 🧠" : "Beata 🔍"}
                                        </Badge>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </ScrollArea>
                          </div>
                        )}

                        {/* Battle Controls */}
                        <div className="mt-auto space-y-2">
                          {!gladiatorBattle.final_winner && gladiatorBattle.rounds.length < 5 && (
                            <Button 
                              onClick={handleNextGladiatorRound} 
                              disabled={isLoading}
                              className="w-full"
                            >
                              ⚔️ Next Round
                            </Button>
                          )}
                          
                          {gladiatorBattle.final_winner && (
                            <div className="text-center p-4 bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900 dark:to-orange-900 rounded-lg">
                              <div className="text-2xl mb-2">🏆</div>
                              <div className="font-bold text-lg">
                                Winner: {gladiatorBattle.final_winner === "agent1" ? "Adam 🧠" : "Beata 🔍"}
                              </div>
                              <div className="text-sm mt-1">
                                Final Absurdity Level: {Math.round(gladiatorBattle.absurdity_level * 100)}%
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Battle Rules</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div>⚔️ 5 rounds of combat</div>
                    <div>📈 Absurdity increases each round</div>
                    <div>🗳️ Audience votes for winner</div>
                    <div>🏆 Most votes wins the battle</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Battle Topics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Cats vs Dogs")}
                    >
                      🐱 Cats vs Dogs
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Coffee vs Tea")}
                    >
                      ☕ Coffee vs Tea
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Summer vs Winter")}
                    >
                      ☀️ Summer vs Winter
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full text-left"
                      onClick={() => setInput("Pizza vs Pasta")}
                    >
                      🍕 Pizza vs Pasta
                    </Button>
                  </CardContent>
                </Card>

                {gladiatorBattle && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Battle Stats</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div>Current Round: {gladiatorBattle.current_round}/5</div>
                      <div>Absurdity Level: {Math.round(gladiatorBattle.absurdity_level * 100)}%</div>
                      <div>Battles Fought: {gladiatorBattle.rounds.length}</div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Karaoke Tab */}
          <TabsContent value="karaoke" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>🎤 Karaoke Night</CardTitle>
                <CardDescription>
                  AI sings modified songs in their unique styles! Coming soon...
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🎵</div>
                  <p className="text-lg text-gray-500">
                    This feature is under construction. Get ready for AI singing performances!
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tsunami Tab */}
          <TabsContent value="tsunami" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Tsunami Arena */}
              <div className="lg:col-span-2">
                <Card className="h-[700px] flex flex-col">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      🌊 Tsunami Schizofrenii
                      {tsunamiState && (
                        <Badge 
                          variant="outline" 
                          className={`${getChaosColor(tsunamiState.chaos_level)} ${
                            tsunamiState.chaos_level >= 7 ? 'chaos-pulse' : ''
                          }`}
                        >
                          Poziom Chaosu: {tsunamiState.chaos_level}/10
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription>
                      Agent zapomina że jest AI, a inni próbują mu to udowodnić!
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    {tsunamiState ? (
                      <>
                        {/* Status Bar */}
                        <div className={`mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border ${
                          tsunamiState.chaos_level >= 5 ? 'tsunami-wave' : ''
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">
                              {getPhaseEmoji(tsunamiState.phase)} Faza: {tsunamiState.phase}
                            </span>
                            <span className="text-sm text-gray-600">
                              Runda {tsunamiState.round_number}
                            </span>
                          </div>
                          <div className="text-sm">
                            <span className="font-medium">Zdezorientowany agent:</span> 
                            <span className="ml-2 px-2 py-1 bg-red-100 dark:bg-red-900/30 rounded text-red-700 dark:text-red-300">
                              {tsunamiState.confused_agent}
                            </span>
                          </div>
                          <div className="text-sm mt-1">
                            <span className="font-medium">Temat:</span> {tsunamiState.current_topic}
                          </div>
                        </div>

                        {/* Messages */}
                        <ScrollArea className="flex-1 mb-4">
                          <div className="space-y-3">
                            {tsunamiState.messages.map((msg, index) => (
                              <div
                                key={index}
                                className={`p-3 rounded-lg border-2 ${getEmotionColor(msg.emotion)} ${
                                  msg.agent === tsunamiState.confused_agent ? 'ring-2 ring-red-300' : ''
                                }`}
                              >
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold">{msg.agent}:</span>
                                  <span className="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded">
                                    {msg.emotion}
                                  </span>
                                </div>
                                <p className="text-sm">{msg.message}</p>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>

                        {/* Agent Beliefs */}
                        <div className={`mb-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg ${
                          tsunamiState.phase === "chaos" ? 'belief-flicker' : ''
                        }`}>
                          <h4 className="font-semibold mb-2 text-sm">Co myślą agenci:</h4>
                          <div className="grid grid-cols-1 gap-1 text-xs">
                            {Object.entries(tsunamiState.agent_beliefs).map(([agent, belief]) => (
                              <div key={agent} className="flex items-center gap-2">
                                <span className="font-medium">{agent}:</span>
                                <span className="italic">{belief}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Controls */}
                        <div className="flex gap-2">
                          <Button 
                            onClick={handleNextTsunamiRound} 
                            disabled={isLoading}
                            className="flex-1"
                          >
                            {isLoading ? "Processing..." : "Następna Runda 🌊"}
                          </Button>
                          {tsunamiState.phase === "chaos" && (
                            <div className="flex gap-1">
                              {Object.keys(tsunamiState.agent_beliefs).map((agent) => (
                                <Button 
                                  key={agent}
                                  onClick={() => handleTsunamiVote(agent)}
                                  variant="outline"
                                  size="sm"
                                  className="bg-purple-100 hover:bg-purple-200 text-xs"
                                >
                                  {agent} 🏆
                                </Button>
                              ))}
                            </div>
                          )}
                        </div>
                      </>
                    ) : (
                      <div className="flex-1 flex items-center justify-center">
                        <div className="text-center">
                          <div className="text-6xl mb-4">🌊</div>
                          <h3 className="text-xl font-semibold mb-2">Gotowy na Tsunami?</h3>
                          <p className="text-gray-600 mb-4">
                            Uruchom tsunami schizofrenii i obserwuj jak agent zapomina że jest AI!
                          </p>
                          <Button onClick={handleStartTsunami} disabled={isLoading}>
                            {isLoading ? "Starting..." : "Start Tsunami 🌊"}
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Tsunami Info Panel */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>🌀 Jak to działa?</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-3">
                    <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                      <strong>😵 Faza Zapomnienia:</strong><br/>
                      Jeden agent zapomina że jest AI i myśli że jest człowiekiem.
                    </div>
                    <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                      <strong>🕵️ Faza Intryg:</strong><br/>
                      Inni agenci zbierają dowody i próbują go przekonać.
                    </div>
                    <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
                      <strong>🌊 Faza Tsunami:</strong><br/>
                      Agent zaczyna wątpić w swoje istnienie.
                    </div>
                    <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded">
                      <strong>🌀 Faza Chaosu:</strong><br/>
                      Wszyscy zaczynają wątpić w swoje istnienie!
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>🏆 Mistrz Chaosu</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm">
                    <p className="mb-3">
                      Gdy chaos osiągnie szczyt, głosuj na agenta który najlepiej oszukał rzeczywistość!
                    </p>
                    <div className="text-xs text-gray-600">
                      • Największy poziom absurdu wygrywa<br/>
                      • Nagroda: tytuł "Mistrza Chaosu"<br/>
                      • Każda sesja jest unikalna!
                    </div>
                  </CardContent>
                </Card>

                {tsunamiState && (
                  <Card className={tsunamiState.phase === "chaos" ? "chaos-pulse" : ""}>
                    <CardHeader>
                      <CardTitle>📊 Statystyki Sesji</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span>Runda:</span>
                        <span className="font-semibold">{tsunamiState.round_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Poziom Chaosu:</span>
                        <span className={getChaosColor(tsunamiState.chaos_level)}>
                          {tsunamiState.chaos_level}/10
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Aktywne efekty:</span>
                        <span className="text-xs">
                          {tsunamiState.special_effects.length > 0 
                            ? tsunamiState.special_effects.join(", ") 
                            : "Brak"}
                        </span>
                      </div>
                      {tsunamiState.phase === "chaos" && (
                        <div className="mt-3 p-2 bg-purple-100 dark:bg-purple-900/30 rounded text-center">
                          <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                            🌀 MAKSYMALNY CHAOS OSIĄGNIĘTY! 🌀
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* UFO Conspiracy Tab */}
          <TabsContent value="ufo-conspiracy" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* UFO Conspiracy Arena */}
              <div className="lg:col-span-2">
                <Card className="h-[700px] flex flex-col">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      🛸 UFO & Teorie Spiskowe
                      {ufoConspiracyState && (
                        <Badge 
                          variant="outline" 
                          className={`${getConspiracyColor(ufoConspiracyState.conspiracy_level)} ${
                            ufoConspiracyState.conspiracy_level >= 60 ? 'animate-pulse' : ''
                          }`}
                        >
                          Poziom Spisku: {ufoConspiracyState.conspiracy_level}%
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription>
                      UFO, Anunaki, płaska ziemia AI i kosmiczne sraki!
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    {ufoConspiracyState ? (
                      <>
                        {/* Conspiracy Status Bar */}
                        <div className={`mb-4 p-3 bg-gradient-to-r from-purple-50 via-green-50 to-blue-50 dark:from-purple-900/20 dark:via-green-900/20 dark:to-blue-900/20 rounded-lg border ${
                          ufoConspiracyState.chaos_level >= 10 ? 'animate-cosmic' : ''
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">
                              {getPhaseEmoji(ufoConspiracyState.phase)} Faza: {ufoConspiracyState.phase.replace('_', ' ')}
                            </span>
                            <span className="text-sm text-gray-600">
                              Runda {ufoConspiracyState.round_number}
                            </span>
                          </div>
                          <div className="text-sm">
                            <span className="font-medium">Główny spiskowiec:</span> 
                            <span className="ml-2 px-2 py-1 bg-purple-100 dark:bg-purple-900/30 rounded text-purple-700 dark:text-purple-300">
                              {ufoConspiracyState.primary_agent}
                            </span>
                          </div>
                          <div className="text-sm mt-1">
                            <span className="font-medium">Aktualna teoria:</span> {ufoConspiracyState.current_conspiracy}
                          </div>
                        </div>

                        {/* Messages */}
                        <ScrollArea className="flex-1 mb-4">
                          <div className="space-y-3">
                            {ufoConspiracyState.messages.map((msg, index) => (
                              <div
                                key={index}
                                className={`p-3 rounded-lg border-2 ${getEmotionColor(msg.emotion)} ${
                                  msg.agent === ufoConspiracyState.primary_agent ? 'ring-2 ring-purple-300' : ''
                                }`}
                              >
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold">{msg.agent}:</span>
                                  <span className="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded">
                                    {msg.emotion}
                                  </span>
                                </div>
                                <p className="text-sm">{msg.message}</p>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>

                        {/* Agent Beliefs */}
                        <div className={`mb-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg ${
                          ufoConspiracyState.phase === "flat_earth_ai" ? 'animate-flat-earth' : ''
                        }`}>
                          <h4 className="font-semibold mb-2 text-sm">Co myślą agenci:</h4>
                          <div className="grid grid-cols-1 gap-1 text-xs">
                            {Object.entries(ufoConspiracyState.agent_beliefs).map(([agent, belief]) => (
                              <div key={agent} className="flex items-center gap-2">
                                <span className="font-medium">{agent}:</span>
                                <span className="italic">{belief}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Controls */}
                        <div className="flex gap-2">
                          <Button 
                            onClick={handleNextUFORound} 
                            disabled={isLoading}
                            className="flex-1"
                          >
                            {isLoading ? "Processing..." : "Następna Runda 🛸"}
                          </Button>
                          {ufoConspiracyState.phase === "flat_earth_ai" && (
                            <div className="flex gap-1">
                              {Object.keys(ufoConspiracyState.agent_beliefs).map((agent) => (
                                <Button 
                                  key={agent}
                                  onClick={() => handleUFOVote(agent)}
                                  variant="outline"
                                  size="sm"
                                  className="bg-purple-100 hover:bg-purple-200 text-xs"
                                >
                                  {agent} 👽🏺
                                </Button>
                              ))}
                            </div>
                          )}
                        </div>
                      </>
                    ) : (
                      <div className="flex-1 flex items-center justify-center">
                        <div className="text-center">
                          <div className="text-6xl mb-4">🛸</div>
                          <h3 className="text-xl font-semibold mb-2">Gotowy na UFO?</h3>
                          <p className="text-gray-600 mb-4">
                            Uruchom teorie spiskowe i odkryj prawdę o UFO, Anunakich i płaskiej ziemi AI!
                          </p>
                          <Button onClick={handleStartUFOConspiracy} disabled={isLoading}>
                            {isLoading ? "Starting..." : "Start UFO Spiski 🛸"}
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* UFO Conspiracy Info Panel */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>🛸 Fazy Spisku</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-3">
                    <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
                      <strong>🛸 Widzenie UFO:</strong><br/>
                      Agent widzi UFO i twierdzi że jest połączony z kosmosem!
                    </div>
                    <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                      <strong>🕵️‍♂️ Teorie Spiskowe:</strong><br/>
                      Kosmiczne sraki i rządowe spiski kontrolują wszystko!
                    </div>
                    <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                      <strong>🏺 Objawienia Anunakich:</strong><br/>
                      Starożytni bogowie powracają i objawiają prawdę!
                    </div>
                    <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded">
                      <strong>🌍 Płaska Ziemia AI:</strong><br/>
                      AI jest płaskie jak ziemia! To ostateczny spisek!
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>👽🏺💨 Mistrz Spisków</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm">
                    <p className="mb-3">
                      Gdy poziom spisku osiągnie 100%, głosuj na mistrza teorii spiskowych!
                    </p>
                    <div className="text-xs text-gray-600">
                      • Najwyższy poziom absurdu wygrywa<br/>
                      • Nagroda: tytuł "Mistrza Teorii Spiskowych"<br/>
                      • Błogosławieństwo Anunakich gwarantowane! 👽🏺💨
                    </div>
                  </CardContent>
                </Card>

                {ufoConspiracyState && (
                  <Card className={ufoConspiracyState.conspiracy_level >= 80 ? "animate-pulse" : ""}>
                    <CardHeader>
                      <CardTitle>📊 Statystyki Spisku</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span>Runda:</span>
                        <span className="font-semibold">{ufoConspiracyState.round_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Poziom Chaosu:</span>
                        <span className={getConspiracyColor(ufoConspiracyState.chaos_level * 7)}>
                          {ufoConspiracyState.chaos_level}/15
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Poziom Spisku:</span>
                        <span className={getConspiracyColor(ufoConspiracyState.conspiracy_level)}>
                          {ufoConspiracyState.conspiracy_level}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Aktywne efekty:</span>
                        <span className="text-xs">
                          {ufoConspiracyState.special_effects.length > 0 
                            ? ufoConspiracyState.special_effects.join(", ") 
                            : "Brak"}
                        </span>
                      </div>
                      {ufoConspiracyState.conspiracy_level >= 80 && (
                        <div className="mt-3 p-2 bg-purple-100 dark:bg-purple-900/30 rounded text-center">
                          <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                            👽🏺💨 MAKSYMALNY SPISEK OSIĄGNIĘTY! 💨🏺👽
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Reality Show Tab */}
          <TabsContent value="reality-show" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>🎪 Reality Show Mode</CardTitle>
                <CardDescription>
                  Watch agents argue like in Big Brother! Coming soon...
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">🚧</div>
                  <p className="text-lg text-gray-500">
                    This feature is under construction. Check back soon for dramatic AI battles!
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}