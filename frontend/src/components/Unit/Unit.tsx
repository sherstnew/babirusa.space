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
  const [showCheckDialog, setShowCheckDialog] = useState<boolean>(false);
  const [taskPrompt, setTaskPrompt] = useState<string>("");
  const [checkResults, setCheckResults] = useState<any>(null);

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
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups/pupils?group_id=${classId}&pupil_id=${unitId}`, {
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

  function checkTask() {
    if (!taskPrompt.trim()) {
      setNotifications([
        ...notifications,
        {
          id: v4(),
          text: "Пожалуйста, введите задание",
          time: 5000,
        },
      ]);
      return;
    }

    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/check_task_ai`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: taskPrompt,
        pupil_username: unit.username,
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Check task error");
        return res.json();
      })
      .then((data) => {
        setCheckResults(data);
        setShowCheckDialog(false);
        setTaskPrompt("");
      })
      .catch((err) => {
        console.log(err);

        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: "Ошибка проверки задания",
            time: 5000,
          },
        ]);
      });
  }

  return (
    <div className={styles.unit}>
      <div className={styles.unit__name}>
        {unit.lastname + " " + unit.firstname + " / " + unit.username}
      </div>
      <div className={styles.unit__actions}>
        <div
          className={styles.action}
          onClick={() => (password ? setPassword("") : getPassword())}
        >
          {password ? password : "Пароль"}
        </div>
        <Link
          to={`https://${unit.username}.babirusa.website`}
          target="_blank"
          className={styles.action}
        >
          Пространство
        </Link>
        <div
          className={styles.action}
          onClick={() => setShowCheckDialog(true)}
        >
          Проверить задание
        </div>
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
              fetch_links=True
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
      
      {showCheckDialog && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3>Введите задание для проверки</h3>
              <button
                className={styles.closeBtn}
                onClick={() => {
                  setShowCheckDialog(false);
                  setTaskPrompt("");
                }}
              >
                ✕
              </button>
            </div>
            <textarea
              className={styles.taskInput}
              value={taskPrompt}
              onChange={(e) => setTaskPrompt(e.target.value)}
              placeholder="Вставьте код или описание задания..."
            />
            <div className={styles.modalActions}>
              <button
                className={styles.checkBtn}
                onClick={checkTask}
              >
                Проверить задание
              </button>
              <button
                className={styles.cancelBtn}
                onClick={() => {
                  setShowCheckDialog(false);
                  setTaskPrompt("");
                }}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {checkResults && (
        <div className={styles.resultsContainer}>
          <div className={styles.resultsHeader}>
            <h3>Результаты проверки</h3>
            <button
              className={styles.closeBtn}
              onClick={() => setCheckResults(null)}
            >
              ✕
            </button>
          </div>
          {checkResults.results && checkResults.results.map((result: any, idx: number) => (
            <div key={idx} className={styles.resultItem}>
              <div className={`${styles.resultStatus} ${result.correct ? styles.correct : styles.incorrect}`}>
                {result.correct ? "✓ Правильно" : "✗ Ошибка"}
              </div>
              <div className={styles.resultUsername}>{result.username}</div>
              <div className={styles.resultSummary}>
                <strong>Резюме:</strong> {result.summary}
              </div>
              {result.suggestions && (
                <div className={styles.resultSuggestions}>
                  <strong>Рекомендации:</strong> {result.suggestions}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
