import { Avatar, Box, Grid, GridItem, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";

interface ChatMessageProps {
  message_from_current_user: boolean;
  name: string;
  message: string;
  date?: string;
}

const ChatMessage = ({
  message_from_current_user,
  name,
  message,
  date,
}: ChatMessageProps) => {
  return (
    <Grid
      gridTemplateColumns={
        message_from_current_user ? "auto min-content" : "min-content auto"
      }
      gridTemplateAreas={
        message_from_current_user
          ? `"message avatar"` // If the message is from the current user
          : `"avatar message"` // If the message is from another user
      }
      justifyItems={message_from_current_user ? "end" : "start"}
      gap={2}
    >
      <GridItem area={"avatar"}>
        <Avatar.Root>
          <Avatar.Fallback name={name == "AI" ? "A I" : name} />
        </Avatar.Root>
      </GridItem>
      <GridItem area={"message"} width={"85%"}>
        <Box backgroundColor={"gray.300"} p={"2"} borderRadius={"1rem"}>
          <Text color="darkslateblue" fontWeight={"bold"}>
            {name}
          </Text>
          <ReactMarkdown>{message}</ReactMarkdown>
          {date && (
            <Text textAlign={"right"} fontSize={"xs"}>
              {date}
            </Text>
          )}
        </Box>
      </GridItem>
    </Grid>
  );
};

export default ChatMessage;
