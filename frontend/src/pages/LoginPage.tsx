import { useMsal } from "@azure/msal-react";
import { Avatar, Button, Card, Flex, Heading } from "@chakra-ui/react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useUsersMe from "../hooks/useUserMe";
import useAuthStore from "../stores/AuthStore";

const LoginPage = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const { user, login } = useAuthStore();

  useEffect(() => {
    if (user && Object.keys(user).length > 0) {
      console.log("Logged in successfully!");
      console.log("User ", user);
      if (user.group === "users") navigate("/my-tickets");
      if (user.group === "technicians") navigate("/technician-portal");
    }
  }, [user]);

  const handleLogin = async () => {
    try {
      instance.clearCache();
      const response = await instance.loginPopup();
      instance.setActiveAccount(response.account);
      const accessToken = response.accessToken;
      const fetchedUser = await useUsersMe(accessToken);
      login(fetchedUser, accessToken);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      backgroundColor={"darkslategray"}
      bgSize="cover"
      bgRepeat="no-repeat"
    >
      <Heading
        color="white"
        fontSize={{ base: "4rem", lg: "6rem" }}
        position="fixed"
        top="7rem"
        left="50%"
        transform="translateX(-50%)"
        whiteSpace={"nowrap"}
      >
        AI Helpdesk
      </Heading>
      <Card.Root width="320px">
        <Card.Body gap="2">
          <Avatar.Root colorPalette="blue">
            <Avatar.Fallback />
          </Avatar.Root>
          <Card.Title mt="2">Login</Card.Title>
          <Card.Description>
            Sign in with your company account to securely authenticate via
            Microsoft Azure.
          </Card.Description>
        </Card.Body>
        <Card.Footer justifyContent="flex-end">
          <Button onClick={handleLogin}>Login</Button>
        </Card.Footer>
      </Card.Root>
    </Flex>
  );
};

export default LoginPage;
