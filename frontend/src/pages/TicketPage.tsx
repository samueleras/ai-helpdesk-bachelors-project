import ChatMessage from "@/components/ChatMessage";
import SimilarTicketDialog from "@/components/SimilarTicketDialog";
import TextDivider from "@/components/TextDivider";
import TicketDetails from "@/components/TicketDetails";
import { NewTicketMessage } from "@/entities/NewTicketMessage";
import { TicketMessage } from "@/entities/Ticket";
import useInsertTicketMessage from "@/hooks/useInsertTicketMessage";
import useTicket from "@/hooks/useTicket";
import { dateToString } from "@/services/dateToString";
import { Box, Button, Flex, Grid, Heading, Input } from "@chakra-ui/react";
import { FormEvent, useRef, useState } from "react";
import { IoSend } from "react-icons/io5";
import ReactMarkdown from "react-markdown";
import { useParams } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";

interface TicketPageProps {
  ticket_id?: string;
}

const TicketPage = ({ ticket_id }: TicketPageProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const { accessToken, user } = useAuthStore();
  const [_, setRerender] = useState(0);
  const params = useParams();
  if (!params.id) {
    throw new Error("ID is undefined");
  }
  const { data: ticket, error } = useTicket(
    ticket_id || params.id,
    accessToken
  );
  const forceRerender = () => {
    setRerender((prev) => prev + 1); // Changing state forces a re-render
  };
  const { mutate } = useInsertTicketMessage();

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    let inputValue = inputRef.current?.value;
    if (inputValue) {
      let now = new Date();
      let newTicketMessageDisplayFormat: TicketMessage = {
        message: inputValue,
        author_name: user.user_name,
        group: user.group,
        created_at: now,
      };
      /* optimistic update displays new message before it is stored in database to prevent delay */
      ticket?.ticket_messages.push(newTicketMessageDisplayFormat) &&
        forceRerender();
      /* insert into database by calling api via mutationQuery */
      let newTicketMessageInsertFormat: NewTicketMessage = {
        ticket_id: Number(params.id),
        message: inputValue,
        created_at: now,
      };
      if (params.id !== undefined) {
        mutate({
          newTicketMessage: newTicketMessageInsertFormat,
          accessToken: accessToken,
        });
      }
    }
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <Grid
      paddingBlock={"2rem"}
      paddingInline={{ base: "1rem", sm: "2rem" }}
      h={{ lg: `calc(100vh - 4rem)` }}
      gap={"2rem"}
      gridTemplateColumns={{ base: "1fr", lg: "50% 50%" }}
      maxWidth={{ base: "100%", lg: "calc(100% - 2rem)" }}
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
        {ticket && <TicketDetails ticket={ticket} />}
        <TextDivider />
        <Grid gap="1rem" wordBreak={"break-word"}>
          <ReactMarkdown>
            {ticket?.content.replace(/\\n/g, "\n").replace(/"/g, "")}
          </ReactMarkdown>
        </Grid>
        {ticket?.similar_tickets && !ticket_id && (
          <Box>
            <TextDivider />
            <Heading paddingBlock="1rem">{"Similar Tickets (Solved):"}</Heading>
            {ticket?.similar_tickets.map((ticket) => (
              <SimilarTicketDialog ticket={ticket} key={ticket.id} />
            ))}
          </Box>
        )}
      </Grid>
      {/* Chat Window incl Input*/}
      <Box
        width={"100%"}
        height={{ base: "85vh", lg: "100%" }}
        border="1px solid gray"
        backgroundColor={"gray.100"}
        borderRadius={".5rem"}
        position={"relative"}
        overflow="hidden"
      >
        {/* Chat Window */}
        <Flex
          overflowY="scroll"
          h={`calc(100% - 4rem)`}
          p="3"
          flexDirection={"column"}
        >
          {ticket?.ticket_messages.length === 0 &&
            user.group === "technicians" &&
            "A Technician will will handle this Ticket soon as possible."}
          {ticket?.ticket_messages.map((ticket_message, index) => (
            <ChatMessage
              name={ticket_message.author_name}
              message_from_current_user={
                ticket_message.author_name === user.user_name
              }
              date={dateToString(ticket_message.created_at)}
              message={ticket_message.message}
              key={index}
            />
          ))}
          {error && <p>Error: {error.message}</p>}
        </Flex>
        {/* Input Field */}
        <Box
          position={"absolute"}
          bottom={0}
          w="100%"
          backgroundColor={"gray.200"}
          p="0.5rem"
        >
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
                disabled={ticket?.closed_date != undefined}
              />
              <Button
                id="btn-submit"
                type="submit"
                height="3rem"
                backgroundColor={"blue"}
                disabled={ticket?.closed_date != undefined}
              >
                <IoSend />
              </Button>
            </Flex>
          </form>
        </Box>
      </Box>
    </Grid>
  );
};

export default TicketPage;
