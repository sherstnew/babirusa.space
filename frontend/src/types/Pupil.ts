import { Group } from "./Group";

export interface Pupil {
  id: string;
  username: string;
  firstname: string;
  lastname: string;
  groups: Group[];
}
