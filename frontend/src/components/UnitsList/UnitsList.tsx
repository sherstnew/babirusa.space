import styles from "./UnitsList.module.scss";
import backIcon from "../../static/icons/back.svg";
import { Unit } from "../Unit/Unit";
import { useState, useEffect } from "react";
import { useCookies } from "react-cookie";
import { Link } from "react-router-dom";
import { Pupil } from "../../types/Pupil";
import { Group } from "../../types/Group";

export function UnitsList() {
  const [units, setUnits] = useState<Pupil[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);

  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils`, {
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
      },
    })
      .then((res) => res.json())
      .then((units: Pupil[]) => {
        setUnits(units);
      })
      .catch((err) => console.log(err));
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
      },
    })
      .then((res) => res.json())
      .then((data: any) => {
        setGroups(data);
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className={styles.card}>
      <header className={styles.header}>
        <Link to="/my/groups">
          <img src={backIcon} alt="" className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>Ученики</div>
      </header>
      <div className={styles.units}>
        <header className={styles.units__header}>
          <div className={styles.header__column}>Имя / никнейм</div>
          <div className={styles.header__column}>Действия</div>
        </header>
        <section className={styles.units__list}>
          {groups && units ? units.map((unit, index) => (
            <Unit key={index} unit={unit} groups={groups} />
          )) : ''}
        </section>
      </div>
    </div>
  );
}
