import { Ticket } from "@/entities/Ticket";
import { dateToString } from "@/services/dateToString";
import {
  Badge,
  Button,
  Card,
  HStack,
  Image,
  VStack,
  Text,
  Flex,
} from "@chakra-ui/react";
import { FaUser } from "react-icons/fa";
import { FaHashtag } from "react-icons/fa";
import { MdDateRange } from "react-icons/md";
import ticketImage from "../assets/ticket_image.webp";
import { AssignDropdown } from "./AssignDropdown";
import { FaTools } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { IoLockClosed } from "react-icons/io5";

interface TicketListItemProps {
  ticket: Ticket;
}

export const TicketListItem = ({ ticket }: TicketListItemProps) => {
  const navigate = useNavigate();

  const handleCloseTicket = () => {
    //handle close ticket
  };

  return (
    <Card.Root
      flexDirection="row"
      overflow="hidden"
      border="1px solid darkgray"
    >
      <Image
        display={{ base: "none", md: "block" }}
        objectFit="cover"
        maxW="35%"
        maxH={{ base: "450px", md: "350px" }}
        src={ticketImage}
        alt="Ticket Dummy Image"
        onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
        cursor={"pointer"}
      />
      <Flex>
        <Card.Body>
          <Card.Title
            mb="2"
            onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
            cursor={"pointer"}
          >
            {ticket.title.replace(/"/g, "")}
          </Card.Title>
          <Card.Description
            onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
            cursor={"pointer"}
          >
            {ticket.content
              .substring(0, ticket.content.indexOf(".") + 1)
              .replace(/"/g, "")}
          </Card.Description>
          <VStack mt="4" alignItems={"start"} fontSize={"sm"} gap="3">
            <HStack>
              <FaUser />
              <Text>Author:</Text>
              <Badge>{ticket.author_name}</Badge>
            </HStack>
            <HStack>
              <FaHashtag />
              <Text>Ticket ID:</Text>
              <Badge>{ticket.ticket_id}</Badge>
            </HStack>
            <HStack>
              <MdDateRange />
              <Text>Creation Date:</Text>
              <Badge>{dateToString(ticket.creation_date)}</Badge>
            </HStack>
            <HStack>
              <FaTools />
              <Text>Assignee:</Text>
              <AssignDropdown />
            </HStack>
            <HStack>
              <IoLockClosed />
              <Text>Closed:</Text>
              <Badge>
                {ticket.closed_date ? dateToString(ticket.closed_date) : "No"}
              </Badge>
              {!ticket.closed_date && (
                <Button onClick={handleCloseTicket} h="1.3rem">
                  Close Ticket
                </Button>
              )}
            </HStack>
          </VStack>
        </Card.Body>
      </Flex>
    </Card.Root>
  );
};
