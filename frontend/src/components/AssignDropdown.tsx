import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu";
import { Ticket } from "@/entities/Ticket";
import useTechnicians from "@/hooks/useTechnicians";
import useAuthStore from "@/stores/AuthStore";
import { Button, MenuItemGroup } from "@chakra-ui/react";
import { useEffect, useState } from "react";

interface AssignDropdownProps {
  ticket: Ticket;
}

export const AssignDropdown = ({ ticket }: AssignDropdownProps) => {
  const { accessToken } = useAuthStore();
  const { data: technicians, error } = useTechnicians(accessToken);
  const [assignee, setAssignee] = useState(
    ticket.assignee_name || "Unassigned"
  );

  useEffect(() => {
    console.log("change assignee", assignee);
  }, [assignee]);

  return (
    <MenuRoot>
      <MenuTrigger asChild h="1.3rem">
        <Button variant="outline" size="sm">
          {assignee}
        </Button>
      </MenuTrigger>
      <MenuContent>
        <MenuItemGroup>
          <MenuItem
            onClick={() => setAssignee("Unassigned")}
            value="Unassigned"
          >
            {error ? "Failed to load Technicians" : "Unassigned"}
          </MenuItem>
          {technicians?.map((technician) => (
            <MenuItem
              value={technician.user_name}
              onClick={() => setAssignee(technician.user_name)}
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
