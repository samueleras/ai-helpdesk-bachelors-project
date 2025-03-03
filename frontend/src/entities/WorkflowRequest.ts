export interface WorkflowRequest {
  conversation: [string, string][];
  query_prompt?: string;
  ticket: boolean;
  execution_count: number;
}
