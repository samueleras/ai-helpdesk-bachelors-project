export interface SimilarTicket {
  distance: number;
  entity: { title: string };
  id: number;
}

export interface TicketMessage {
  message: string;
  author_name: string;
  group: string;
  created_at: Date;
}

export interface Ticket {
  ticket_id: number;
  title: string;
  content: string;
  creation_date: Date;
  closed_date?: Date | null;
  author_name: string;
  assignee_name?: string | null;
  similar_tickets: SimilarTicket[];
  ticket_messages: TicketMessage[];
}
