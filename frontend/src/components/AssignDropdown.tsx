import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu";
import { Ticket } from "@/entities/Ticket";
import useAssignTicket from "@/hooks/useAssignTicket";
import useTechnicians from "@/hooks/useTechnicians";
import useAuthStore from "@/stores/AuthStore";
import { Button, MenuItemGroup } from "@chakra-ui/react";
import { Toaster, toaster } from "@/components/ui/toaster";
import { useEffect, useState } from "react";
interface AssignDropdownProps {
  ticket: Ticket;
}

export const AssignDropdown = ({ ticket }: AssignDropdownProps) => {
  const { accessToken } = useAuthStore();
  const { data: technicians, error: technicansError } =
    useTechnicians(accessToken);
  const { mutate: assignTicket, error: assignTicketError } = useAssignTicket();
  const [assigneeName, setAssigneeName] = useState(ticket.assignee_name);

  const handleClick = (assignee: string) => {
    const assigneeObj = technicians?.find(
      (technician) => technician.user_name == assignee
    );
    setAssigneeName(assignee);
    assignTicket({
      accessToken,
      ticketAssignee: {
        ticket_id: ticket.ticket_id,
        assignee_id: assigneeObj?.user_id || "Unassigned",
      },
    });
  };

  useEffect(() => {
    assignTicketError &&
      toaster.create({
        title: "Error",
        description: "Failed to assign Ticket. Please try again.",
      });
    setAssigneeName(ticket.assignee_name);
  }, [assignTicketError]);

  return (
    <MenuRoot>
      <Toaster />
      <MenuTrigger asChild h="1.3rem">
        <Button variant="outline" size="sm">
          {assigneeName || "Unassigned"}
        </Button>
      </MenuTrigger>
      <MenuContent>
        <MenuItemGroup>
          <MenuItem
            onClick={() => handleClick("Unassigned")}
            value="Unassigned"
          >
            {technicansError ? "Failed to load Technicians" : "Unassigned"}
          </MenuItem>
          {technicians?.map((technician) => (
            <MenuItem
              value={technician.user_name}
              onClick={() => handleClick(technician.user_name)}
              key={technician.user_id}
            >
              {technician.user_name}
            </MenuItem>
          ))}
        </MenuItemGroup>
      </MenuContent>
    </MenuRoot>
  );
};
