import { create } from "zustand";
import { TicketFilter } from "@/entities/Filter";
interface FilterStore {
  ticketFilter: TicketFilter;
  updateTicketFilter: (ticketFilter: TicketFilter) => void;
}

const useFilterStore = create<FilterStore>((set) => ({
  ticketFilter: { closed: false },
  updateTicketFilter: (ticketFilter: TicketFilter) =>
    set(() => ({ ticketFilter })),
}));

export default useFilterStore;
