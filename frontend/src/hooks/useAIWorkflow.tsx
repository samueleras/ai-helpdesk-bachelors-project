import { useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { WorkflowResponse } from "../entities/WorkflowRepsonse";
import { WorkflowRequest } from "../entities/WorkflowRequest";

const workflowClient = new APIClient<WorkflowResponse>("/init_ai_workflow");

const useAIWorkflow = (
  workflowRequest: WorkflowRequest,
  accessToken: string
) => {
  return useQuery<WorkflowResponse>({
    queryKey: ["workflow", workflowRequest],
    queryFn: () => workflowClient.initAIWorkflow(workflowRequest, accessToken),
    retry: 2,
    staleTime: Infinity,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchInterval: false,
    refetchOnMount: false,
    enabled: false,
    gcTime: 0,
  });
};

export default useAIWorkflow;
