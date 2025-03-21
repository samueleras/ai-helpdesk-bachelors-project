import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu";
import useTechnicians from "@/hooks/useTechnicians";
import useAuthStore from "@/stores/AuthStore";
import useFilterStore from "@/stores/FilterStore";
import {
  Box,
  Button,
  Flex,
  Input,
  MenuItemGroup,
  Text,
} from "@chakra-ui/react";
import { FaSearch, FaTools } from "react-icons/fa";
import { FaArrowDownWideShort } from "react-icons/fa6";
import { IoLockClosed } from "react-icons/io5";

const TicketFilter = () => {
  const { ticketFilter, updateTicketFilter } = useFilterStore();
  const { accessToken } = useAuthStore();
  const { data: technicians } = useTechnicians(accessToken);

  return (
    <Flex
      mb={{ base: "1rem", sm: "2rem" }}
      backgroundColor={"white"}
      alignItems={"left"}
      paddingInline={"1rem"}
      paddingBlock=".5rem"
      gap="1rem"
      borderRadius={".4rem"}
      border={"1px solid darkgray"}
      flexWrap={"wrap"}
      justifyContent={"space-between"}
      flexDirection={{ base: "column", sm: "row" }}
    >
      <Flex flexWrap={"wrap"} gap="1rem">
        <MenuRoot>
          <Flex alignItems={"center"}>
            <FaTools />
            <Text paddingInline={".5rem"}>Assignee:</Text>
            <MenuTrigger asChild>
              <Button variant="outline" size="sm" h="1.3rem" mr="1rem">
                {!ticketFilter.assignee_id
                  ? "Any"
                  : ticketFilter.assignee_id == "unassigned"
                  ? "Unassigned"
                  : technicians?.find(
                      (technician) =>
                        technician.user_id === ticketFilter.assignee_id
                    )?.user_name}
              </Button>
            </MenuTrigger>
          </Flex>
          <MenuContent>
            <MenuItemGroup>
              <MenuItem
                onClick={() => {
                  const { assignee_id, ...updatedFilter } = ticketFilter;
                  updateTicketFilter(updatedFilter);
                }}
                value="any"
              >
                Any
              </MenuItem>
              <MenuItem
                onClick={() =>
                  updateTicketFilter({
                    ...ticketFilter,
                    assignee_id: "unassigned",
                  })
                }
                value="unassigned"
              >
                Unassigned
              </MenuItem>
              {technicians?.map((technician) => (
                <MenuItem
                  onClick={() =>
                    updateTicketFilter({
                      ...ticketFilter,
                      assignee_id: technician.user_id,
                    })
                  }
                  value={technician.user_name}
                  key={technician.user_id}
                >
                  {technician.user_name}
                </MenuItem>
              ))}
            </MenuItemGroup>
          </MenuContent>
        </MenuRoot>
        <MenuRoot>
          <Flex alignItems={"center"}>
            <FaArrowDownWideShort />
            <Text paddingInline={".5rem"}>Order:</Text>
            <MenuTrigger asChild>
              <Button variant="outline" size="sm" h="1.3rem" mr="1rem">
                {ticketFilter.order == "asc"
                  ? "Creation Date ASC"
                  : "Creation Date DESC"}
              </Button>
            </MenuTrigger>
          </Flex>
          <MenuContent>
            <MenuItemGroup>
              <MenuItem
                onClick={() => {
                  const { order, ...updatedFilter } = ticketFilter;
                  updateTicketFilter(updatedFilter);
                }}
                value="desc"
              >
                Creation Date DESC
              </MenuItem>
              <MenuItem
                onClick={() =>
                  updateTicketFilter({ ...ticketFilter, order: "asc" })
                }
                value="asc"
              >
                Creation Date ASC
              </MenuItem>
            </MenuItemGroup>
          </MenuContent>
        </MenuRoot>
        <MenuRoot>
          <Flex alignItems={"center"}>
            <IoLockClosed />
            <Text paddingInline={".5rem"}>Status:</Text>
            <MenuTrigger asChild>
              <Button variant="outline" size="sm" h="1.3rem">
                {ticketFilter.closed == true
                  ? "Closed"
                  : ticketFilter.closed == false
                  ? "Opened"
                  : "All"}
              </Button>
            </MenuTrigger>
          </Flex>
          <MenuContent>
            <MenuItemGroup>
              <MenuItem
                onClick={() => {
                  const { closed, ...updatedFilter } = ticketFilter;
                  updateTicketFilter(updatedFilter);
                }}
                value="all"
              >
                All
              </MenuItem>
              <MenuItem
                onClick={() =>
                  updateTicketFilter({ ...ticketFilter, closed: false })
                }
                value="opened"
              >
                Opened
              </MenuItem>
              <MenuItem
                onClick={() =>
                  updateTicketFilter({ ...ticketFilter, closed: true })
                }
                value="closed"
              >
                Closed
              </MenuItem>
            </MenuItemGroup>
          </MenuContent>
        </MenuRoot>
      </Flex>
      <Flex
        position={"relative"}
        alignItems={"center"}
        w={{ base: "100%", lg: "15em" }}
      >
        <Box position={"absolute"} right=".5rem">
          <FaSearch />
        </Box>
        <Input
          placeholder={"Search for Ticket Title"}
          value={ticketFilter.search ?? ""}
          onChange={(e) => {
            if (e.target.value == "") {
              const { search, ...updatedFilter } = ticketFilter;
              updateTicketFilter(updatedFilter);
            } else {
              updateTicketFilter({ ...ticketFilter, search: e.target.value });
            }
          }}
        />
      </Flex>
    </Flex>
  );
};

export default TicketFilter;
