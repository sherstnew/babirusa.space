import { Pupil } from "./Pupil";

export interface Teacher {
  id: string;
  login: string;
  hashed_password: string;
  pupils: Pupil[];
}
