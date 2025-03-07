import { format } from "date-fns";

export const dateToString = (date?: Date) => {
  return date ? format(new Date(date), "MMMM do, yyyy h:mm a") : "N/A";
};
