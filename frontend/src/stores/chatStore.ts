import { create } from 'zustand';
import { useUIStore } from './uiStore';

export interface Step {
  title: string;
  tool: string;
  input?: string;
  output?: string;
  status: 'ok' | 'err' | 'warn';
  duration?: number;
}

export interface Message {
  id: string;
  text: string;
  role: 'user' | 'agent';
  timestamp: Date;
  chart?: {
    title: string;
    mode: 'line' | 'bar';
    points: { month: string; cases: number }[];
  };
  plotlyData?: any;
  steps?: Step[];
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  threadId?: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ChatState {
  chats: Chat[];
  currentChatId: string | null;
  isLoading: boolean;
  
  createChat: (title?: string) => string;
  deleteChat: (chatId: string) => void;
  setCurrentChat: (chatId: string | null) => void;
  addMessage: (chatId: string, message: Omit<Message, 'id' | 'timestamp'>) => string;
  updateMessage: (chatId: string, messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (chatId: string, messageId: string) => void;
  clearChat: (chatId: string) => void;
  setLoading: (loading: boolean) => void;
  getChatById: (chatId: string) => Chat | undefined;
  getCurrentChat: () => Chat | undefined;
  setThreadId: (chatId: string, threadId: string) => void;
  sendMessage: (text: string) => Promise<void>;
}

const API_URL = 'http://localhost:8000';

let msgIdCounter = 0;
const genMsgId = () => `msg_${Date.now()}_${++msgIdCounter}`;

// Extract answer from various formats
const extractAnswer = (answer: any): string => {
  if (!answer) return '';
  if (typeof answer === 'string') {
    // Check if it's JSON string
    if (answer.startsWith('{') || answer.startsWith('[')) {
      try {
        const parsed = JSON.parse(answer);
        return parsed.answer || parsed.text || JSON.stringify(parsed);
      } catch {
        return answer;
      }
    }
    return answer;
  }
  if (typeof answer === 'object') {
    return answer.answer || answer.text || JSON.stringify(answer);
  }
  return String(answer);
};

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  currentChatId: null,
  isLoading: false,

  createChat: (title = 'New Chat') => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    set(state => ({
      chats: [newChat, ...state.chats],
      currentChatId: newChat.id,
    }));
    
    return newChat.id;
  },

  deleteChat: (chatId) => {
    set(state => {
      const newChats = state.chats.filter(chat => chat.id !== chatId);
      const newCurrentChatId = state.currentChatId === chatId 
        ? (newChats.length > 0 ? newChats[0].id : null)
        : state.currentChatId;
      
      return {
        chats: newChats,
        currentChatId: newCurrentChatId,
      };
    });
  },

  setCurrentChat: (chatId) => {
    set({ currentChatId: chatId });
  },

  addMessage: (chatId, message) => {
    const newMessage: Message = {
      ...message,
      id: genMsgId(),
      timestamp: new Date(),
    };
    
    set(state => ({
      chats: state.chats.map(chat => 
        chat.id === chatId
          ? {
              ...chat,
              messages: [...chat.messages, newMessage],
              updatedAt: new Date(),
            }
          : chat
      ),
    }));
    
    return newMessage.id;
  },

  updateMessage: (chatId, messageId, updates) => {
    set(state => ({
      chats: state.chats.map(chat => 
        chat.id === chatId
          ? {
              ...chat,
              messages: chat.messages.map(msg => 
                msg.id === messageId ? { ...msg, ...updates } : msg
              ),
              updatedAt: new Date(),
            }
          : chat
      ),
    }));
  },

  deleteMessage: (chatId, messageId) => {
    set(state => ({
      chats: state.chats.map(chat => 
        chat.id === chatId
          ? {
              ...chat,
              messages: chat.messages.filter(msg => msg.id !== messageId),
              updatedAt: new Date(),
            }
          : chat
      ),
    }));
  },

  clearChat: (chatId) => {
    set(state => ({
      chats: state.chats.map(chat => 
        chat.id === chatId
          ? { ...chat, messages: [], threadId: undefined, updatedAt: new Date() }
          : chat
      ),
    }));
    useUIStore.getState().setSelectedChartMessageId(null);
    useUIStore.getState().closeChart();
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  getChatById: (chatId) => {
    return get().chats.find(chat => chat.id === chatId);
  },

  getCurrentChat: () => {
    const { chats, currentChatId } = get();
    return currentChatId ? chats.find(chat => chat.id === currentChatId) : undefined;
  },

  setThreadId: (chatId, threadId) => {
    set(state => ({
      chats: state.chats.map(chat =>
        chat.id === chatId ? { ...chat, threadId } : chat
      ),
    }));
  },

  sendMessage: async (text: string) => {
    const { currentChatId, createChat, addMessage, updateMessage, setLoading, getChatById, setThreadId } = get();

    let chatId = currentChatId;
    if (!chatId) {
      chatId = createChat();
    }

    addMessage(chatId, { role: 'user', text });
    setLoading(true);

    // Create agent message immediately for streaming steps
    const agentMsgId = addMessage(chatId, { role: 'agent', text: '', steps: [] });

    try {
      const chat = getChatById(chatId);
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          thread_id: chat?.threadId || null,
        }),
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader');

      const decoder = new TextDecoder();
      let finalAnswer = '';
      let plotlyData: any = null;
      let threadId: string | null = null;
      const steps: Step[] = [];
      let currentStepIdx = -1;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          
          try {
            const data = JSON.parse(line.substring(6));
            
            if (data.type === 'step') {
              // New step - add it with input (tool name and any thought)
              const step: Step = {
                title: `Step ${data.step}`,
                tool: data.tool || 'thought',
                input: data.thought || '',
                output: '',
                status: 'ok',
                duration: data.duration
              };
              steps.push(step);
              currentStepIdx = steps.length - 1;
              
              // Update message with new step immediately
              updateMessage(chatId!, agentMsgId, { steps: [...steps] });
            }
            
            if (data.type === 'tool_result') {
              // Update current step with output
              if (currentStepIdx >= 0 && steps[currentStepIdx]) {
                steps[currentStepIdx].output = data.result || '';
                updateMessage(chatId!, agentMsgId, { steps: [...steps] });
              }
            }
            
            if (data.type === 'visualization' && data.data) {
              plotlyData = data.data;
              // Add visualization step
              steps.push({
                title: 'Visualization',
                tool: 'chart',
                input: 'Generate chart',
                output: 'Graph generated',
                status: 'ok',
                duration: data.duration
              });
              updateMessage(chatId!, agentMsgId, { steps: [...steps], plotlyData });
            }
            
            if (data.type === 'final') {
              finalAnswer = extractAnswer(data.answer);
              if (data.visualization && !plotlyData) {
                plotlyData = data.visualization;
              }
              if (data.thread_id) {
                threadId = data.thread_id;
              }
            }
            
            if (data.type === 'error') {
              finalAnswer = `Error: ${data.message}`;
              steps.push({
                title: 'Error',
                tool: 'error',
                input: '',
                output: data.message,
                status: 'err'
              });
              updateMessage(chatId!, agentMsgId, { steps: [...steps] });
            }
          } catch {}
        }
      }

      if (threadId) {
        setThreadId(chatId!, threadId);
      }

      // Final update with answer and plotly data
      updateMessage(chatId!, agentMsgId, { 
        text: finalAnswer || 'Response received', 
        plotlyData,
        steps: steps.length > 0 ? steps : undefined 
      });

    } catch (error) {
      updateMessage(chatId!, agentMsgId, { text: `Connection error: ${error}` });
    } finally {
      setLoading(false);
    }
  },
}));
