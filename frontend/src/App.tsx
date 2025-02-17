import { Outlet } from "react-router-dom";
import useAuthToken from "./hooks/useAuthToken";

const App = () => {
  useAuthToken();
  return <Outlet />;
};

export default App;
