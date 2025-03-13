import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu";
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

const TicketFilter = () => {
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
                Any
              </Button>
            </MenuTrigger>
          </Flex>
          <MenuContent>
            <MenuItemGroup>
              <MenuItem onClick={() => console.log("Any")} value="Any">
                Any
              </MenuItem>
              <MenuItem
                onClick={() => console.log("Technician")}
                value="Technician"
              >
                Technician
              </MenuItem>
            </MenuItemGroup>
          </MenuContent>
        </MenuRoot>
        <MenuRoot>
          <Flex alignItems={"center"}>
            <FaArrowDownWideShort />
            <Text paddingInline={".5rem"}>Order:</Text>
            <MenuTrigger asChild>
              <Button variant="outline" size="sm" h="1.3rem">
                Creation Date Asc
              </Button>
            </MenuTrigger>
          </Flex>
          <MenuContent>
            <MenuItemGroup>
              <MenuItem
                onClick={() => console.log("Creation Date ASC")}
                value="Creation Date ASC"
              >
                Creation Date ASC
              </MenuItem>
              <MenuItem
                onClick={() => console.log("Creation Date DESC")}
                value="Creation Date DESC"
              >
                Creation Date DESC
              </MenuItem>
            </MenuItemGroup>
          </MenuContent>
        </MenuRoot>
      </Flex>
      <Flex
        position={"relative"}
        alignItems={"center"}
        w={{ base: "100%", md: "15em" }}
      >
        <Box position={"absolute"} right=".5rem">
          <FaSearch />
        </Box>
        <Input placeholder={"Search for Ticket Title"} />
      </Flex>
    </Flex>
  );
};

export default TicketFilter;
