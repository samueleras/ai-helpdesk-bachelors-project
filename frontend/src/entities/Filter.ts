export interface Filter {
  page?: number;
  page_size?: number;
}

export interface TicketFilter extends Filter {
  assignee_id?: string;
  closed?: boolean;
  order?: string;
  search?: string;
}
