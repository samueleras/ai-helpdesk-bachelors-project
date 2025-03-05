import { FormEvent, useEffect, useRef, useState } from "react";
import useAuthStore from "../stores/AuthStore";
import { useNavigate } from "react-router-dom";
import useAIWorkflow from "../hooks/useAIWorkflow";
import useChatStore from "../stores/ChatStore";
import ReactMarkdown from "react-markdown";
import { Box, Button, Flex, Input, Text } from "@chakra-ui/react";
import { IoSend } from "react-icons/io5";

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
        <Box overflowY="auto" h={`calc(80vh - 3.2rem)`} p="3">
          {conversation.map((message, index) => (
            <Box key={index} className={message[0]}>
              {<ReactMarkdown>{message[1]}</ReactMarkdown>}
            </Box>
          ))}
          {isFetching && <p>Fetching...</p>}
          {error && <p>Error: {error.message}</p>}
        </Box>
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
      <Box>
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
      {/* <Box id="chat">
        
      </Box> */}
    </Flex>
  );
};

export default AIChatPage;
