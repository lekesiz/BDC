import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  Bot,
  Send,
  User,
  RotateCcw,
  Settings,
  Download,
  Sparkles,
  Mic,
  Paperclip,
  X,
  Info
} from 'lucide-react';

const AIChatbotPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hello! I'm your AI learning assistant. How can I help you today?",
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [context, setContext] = useState('general');
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    language: 'en',
    personality: 'professional',
    rememberContext: true,
    maxLength: 500
  });
  const [suggestedQuestions] = useState([
    "What are my current learning goals?",
    "Can you help me understand this concept?",
    "What's my progress in the current program?",
    "Can you suggest resources for improvement?",
    "How can I prepare for my next test?"
  ]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (message = input) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setTyping(true);

    try {
      const res = await fetch('/api/ai/chatbot/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: message,
          context: context,
          settings: settings,
          conversation_history: messages.slice(-10) // Send last 10 messages for context
        })
      });

      if (!res.ok) throw new Error('Failed to get response');

      const data = await res.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions || [],
        resources: data.resources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: 'Error',
        description: 'Failed to get response from AI assistant',
        variant: 'destructive'
      });
    } finally {
      setTyping(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      setMessages([
        {
          id: 1,
          type: 'assistant',
          content: "Chat cleared. How can I help you today?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  };

  const handleExportChat = () => {
    const chatText = messages.map(msg => 
      `${msg.type === 'user' ? 'You' : 'AI Assistant'}: ${msg.content}\n`
    ).join('\n');

    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleSaveSettings = () => {
    toast({
      title: 'Success',
      description: 'Settings saved successfully'
    });
    setShowSettings(false);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Learning Assistant</h1>
          <Badge variant="secondary">
            {context === 'general' ? 'General Help' : context}
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearChat}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportChat}
          >
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="p-4 mb-4">
          <h3 className="font-medium mb-3">Chat Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Language
              </label>
              <select
                value={settings.language}
                onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="en">English</option>
                <option value="fr">French</option>
                <option value="es">Spanish</option>
                <option value="de">German</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Personality
              </label>
              <select
                value={settings.personality}
                onChange={(e) => setSettings({ ...settings, personality: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="tutor">Tutor</option>
                <option value="coach">Coach</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="rememberContext"
                checked={settings.rememberContext}
                onChange={(e) => setSettings({ ...settings, rememberContext: e.target.checked })}
                className="rounded text-primary"
              />
              <label htmlFor="rememberContext" className="text-sm">
                Remember conversation context
              </label>
            </div>

            <div className="flex justify-end">
              <Button size="sm" onClick={handleSaveSettings}>
                Save Settings
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Context Selection */}
      <div className="flex gap-2 mb-4">
        <Button
          variant={context === 'general' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setContext('general')}
        >
          General Help
        </Button>
        <Button
          variant={context === 'program' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setContext('program')}
        >
          Program Questions
        </Button>
        <Button
          variant={context === 'test' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setContext('test')}
        >
          Test Preparation
        </Button>
        <Button
          variant={context === 'career' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setContext('career')}
        >
          Career Guidance
        </Button>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                <div className="flex items-end gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' ? 'bg-primary text-white order-2' : 'bg-gray-200 order-1'
                  }`}>
                    {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  
                  <div className={`order-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block p-3 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-primary text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="mt-2 space-y-1">
                        <p className="text-xs text-gray-500">Suggested follow-ups:</p>
                        {message.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSendMessage(suggestion)}
                            className="block text-sm text-blue-600 hover:underline text-left"
                          >
                            • {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    {message.resources && message.resources.length > 0 && (
                      <div className="mt-2 space-y-1">
                        <p className="text-xs text-gray-500">Helpful resources:</p>
                        {message.resources.map((resource, index) => (
                          <a
                            key={index}
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block text-sm text-blue-600 hover:underline"
                          >
                            • {resource.title}
                          </a>
                        ))}
                      </div>
                    )}
                    
                    <p className="text-xs text-gray-400 mt-1">
                      {formatTimestamp(message.timestamp)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {typing && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length === 1 && (
          <div className="px-4 pb-2">
            <p className="text-sm text-gray-500 mb-2">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(question)}
                  className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t">
          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            
            <Input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              disabled={typing}
            />
            
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled
            >
              <Mic className="h-4 w-4" />
            </Button>
            
            <Button
              type="submit"
              disabled={!input.trim() || typing}
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
          
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <Info className="h-3 w-3" />
            <span>AI responses are generated and may not always be accurate</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AIChatbotPage;