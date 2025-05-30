import styles from "./GroupList.module.scss";
import backIcon from "../../static/icons/back.svg";
import { Unit } from "../Unit/Unit";
import { useState, useEffect } from "react";
import { useCookies } from "react-cookie";
import { Link } from "react-router-dom";
import { Group } from "../../types/Group";
import { Pupil } from "../../types/Pupil";

export interface IGroupListProps {
  groupId: string;
}

export function GroupList(props: IGroupListProps) {
  const [units, setUnits] = useState<Pupil[]>([]);
  const [freeUnits, setFreeUnits] = useState<Pupil[]>([]);
  const [groupInfo, setGroupInfo] = useState<Group>();

  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils`, {
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
      },
    })
      .then((res) => res.json())
      .then((allUnits: Pupil[]) => {
        fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
          headers: {
            Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
          },
        })
          .then((res) => res.json())
          .then((groups: Group[]) => {
            const groupInfo = groups.find(
              (group) => group.id === props.groupId
            );
            if (groupInfo) {
              setGroupInfo(groupInfo);
              setUnits(groupInfo.pupils);
              setFreeUnits(allUnits.filter(unit => !groupInfo.pupils.map(pupil => pupil.id).includes(unit.id)));
            }
          })
          .catch((err) => console.log(err));
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className={styles.card}>
      <header className={styles.header}>
        <Link to="/my/groups">
          <img src={backIcon} alt="" className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>{groupInfo?.name || ""}</div>
        {
          freeUnits.length > 0
          ?
          <div className={styles.add__unit}>

          </div>
          :
          ''
        }
      </header>
      <div className={styles.units}>
        <header className={styles.units__header}>
          <div className={styles.header__column}>Имя / никнейм</div>
          <div className={styles.header__column}>Действия</div>
        </header>
        <section className={styles.units__list}>
          {units.map((unit, index) => (
            <Unit key={index} unit={unit} groupId={props.groupId} />
          ))}
        </section>
      </div>
    </div>
  );
}
