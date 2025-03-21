import { useMsal } from "@azure/msal-react";
import { Avatar, Button, Card, Flex, Heading, Text } from "@chakra-ui/react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useUsersMe from "../hooks/useUserMe";
import useAuthStore from "../stores/AuthStore";

const LoginPage = () => {
  const { instance } = useMsal();
  const navigate = useNavigate();
  const { accessToken, user, setUser, setAccessToken } = useAuthStore();
  const {
    data: fetchedUser,
    error: userMeError,
    refetch,
    isFetching,
  } = useUsersMe(accessToken);

  useEffect(() => {
    fetchedUser && accessToken && setUser(fetchedUser);
  }, [fetchedUser, accessToken]);

  useEffect(() => {
    if (user.group === "users") navigate("/my-tickets");
    if (user.group === "technicians") navigate("/technician-portal");
  }, [user]);

  const handleLogin = async () => {
    try {
      instance.clearCache();
      const response = await instance.loginPopup();
      instance.setActiveAccount(response.account);
      setAccessToken(response.accessToken);
      refetch();
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <Flex
      minH="100vh"
      h="100vh"
      align="center"
      paddingTop="10vh"
      backgroundColor={"darkslategray"}
      bgSize="cover"
      bgRepeat="no-repeat"
      flexDirection="column"
    >
      <Heading
        color="white"
        fontSize={{ base: "4rem", lg: "6rem" }}
        whiteSpace={"nowrap"}
        lineHeight="1"
        marginBottom="calc(30vh - 7rem)"
      >
        AI Helpdesk
      </Heading>
      <Card.Root width="320px" justifySelf="center">
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
        <Card.Footer flexDirection={"column"}>
          <Button marginLeft={"auto"} onClick={handleLogin}>
            Login
          </Button>
          {userMeError && (
            <Text color="red">
              Login is currently not available. Try again later.
            </Text>
          )}
          {!isFetching && !userMeError && accessToken && !user.group && (
            <Text color="red">No permission to access this Application.</Text>
          )}
        </Card.Footer>
      </Card.Root>
    </Flex>
  );
};

export default LoginPage;
