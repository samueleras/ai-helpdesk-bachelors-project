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
interface AssignDropdownProps {
  ticket: Ticket;
}

export const AssignDropdown = ({ ticket }: AssignDropdownProps) => {
  const { accessToken } = useAuthStore();
  const { data: technicians, error } = useTechnicians(accessToken);
  const { mutate: assignTicket } = useAssignTicket();

  const handleClick = (assignee: string) => {
    const assigneeObj = technicians?.find(
      (technician) => technician.user_name == assignee
    );
    ticket.assignee_name = assignee;
    assignTicket({
      accessToken,
      ticketAssignee: {
        ticket_id: ticket.ticket_id,
        assignee_id: assigneeObj?.user_id || "Unassigned",
      },
    });
  };

  return (
    <MenuRoot>
      <MenuTrigger asChild h="1.3rem">
        <Button variant="outline" size="sm">
          {ticket.assignee_name || "Unassigned"}
        </Button>
      </MenuTrigger>
      <MenuContent>
        <MenuItemGroup>
          <MenuItem
            onClick={() => handleClick("Unassigned")}
            value="Unassigned"
          >
            {error ? "Failed to load Technicians" : "Unassigned"}
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
