import ChatMessage from "@/components/ChatMessage";
import {
  Avatar,
  Box,
  Button,
  Flex,
  Input,
  Spinner,
  Text,
} from "@chakra-ui/react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { IoSend } from "react-icons/io5";
import { useNavigate } from "react-router-dom";
import { BeatLoader } from "react-spinners";
import useAIWorkflow from "../hooks/useAIWorkflow";
import useAuthStore from "../stores/AuthStore";
import useChatStore from "../stores/ChatStore";
import { Toaster, toaster } from "@/components/ui/toaster";

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
    error: aiWorkflowError,
    isFetching,
    refetch,
  } = useAIWorkflow(workflowRequest, accessToken);

  useEffect(() => {
    if (isFirstRender) {
      setIsFirstRender(false);
      return;
    }
    if (workflowResponse) {
      if (workflowResponse.ticket_id) {
        resetChat();
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
      refetch();
    }
  }, [workflowRequest]);

  useEffect(() => {
    if (aiWorkflowError) {
      conversation.pop();
      setConversation(conversation);
      toaster.create({
        title: "Error",
        type: "error",
        description: "The AI failed to respond. Please try again.",
      });
    }
  }, [aiWorkflowError]);

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
      p={{ base: "1rem", sm: "2rem" }}
      justifyContent="center"
      alignItems={"center"}
      flexDirection={"column"}
      gap="3"
    >
      <Toaster />
      {/* Chat Window */}
      <Box
        width={{ base: "100%", lg: "60vw" }}
        flex="1"
        overflow="auto"
        border="1px solid gray"
        backgroundColor={"gray.100"}
        borderRadius={".5rem"}
        position={"relative"}
      >
        <Flex
          overflowY="scroll"
          h={`calc(100% - 3.2rem)`}
          p="3"
          gap={3}
          flexDirection={"column"}
        >
          {conversation.length === 0 &&
            "Start a conversation by stating and describing your issue ..."}
          {conversation.map((message, index) => (
            <ChatMessage
              name={message[0] == "ai" ? "AI" : user.user_name ?? "User"}
              message_from_current_user={message[0] !== "ai"}
              message={message[1]}
              key={index}
            />
          ))}
          {/* Writing and Ticket Creation Animation */}
          {isFetching &&
            (ticket == true && executionCount == 1 ? (
              <Flex alignItems={"center"} gap={2}>
                <Avatar.Root>
                  <Avatar.Fallback name={"A I"} />
                </Avatar.Root>
                <Text>Generating ticket</Text>
                <Spinner />
                <Text>
                  This may take 1-2 minutes. Please stay on this page.
                </Text>
              </Flex>
            ) : (
              <Flex alignItems={"center"} gap={2}>
                <Avatar.Root>
                  <Avatar.Fallback name={"A I"} />
                </Avatar.Root>
                <BeatLoader size={8} color="gray" />
              </Flex>
            ))}
        </Flex>
        {/* Input Field */}
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
      {/* Buttons */}
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
