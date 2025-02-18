import { useEffect } from "react";
import useAuthStore from "../stores/AuthStore";
import { useNavigate } from "react-router-dom";

const TechnicianPortalPage = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user || Object.keys(user).length === 0) return; //This case does not need to be handled here and might interfere on reload
    if (user?.group !== "technicians") {
      console.log("Access restricted!");
      navigate(-1); //return to previous page
    }
  }, [user]);

  return (
    <div>
      <h1>TechnicianPortalPage</h1>
      <p>content</p>
    </div>
  );
};

export default TechnicianPortalPage;
