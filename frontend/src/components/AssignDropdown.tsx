import { Button } from "@chakra-ui/react";
import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu";

export const AssignDropdown = () => {
  const handleSubmit = () => {};

  return (
    <MenuRoot>
      <MenuTrigger asChild h="1.3rem">
        <Button variant="outline" size="sm" onClick={handleSubmit}>
          Unassigned
        </Button>
      </MenuTrigger>
      <MenuContent>
        <MenuItem value="new-txt-a">Unassigned</MenuItem>
        <MenuItem value="new-file-a">Technician A</MenuItem>
        <MenuItem value="new-file-a">Technician B</MenuItem>
      </MenuContent>
    </MenuRoot>
  );
};
