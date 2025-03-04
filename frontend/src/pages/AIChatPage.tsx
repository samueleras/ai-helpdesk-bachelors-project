import { FormEvent, useEffect, useRef, useState } from "react";
import useAuthStore from "../stores/AuthStore";
import { useNavigate } from "react-router-dom";
import useAIWorkflow from "../hooks/useAIWorkflow";
import useChatStore from "../stores/ChatStore";
import ReactMarkdown from "react-markdown";

const AIChatPage = () => {
  const inputRef = useRef<HTMLInputElement>(null);
  const { accessToken } = useAuthStore();
  const [isFirstRender, setIsFirstRender] = useState(true);
  const {
    conversation,
    setConversation,
    executionCount,
    setExecutionCount,
    ticket,
    setTicket,
    ticketButton,
    setTicketButton,
    workflowRequest,
    setWorkflowRequest,
    resetChat,
  } = useChatStore();
  const navigate = useNavigate();

  const {
    data: workflowResponse,
    error,
    isFetching,
    refetch,
  } = useAIWorkflow(workflowRequest, accessToken);

  useEffect(() => {
    if (isFirstRender) {
      setIsFirstRender(false);
      return;
    }
    if (workflowResponse) {
      console.log(workflowResponse);
      if (workflowResponse.ticket_id) {
        navigate(`/ticket/${workflowResponse.ticket_id}`);
        return;
      }
      setConversation([...conversation, ["ai", workflowResponse.llm_output]]);
      setExecutionCount(executionCount + 1);
      if (workflowResponse.ticket) {
        if (workflowResponse.ticket && !ticket) {
          setTicketButton(true);
          setExecutionCount(0);
        }
        setTicket(true);
      }
    }
  }, [workflowResponse]);

  useEffect(() => {
    if (isFirstRender) {
      setIsFirstRender(false);
      return;
    }
    if (workflowRequest?.conversation.length != 0) {
      console.log(
        "Workflow Request:",
        JSON.stringify(workflowRequest, null, 2)
      );
      refetch();
    }
  }, [workflowRequest]);

  const handleTicketCreation = () => {
    setTicketButton(false);
    handleSubmit("Please create a Ticket.");
  };

  const handleSendMessage = (event: FormEvent) => {
    //prevents page reload
    event.preventDefault();
    let inputValue = inputRef.current?.value;
    //Only executes if inputValue is not an empty String
    if (inputValue) handleSubmit(inputValue);
  };

  const handleSubmit = (inputValue: string) => {
    const updatedConversation: [string, string][] = [
      ...conversation,
      ["human", inputValue],
    ];
    setConversation(updatedConversation);
    setWorkflowRequest({
      conversation: updatedConversation,
      execution_count: executionCount,
      ticket: ticket,
    });
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div>
      <h1>AIChatPage</h1>
      <div id="chat">
        {conversation.map((message, index) => (
          <div key={index} className={message[0]}>
            {<ReactMarkdown>{message[1]}</ReactMarkdown>}
          </div>
        ))}
        {isFetching && <p>Fetching...</p>}
        {error && <p>Error: {error.message}</p>}
      </div>
      <div>
        <button
          id="btn-reset"
          type="button"
          onClick={resetChat}
          disabled={isFetching}
        >
          Reset Chat
        </button>
        {ticketButton && (
          <button id="btn-ticket" type="button" onClick={handleTicketCreation}>
            Create Ticket
          </button>
        )}
      </div>

      <form onSubmit={handleSendMessage}>
        <label>Enter Question:</label>
        <input
          type="text"
          id="input"
          name="input"
          ref={inputRef}
          disabled={isFetching || ticketButton}
        />
        <button
          id="btn-submit"
          type="submit"
          disabled={isFetching || ticketButton}
        >
          Submit
        </button>
      </form>
      <p id="response"></p>
    </div>
  );
};

export default AIChatPage;
