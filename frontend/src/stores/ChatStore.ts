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

const useChatStore = create<ChatStore>((set) => ({
  conversation: [],
  executionCount: 0,
  ticket: false,
  ticketButton: false,
  workflowRequest: {
    conversation: [],
    execution_count: 0,
    ticket: false,
  },

  setConversation: (conversation) => set({ conversation }),
  setExecutionCount: (count) => set({ executionCount: count }),
  setTicket: (ticket) => set({ ticket }),
  setTicketButton: (ticketButton) => set({ ticketButton }),
  setWorkflowRequest: (request) => set({ workflowRequest: request }),

  resetChat: () =>
    set({
      conversation: [],
      executionCount: 0,
      ticket: false,
      ticketButton: false,
      workflowRequest: {
        conversation: [],
        execution_count: 0,
        ticket: false,
      },
    }),
}));

export default useChatStore;
