import styles from "./Unit.module.scss";
import { useCookies } from "react-cookie";
import { useContext, useState } from "react";
import { NotificationsContext } from "../../contexts/NotificationsContext";
import { v4 } from "uuid";
import { Link, useNavigate } from "react-router-dom";

export interface IUnitProps {
  name: string;
  unitId: string;
  username: string;
}

export function Unit(props: IUnitProps) {
  const navigate = useNavigate();

  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);
  const { notifications, setNotifications } = useContext(NotificationsContext);

  const [password, setPassword] = useState<string>("");

  const deleteUnit = (unitId: string) => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils/${unitId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
      },
    })
      .then((res) => {
        if (res.status === 200) {
          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: "Ученик успешно удален",
              time: 5000,
            },
          ]);
        } else {
          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: "Ошибка удаления ученика",
              time: 5000,
            },
          ]);
        }
        navigate(0);
      })
      .catch((err) => {
        console.log(err);

        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: "Ошибка удаления ученика",
            time: 5000,
          },
        ]);
      });
  };

  function getPassword() {
    fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils/${
        props.unitId
      }/password`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
        },
      }
    )
      .then((res) => {
        if (!res.ok) throw new Error("Password problem");
        return res.json();
      })
      .then((data) => {
        setPassword(data.password);
      })
      .catch((err) => {
        console.log(err);

        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: "Ошибка получения пароля",
            time: 5000,
          },
        ]);
      });
  }
  return (
    <div className={styles.unit}>
      <div className={styles.unit__name}>
        {props.username + " / " + props.name}
      </div>
      <div className={styles.unit__actions}>
        <div
          className={styles.action}
          onClick={() => (password ? setPassword("") : getPassword())}
        >
          {password ? password : "пароль"}
        </div>
        <Link
          to={`https://${props.username}.babirusa.space`}
          target="_blank"
          className={styles.action}
        >
          открыть пространство
        </Link>
        <div className={styles.action} onClick={() => deleteUnit(props.unitId)}>
          удалить
        </div>
      </div>
    </div>
  );
}
