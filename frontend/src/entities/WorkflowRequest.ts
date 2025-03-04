export interface WorkflowRequest {
  conversation: [string, string][];
  ticket: boolean;
  execution_count: number;
}
