import { request } from "./request";

export const getMyUser = () => {
  return request.get("users/me");
};
