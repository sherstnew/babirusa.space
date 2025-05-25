import styles from "./AddUnit.module.scss";
import backIcon from "../../static/icons/back.svg";
import { useCookies } from "react-cookie";
import { useContext, useEffect, useState } from "react";
import { NotificationsContext } from "../../contexts/NotificationsContext";
import { v4 } from "uuid";
import { Link } from "react-router-dom";
import { Pupil } from "../../types/Pupil";
import { Group } from '../../types/Group';

export function AddUnit() {
  const { notifications, setNotifications } = useContext(NotificationsContext);
  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);

  const [unitFName, setUnitFName] = useState("");
  const [unitLName, setUnitLName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [groupId, setGroupId] = useState("");

  const [groups, setGroups] = useState<Group[]>([]);

  const createUnit = (event: any) => {
    event.preventDefault();
    if (unitFName !== "" && unitLName !== "" && groupId !== "" && username !== "" && password !== "") {
      fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils/new`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstname: unitFName,
          lastname: unitLName,
          username: username,
          password: password,
        }),
      })
        .then((res) => {
          if (res.status === 200) {
            return res.json();
          } else {
            setNotifications([
              ...notifications,
              {
                id: v4(),
                text: "Не удалось создать ученика",
                time: 5000,
              },
            ]);
            throw new Error(`Status: ${res.status}`);
          }
        })
        .then((pupil: Pupil) => {
          fetch(
            `${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups/pupils`,
            {
              method: "POST",
              headers: {
                Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                group_id: groupId,
                pupil_id: [pupil.id],
              }),
            }
          )
            .then((res) => {
              if (!res.ok) throw new Error(`Status: ${res.status}`);
              return res.json();
            })
            .then(() => {
              window.location.href = "/my/groups";
            });
        })
        .catch((err) => {
          console.log(err);

          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: "Неизвестная ошибка",
              time: 5000,
            },
          ]);
        });
    } else {
      setNotifications([
        ...notifications,
        {
          id: v4(),
          text: "Введите все необходимые данные",
          time: 5000,
        },
      ]);
    }
  };

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
      },
    })
      .then((res) => res.json())
      .then((data: Group[]) => {
        setGroups(data);
        setGroupId(data.length > 0 ? data[0].id : "");
      })
      .catch((err) => {
        console.log(err);

        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: "Неизвестная ошибка",
            time: 5000,
          },
        ]);
      });
  }, []);

  return (
    <div className={styles.add}>
      <header className={styles.header}>
        <Link to="/my/groups">
          <img src={backIcon} alt="" className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>Добавить ученика</div>
      </header>
      <form className={styles.form}>
        <input
          type="text"
          className={styles.input}
          placeholder="Введите имя ученика"
          value={unitFName}
          onChange={(event) => setUnitFName(event.target.value)}
        />
        <input
          type="text"
          className={styles.input}
          placeholder="Введите фамилию ученика"
          value={unitLName}
          onChange={(event) => setUnitLName(event.target.value)}
        />
        <input
          type="text"
          className={styles.input}
          placeholder="Введите никнейм"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
        <input
          type="text"
          className={styles.input}
          placeholder="Введите пароль"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <select
          className={styles.input + " " + styles.groupSelect}
          defaultValue={groups[0] ? groups[0].id : ""}
          onChange={(event) => setGroupId(event.target.value)}
        >
          {groups.map((group) => (
            <option
              key={group.id}
              value={group.id}
              className={styles.option}
            >
              {group.name}
            </option>
          ))}
        </select>
        <button className={styles.button} onClick={createUnit}>
          Создать ученика
        </button>
      </form>
    </div>
  );
}
