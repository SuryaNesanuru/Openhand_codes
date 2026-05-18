"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Settings, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls?: Array<{ name: string; args: Record<string, unknown> };
  created_at: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentConv, setCurrentConv] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
      created_at: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg.content,
          conversation_id: currentConv,
        }),
      });
      
      const data = await res.json();
      
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message || "Configure a backend to enable AI responses.",
        created_at: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, assistantMsg]);
      setCurrentConv(data.conversation_id);
    } catch {
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Configure the backend to enable real AI responses.",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <aside className="w-64 border-r border-border bg-card p-4">
        <div className="flex items-center gap-2 mb-4">
          <Bot className="w-6 h-6 text-primary" />
          <span className="font-bold">Agent Platform</span>
        </div>
        <Button onClick={() => setMessages([])} variant="outline" className="w-full mb-4">
          <Plus className="w-4 h-4 mr-2" />New Chat
        </Button>
      </aside>
      
      <main className="flex-1 flex flex-col">
        <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <Bot className="w-12 h-12 mx-auto mb-4 text-primary" />
                <p className="text-lg">Start a conversation</p>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center"><Bot className="w-4 h-4 text-primary" /></div>}
                <div className={`max-w-[70%] rounded-lg px-4 py-2 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  <p>{msg.content}</p>
                </div>
                {msg.role === "user" && <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center"><User className="w-4 h-4" /></div>}
              </div>
            ))
          )}
          {loading && <div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /><span>Thinking...</span></div>}
        </div>
        
        <div className="p-4 border-t border-border">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Message..." className="flex-1 bg-muted rounded-lg px-4 py-3" />
            <Button type="submit" disabled={loading}><Send className="w-4 h-4" /></Button>
          </form>
        </div>
      </main>
    </div>
  );
}