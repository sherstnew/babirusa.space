import styles from "./Unit.module.scss";
import { useCookies } from "react-cookie";
import { useContext, useState } from "react";
import { NotificationsContext } from "../../contexts/NotificationsContext";
import { v4 } from "uuid";
import { Link, useNavigate } from "react-router-dom";
import { Pupil } from "../../types/Pupil";
import { Group } from "../../types/Group";

export interface IUnitProps {
  unit: Pupil;
  groupId?: string;
  groups?: Group[];
}

export function Unit({ unit, groupId, groups }: IUnitProps) {
  const navigate = useNavigate();

  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);
  const { notifications, setNotifications } = useContext(NotificationsContext);

  const [password, setPassword] = useState<string>("");

  const deleteUnitFromGroup = (unitId: string) => {
    fetch(
      `${
        import.meta.env.VITE_BACKEND_URL
      }/api/teacher/groups/pupils?group_id=${groupId}&pupil_id=${unitId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
        },
      }
    )
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
        unit.id
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

  function moveUnit(unitId: string, classId: string) {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/gropus/pupils`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        group_id: classId,
        pupil_id: [unitId],
      }),
    })
      .then((res) => {
        if (res.status === 200) {
          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: "Ученик успешно перемещен",
              time: 5000,
            },
          ]);
        } else {
          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: "Ошибка перемещения ученика",
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
            text: "Ошибка перемещения ученика",
            time: 5000,
          },
        ]);
      });
  }

  return (
    <div className={styles.unit}>
      <div className={styles.unit__name}>
        {unit.firstname + " " + unit.lastname + " / " + unit.username}
      </div>
      <div className={styles.unit__actions}>
        <div
          className={styles.action}
          onClick={() => (password ? setPassword("") : getPassword())}
        >
          {password ? password : "Пароль"}
        </div>
        <Link
          to={`https://${unit.username}.babirusa.space`}
          target="_blank"
          className={styles.action}
        >
          Пространство
        </Link>
        {groupId ? (
          <div
            className={styles.action}
            onClick={() => deleteUnitFromGroup(unit.id)}
          >
            Удалить из группы
          </div>
        ) : (
          <>
            <div className={styles.action} onClick={() => deleteUnit(unit.id)}>
              Удалить
            </div>
            {groups ? (
              <select
                className={styles.input}
                value={
                  groups.find(group => group.pupils.find(pupil => pupil.id === unit.id)) ? groups.find(group => group.pupils.find(pupil => pupil.id === unit.id))?.id : "null"
                }
                onChange={(evt) => {
                  if (evt.target.value !== "null") {
                    moveUnit(unit.id, evt.target.value);
                  }
                }}
              >
                <option value="null">Выберите класс</option>
                {groups.map((group) => (
                  <option value={group.id} key={group.id}>{group.name}</option>
                ))}
              </select>
            ) : (
              ""
            )}
          </>
        )}
      </div>
    </div>
  );
}
