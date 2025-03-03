export interface WorkflowResponse {
  llm_output: string;
  ticket_title: string;
  ticket_content: string;
  ticket_summary: string;
  query_prompt: string;
  ticket: boolean;
}
