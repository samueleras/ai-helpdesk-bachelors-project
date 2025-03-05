import { useMsal } from "@azure/msal-react";
import { Box, Button, Flex } from "@chakra-ui/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import StyledNavLink from "./StyledNavLink";
import { TbLogout } from "react-icons/tb";

export function Navbar() {
  const { instance } = useMsal();
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  const azurelogout = () => {
    instance.clearCache();
    logout();
    console.log("Logged out.");
  };

  return (
    <Flex
      px={6}
      py={4}
      boxShadow="md"
      position="sticky"
      top={0}
      zIndex={1000}
      h={"4rem"}
    >
      <Flex
        justify="space-between"
        align="center"
        alignContent={"center"}
        w={"100vw"}
      >
        <Box style={{ fontWeight: "bold", fontSize: "1.2rem" }}>
          AI Helpdesk
        </Box>

        {/* Desktop Navbar */}
        <Flex display={{ base: "none", md: "flex" }} gap={6}>
          <StyledNavLink link="/ai-chat" name="AI Chat" bottomline={true} />
          <StyledNavLink
            link="/technician-portal"
            name="Technician Portal"
            bottomline={true}
          />
          <StyledNavLink
            link="/my-tickets"
            name="My Tickets"
            bottomline={true}
          />
        </Flex>

        <Button
          display={{ base: "none", md: "flex" }}
          onClick={() => {
            azurelogout();
            navigate("/");
          }}
        >
          Logout
          <TbLogout />
        </Button>
      </Flex>
    </Flex>
  );
}
