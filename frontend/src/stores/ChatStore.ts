import { create } from "zustand";
import { WorkflowRequest } from "../entities/WorkflowRequest";

interface ChatStore {
  conversation: [string, string][];
  executionCount: number;
  ticket: boolean;
  ticketButton: boolean;
  workflowRequest: WorkflowRequest;
  setConversation: (conversation: [string, string][]) => void;
  setExecutionCount: (count: number) => void;
  setTicket: (ticket: boolean) => void;
  setTicketButton: (ticketButton: boolean) => void;
  setWorkflowRequest: (request: WorkflowRequest) => void;
  resetChat: () => void;
}

interface ChatState {
  conversation: [string, string][];
  executionCount: number;
  ticket: boolean;
  ticketButton: boolean;
  workflowRequest: WorkflowRequest;
}

const getChatStateFromLocalStorage = () => {
  const chatState = localStorage.getItem("ChatState");
  return chatState ? JSON.parse(chatState) : {};
};

const setChatStateFromLocalStorage = (state: ChatState) => {
  localStorage.setItem("ChatState", JSON.stringify(state));
};

const useChatStore = create<ChatStore>((set) => {
  const savedState = getChatStateFromLocalStorage();

  return {
    conversation: savedState.conversation || [],
    executionCount: savedState.executionCount || 0,
    ticket: savedState.ticket || false,
    ticketButton: savedState.ticketButton || false,
    workflowRequest: savedState.workflowRequest || {
      conversation: [],
      execution_count: 0,
      ticket: false,
    },

    setConversation: (conversation) =>
      set((state) => {
        const newState = { ...state, conversation };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),

    setExecutionCount: (count) =>
      set((state) => {
        const newState = { ...state, executionCount: count };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),

    setTicket: (ticket) =>
      set((state) => {
        const newState = { ...state, ticket };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),

    setTicketButton: (ticketButton) =>
      set((state) => {
        const newState = { ...state, ticketButton };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),

    setWorkflowRequest: (request) =>
      set((state) => {
        const newState = { ...state, workflowRequest: request };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),

    resetChat: () =>
      set(() => {
        const newState = {
          conversation: [],
          executionCount: 0,
          ticket: false,
          ticketButton: false,
          workflowRequest: {
            conversation: [],
            execution_count: 0,
            ticket: false,
          },
        };
        setChatStateFromLocalStorage(newState);
        return newState;
      }),
  };
});

export default useChatStore;
