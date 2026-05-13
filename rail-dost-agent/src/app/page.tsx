"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Train, Clock, MapPin, RefreshCw } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  trains?: Train[];
}

interface Train {
  trainNumber: string;
  trainName: string;
  from: string;
  to: string;
  departure: string;
  arrival: string;
  duration: string;
  classes: string[];
}

function cn(...inputs: (string | undefined)[]) {
  return twMerge(clsx(inputs));
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Namaste! 🙏 I'm Rail Dost, your Indian Railways assistant. Ask me about trains between any stations like:\n\n• New Delhi to Mumbai\n• Howrah to Chennai\n• Bangalore to Jaipur\n\nI can help you find train numbers, timings, and class availability!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userMessage,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message || "Here are the trains I found:",
        trains: data.trains,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, something went wrong. Please try again!",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center">
              <Train className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Rail Dost</h1>
              <p className="text-xs text-slate-400">AI Train Assistant</p>
            </div>
          </div>
          <button
            onClick={() =>
              setMessages([
                {
                  id: "welcome",
                  role: "assistant",
                  content:
                    "Namaste! 🙏 I'm Rail Dost, your Indian Railways assistant. Ask me about trains between any stations like:\n\n• New Delhi to Mumbai\n• Howrah to Chennai\n• Bangalore to Jaipur\n\nI can help you find train numbers, timings, and class availability!",
                },
              ])
            }
            className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-slate-300" />
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="max-w-4xl mx-auto px-4 py-6 h-[calc(100vh-180px)] overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3",
                  message.role === "user"
                    ? "bg-orange-500 text-white rounded-br-md"
                    : "bg-white/10 text-slate-100 rounded-bl-md"
                )}
              >
                {message.role === "user" ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <>
                    <p className="whitespace-pre-wrap mb-3">{message.content}</p>
                    {/* Train Cards */}
                    {message.trains && message.trains.length > 0 && (
                      <div className="space-y-2">
                        {message.trains.map((train, idx) => (
                          <div
                            key={idx}
                            className="bg-white/5 rounded-xl p-3 border border-white/10"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-orange-400 font-bold text-sm">
                                {train.trainNumber}
                              </span>
                              <span className="text-slate-400 text-xs">
                                {train.duration}
                              </span>
                            </div>
                            <h4 className="font-semibold text-sm mb-2">
                              {train.trainName}
                            </h4>
                            <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                              <div className="flex items-center gap-1">
                                <MapPin className="w-3 h-3 text-orange-400" />
                                <span>
                                  {train.from} → {train.to}
                                </span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3 text-orange-400" />
                                <span>
                                  {train.departure} - {train.arrival}
                                </span>
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {train.classes.map((cls) => (
                                <span
                                  key={cls}
                                  className="px-2 py-0.5 bg-orange-500/20 text-orange-300 text-xs rounded"
                                >
                                  {cls}
                                </span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white/10 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                  <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/10 backdrop-blur-md border-t border-white/10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about trains..."
              className="flex-1 bg-white/10 border border-white/20 rounded-full px-4 py-3 text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="bg-orange-500 hover:bg-orange-600 disabled:bg-orange-500/50 disabled:cursor-not-allowed p-3 rounded-full transition-colors"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </form>
          <p className="text-center text-xs text-slate-500 mt-2">
            Powered by Rail Dost • IRCTC Compatible
          </p>
        </div>
      </div>
    </div>
  );
}
