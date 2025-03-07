import ChatMessage from "@/components/ChatMessage";
import {
  Box,
  Button,
  Flex,
  Grid,
  Heading,
  Input,
  Text,
} from "@chakra-ui/react";
import { FormEvent, useRef } from "react";
import { IoSend } from "react-icons/io5";
import { useParams } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import useTicket from "@/hooks/useTicket";
import ReactMarkdown from "react-markdown";
import { format } from "date-fns";
import TextDivider from "@/components/TextDivider";

const TicketPage = () => {
  const inputRef = useRef<HTMLInputElement>(null);
  const { accessToken, user } = useAuthStore();

  const params = useParams();
  if (!params.id) {
    throw new Error("ID is undefined");
  }

  const { data: ticket, error } = useTicket(params.id, accessToken);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    let inputValue = inputRef.current?.value;
    console.log(inputValue);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <Grid
      p={"2rem"}
      h={{ lg: `calc(100vh - 4rem)` }}
      gap={"2rem"}
      gridTemplateColumns={{ base: "1fr", lg: "50% 50%" }}
      maxWidth="calc(100% - 2rem)"
    >
      <Grid
        backgroundColor={"white"}
        overflow={{ base: "none", lg: "auto" }}
        p="2rem"
        gap="1rem"
        border="1px solid gray"
        borderRadius={".5rem"}
      >
        <Heading>
          <ReactMarkdown>
            {ticket?.title.replace(/\\n/g, "\n").replace(/"/g, "")}
          </ReactMarkdown>
        </Heading>
        <TextDivider />
        <Box>
          <Text>User: {ticket?.author_name}</Text>
          <Text>Ticket ID: {ticket?.ticket_id}</Text>
          <Text>
            Creation Date:
            {ticket?.creation_date
              ? format(new Date(ticket.creation_date), "MMMM do, yyyy h:mm a")
              : "N/A"}
          </Text>
        </Box>
        <TextDivider />
        <Grid gap="1rem">
          <ReactMarkdown>
            {ticket?.content.replace(/\\n/g, "\n").replace(/"/g, "")}
          </ReactMarkdown>
        </Grid>
        <Button mt="1rem">Show Similar Tickets</Button>
      </Grid>
      <Flex
        justifyContent="center"
        alignItems={"center"}
        flexDirection={"column"}
        gap="3"
        width={"100%"}
        height={"100%"}
      >
        {/* Chat Window */}
        <Box
          width={"100%"}
          height={"100%"}
          minHeight={"85vh"}
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
            {ticket?.ticket_messages.map((ticket_message, index) => (
              <ChatMessage
                name={ticket_message.author_name}
                message_from_current_user={
                  ticket_message.author_name === user.user_name
                }
                message={ticket_message.message}
                key={index}
              />
            ))}
            {error && <p>Error: {error.message}</p>}
          </Flex>
          {/* Input Field */}
          <Box position={"absolute"} bottom={0} w="100%">
            <form onSubmit={handleSubmit}>
              <Flex gap={1}>
                <Input
                  type="text"
                  id="input"
                  name="input"
                  ref={inputRef}
                  backgroundColor={"gray.100"}
                  placeholder={
                    user.group == "technicians"
                      ? "Ask for Details or propose a Solution ..."
                      : "Provide more Ticket details ..."
                  }
                  height="3rem"
                />
                <Button
                  id="btn-submit"
                  type="submit"
                  height="3rem"
                  backgroundColor={"blue"}
                >
                  <IoSend />
                </Button>
              </Flex>
            </form>
          </Box>
        </Box>
      </Flex>
    </Grid>
  );
};

export default TicketPage;
