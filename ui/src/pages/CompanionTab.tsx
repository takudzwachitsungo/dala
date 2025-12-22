import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Sparkles, Shield, X } from 'lucide-react';
import { apiClient, ChatWebSocket } from '../api/client';
import { MarkdownText } from '../components/MarkdownText';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
};

export function CompanionTab() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mode, setMode] = useState<'listen' | 'reflect' | 'ground'>('listen');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [wsConnection, setWsConnection] = useState<ChatWebSocket | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentResponseRef = useRef<string>('');
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth'
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize conversation and WebSocket
  useEffect(() => {
    const initializeConversation = async () => {
      try {
        // Check if there's an existing active conversation
        const conversations = await apiClient.getConversations(0, 1);
        let conversation;
        
        if (conversations.length > 0 && conversations[0].is_active) {
          // Load existing active conversation
          conversation = conversations[0];
          setConversationId(conversation.id);
          
          // Load message history
          setIsLoadingHistory(true);
          const history = await apiClient.getConversationMessages(conversation.id, 0, 100);
          const loadedMessages = history.map((msg: any) => ({
            id: msg.id,
            role: msg.role,
            text: msg.content,
            timestamp: new Date(msg.created_at)
          }));
          setMessages(loadedMessages);
          setIsLoadingHistory(false);
        } else {
          // Create a new conversation
          conversation = await apiClient.createConversation(mode);
          setConversationId(conversation.id);
          setIsLoadingHistory(false);
        }

        // Connect WebSocket
        const token = apiClient.getToken();
        if (!token) {
          console.error('No auth token found');
          return;
        }

        const ws = new ChatWebSocket(token, conversation.id);
        
        await ws.connect(
          (message) => {
            if (message.type === 'connected') {
              console.log('Connected to Dala:', message.message);
              setIsConnecting(false);
            } else if (message.type === 'chunk') {
              // Streaming response chunks
              currentResponseRef.current += message.content;
              setMessages(prev => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === 'assistant' && lastMsg.id === 'typing') {
                  return [
                    ...prev.slice(0, -1),
                    { ...lastMsg, text: currentResponseRef.current }
                  ];
                }
                return prev;
              });
            } else if (message.type === 'done') {
              // Complete the response
              const finalText = currentResponseRef.current;
              currentResponseRef.current = '';
              setMessages(prev => {
                const filtered = prev.filter(m => m.id !== 'typing');
                return [
                  ...filtered,
                  {
                    id: message.message_id || Date.now().toString(),
                    role: 'assistant',
                    text: finalText,
                    timestamp: new Date()
                  }
                ];
              });
              setIsTyping(false);
            } else if (message.type === 'typing') {
              setIsTyping(message.status);
            } else if (message.type === 'error') {
              console.error('WebSocket error:', message.message);
              setIsTyping(false);
            }
          },
          (error) => {
            console.error('WebSocket connection error:', error);
            setIsConnecting(false);
          }
        );

        setWsConnection(ws);
      } catch (error) {
        console.error('Failed to initialize conversation:', error);
        setIsConnecting(false);
      }
    };

    initializeConversation();

    // Cleanup on unmount
    return () => {
      wsConnection?.disconnect();
    };
  }, [mode]);
  const handleSend = () => {
    if (!inputValue.trim() || !wsConnection || !wsConnection.isConnected()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: inputValue,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    
    // Send message via WebSocket
    try {
      wsConnection.sendMessage(inputValue, mode);
      currentResponseRef.current = '';
      
      // Add typing placeholder
      setMessages(prev => [...prev, {
        id: 'typing',
        role: 'assistant',
        text: '',
        timestamp: new Date()
      }]);
      setIsTyping(true);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
    
    setInputValue('');
  };
  return <div className="flex flex-col h-[calc(100vh-4rem)] bg-background relative pb-20">
      <div className="max-w-2xl mx-auto w-full flex flex-col h-full">
        {/* Header */}
        <div className="px-6 py-4 border-b border-divider/50 flex items-center justify-between bg-background/80 backdrop-blur-sm z-10">
          <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-sage/20 flex items-center justify-center text-sage">
            <Sparkles size={16} />
          </div>
          <div>
            <h2 className="text-sm font-medium text-primary">Dala Companion</h2>
            <p className="text-[10px] text-sage font-medium">Listening now</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <select value={mode} onChange={e => setMode(e.target.value as any)} className="text-xs bg-secondary/10 text-primary border-none rounded-full px-3 py-1.5 focus:ring-1 focus:ring-sage outline-none">
            <option value="listen">Just Listen</option>
            <option value="reflect">Reflect</option>
            <option value="ground">Ground Me</option>
          </select>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-3 pb-24">
        <div className="flex justify-center mb-8">
          <div className="bg-sage/10 text-sage text-xs px-4 py-2 rounded-full flex items-center space-x-2">
            <Shield size={12} />
            <span>Private & Non-judgmental space</span>
          </div>
        </div>

        {isLoadingHistory && (
          <div className="flex justify-center items-center py-8">
            <div className="text-sm text-secondary">Loading conversation history...</div>
          </div>
        )}

        {messages.map(msg => <motion.div key={msg.id} initial={{
        opacity: 0,
        y: 10
      }} animate={{
        opacity: 1,
        y: 0
      }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user' ? 'bg-primary text-white rounded-tr-sm' : 'bg-white border border-divider/50 text-primary rounded-tl-sm shadow-sm'}`}>
              {msg.role === 'assistant' ? (
                <MarkdownText text={msg.text} />
              ) : (
                msg.text
              )}
            </div>
          </motion.div>)}

        {isTyping && <motion.div initial={{
        opacity: 0
      }} animate={{
        opacity: 1
      }} className="flex justify-start">
            <div className="bg-white border border-divider/50 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm flex space-x-1">
              <motion.div animate={{
            scale: [1, 1.2, 1]
          }} transition={{
            repeat: Infinity,
            duration: 1.5,
            delay: 0
          }} className="w-1.5 h-1.5 bg-sage/40 rounded-full" />
              <motion.div animate={{
            scale: [1, 1.2, 1]
          }} transition={{
            repeat: Infinity,
            duration: 1.5,
            delay: 0.2
          }} className="w-1.5 h-1.5 bg-sage/60 rounded-full" />
              <motion.div animate={{
            scale: [1, 1.2, 1]
          }} transition={{
            repeat: Infinity,
            duration: 1.5,
            delay: 0.4
          }} className="w-1.5 h-1.5 bg-sage rounded-full" />
            </div>
          </motion.div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-background border-t border-divider/50">
        <div className="relative flex items-center max-w-2xl mx-auto">
          <input type="text" value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSend()} placeholder="Type your thoughts..." className="w-full bg-white border border-divider rounded-full pl-6 pr-24 py-4 text-sm focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage transition-all shadow-sm" />
          <div className="absolute right-2 flex items-center space-x-1">
            <button className="p-2 text-secondary hover:text-primary transition-colors">
              <Mic size={20} />
            </button>
            <button onClick={handleSend} disabled={!inputValue.trim()} className="p-2 bg-sage text-white rounded-full hover:bg-sage-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
      </div>
    </div>;
}