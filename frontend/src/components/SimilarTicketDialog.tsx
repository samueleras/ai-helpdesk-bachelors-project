import { SimilarTicket } from "@/entities/Ticket";
import TicketPage from "@/pages/TicketPage";
import { Text, CloseButton, Dialog, Portal } from "@chakra-ui/react";

interface SimilarTicketsContainerProps {
  ticket: SimilarTicket;
}

const SimilarTicketDialog = ({ ticket }: SimilarTicketsContainerProps) => {
  return (
    <Dialog.Root placement={"center"} size="full" scrollBehavior="inside">
      <Dialog.Trigger asChild>
        <Text
          borderRadius=".3rem"
          border="1px solid darkgray"
          mb="1rem"
          p=".5rem"
          cursor="pointer"
        >
          {ticket.entity.title}
        </Text>
      </Dialog.Trigger>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.CloseTrigger asChild>
              <CloseButton position={"fixed"} top={2} right={2} />
            </Dialog.CloseTrigger>
            <Dialog.Body mt="1.5rem">
              <TicketPage ticket_id={ticket.id.toString()} />
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

export default SimilarTicketDialog;
