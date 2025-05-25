import { Pupil } from "./Pupil";
import { Teacher } from "./Teacher";

export interface Group {
  id: string;
  name: string;
  teacher: Teacher;
  pupils: Pupil[];
}
