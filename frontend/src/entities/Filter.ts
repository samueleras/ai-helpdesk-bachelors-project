export interface Filter {}

export interface TicketFilter extends Filter {
  assignee_id?: string;
}
