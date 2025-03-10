import {
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { useMsal } from "@azure/msal-react";
import { Box, Button, Flex, VStack } from "@chakra-ui/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import StyledNavLink from "./StyledNavLink";
import { TbLogout } from "react-icons/tb";
import { GiHamburgerMenu } from "react-icons/gi";

export function Navbar() {
  const { instance } = useMsal();
  const { logout } = useAuthStore();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const azurelogout = () => {
    instance.clearCache();
    logout();
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
      backgroundColor={"white"}
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

        {/* Mobile Navbar */}
        <DrawerRoot open={open} onOpenChange={(e) => setOpen(e.open)}>
          <DrawerBackdrop />
          <DrawerTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              display={{ base: "flex", md: "none" }}
            >
              <GiHamburgerMenu />
            </Button>
          </DrawerTrigger>
          <DrawerContent>
            <DrawerCloseTrigger />
            <DrawerBody>
              <Flex
                justifyContent={"space-between"}
                h={"100%"}
                paddingTop={10}
                paddingBottom={5}
                flexDirection={"column"}
              >
                <VStack gap="5" alignItems={"start"}>
                  <StyledNavLink
                    link="/ai-chat"
                    name="AI Chat"
                    sideline={true}
                    callBack={setOpen}
                  />
                  <StyledNavLink
                    link="/technician-portal"
                    name="Technician Portal"
                    sideline={true}
                    callBack={setOpen}
                  />
                  <StyledNavLink
                    link="/my-tickets"
                    name="My Tickets"
                    sideline={true}
                    callBack={setOpen}
                  />
                </VStack>
                <Button
                  onClick={() => {
                    azurelogout();
                    setOpen(false);
                    navigate("/");
                  }}
                >
                  <TbLogout />
                  Logout
                </Button>
              </Flex>
            </DrawerBody>
          </DrawerContent>
        </DrawerRoot>
      </Flex>
    </Flex>
  );
}
