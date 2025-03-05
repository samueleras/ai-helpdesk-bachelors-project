import ChatMessage from "@/components/ChatMessage";
import { Box, Button, Flex, Input, Spinner } from "@chakra-ui/react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { IoSend } from "react-icons/io5";
import { useNavigate } from "react-router-dom";
import useAIWorkflow from "../hooks/useAIWorkflow";
import useAuthStore from "../stores/AuthStore";
import useChatStore from "../stores/ChatStore";

const AIChatPage = () => {
  const inputRef = useRef<HTMLInputElement>(null);
  const { accessToken, user } = useAuthStore();
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
    <Flex
      backgroundColor="darkslategray"
      h={`calc(100vh - 4rem)`}
      justifyContent="center"
      alignItems={"center"}
      flexDirection={"column"}
      gap="3"
    >
      <Box
        width={{ base: "100vw", sm: "80vw" }}
        height="80vh"
        border="1px solid gray"
        backgroundColor={"gray.100"}
        borderRadius={".5rem"}
        position={"relative"}
      >
        <Flex
          overflowY="auto"
          h={`calc(80vh - 3.2rem)`}
          p="3"
          gap={3}
          flexDirection={"column"}
        >
          {conversation.map((message, index) => (
            <ChatMessage
              name={message[0] == "ai" ? "AI" : user.user_name ?? "User"}
              message_from_current_user={message[0] !== "ai"}
              message={message[1]}
              key={index}
            />
          ))}
          {isFetching && <Spinner />}
          {error && <p>Error: {error.message}</p>}
        </Flex>
        <Box position={"absolute"} bottom={0} w="100%">
          <form onSubmit={handleSendMessage}>
            <Flex gap={1}>
              <Input
                type="text"
                id="input"
                name="input"
                ref={inputRef}
                disabled={isFetching || ticketButton}
                backgroundColor={"gray.100"}
                placeholder="Prompt your issue ..."
                height="3rem"
              />
              <Button
                id="btn-submit"
                type="submit"
                disabled={isFetching || ticketButton}
                height="3rem"
                backgroundColor={"blue"}
              >
                <IoSend />
              </Button>
            </Flex>
          </form>
        </Box>
      </Box>
      <Box spaceX={2}>
        <Button
          id="btn-reset"
          type="button"
          onClick={resetChat}
          disabled={isFetching}
        >
          Reset Chat
        </Button>
        {ticketButton && (
          <Button id="btn-ticket" type="button" onClick={handleTicketCreation}>
            Create Ticket
          </Button>
        )}
      </Box>
    </Flex>
  );
};

export default AIChatPage;
