import { Box } from "@chakra-ui/react";
import { NavLink } from "react-router-dom";

interface StyledNavProps {
  link: string;
  name: string;
  bottomline?: boolean;
  sideline?: boolean;
  callBack?: (bool: boolean) => void;
}

const StyledNavLink = ({
  link,
  name,
  bottomline,
  sideline,
  callBack,
}: StyledNavProps) => {
  return (
    <Box position={"relative"}>
      <NavLink
        to={link}
        className={({ isActive }) => `link ${isActive ? "active" : ""}`}
        onClick={callBack ? () => callBack(false) : undefined}
      >
        {bottomline && (
          <Box
            display={"none"}
            className="link-effect"
            height={"0.2rem"}
            w={"100%"}
            backgroundColor={"blue"}
            position={"absolute"}
            bottom={"-1.22rem"}
          ></Box>
        )}
        {sideline && (
          <Box
            display={"none"}
            className="link-effect"
            w={"0.2rem"}
            h={"100%"}
            backgroundColor={"blue"}
            position={"absolute"}
            left={"-1.5rem"}
          ></Box>
        )}
        {name}
      </NavLink>
    </Box>
  );
};

export default StyledNavLink;
