import styles from "./MyPage.module.scss";
import { useCookies } from "react-cookie";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Layout } from "../../components/Layout/Layout";
import { LoginForm } from "../../components/LoginForm/LoginForm";
import { Groups } from "../../components/Groups/Groups";
import { GroupList } from "../../components/GroupList/GroupList";
import { AddUnit } from "../../components/AddUnit/AddUnit";
import { AddGroup } from "../../components/AddGroup/AddGroup";
import { Works } from "../../components/Works/Works";
import { UnitsList } from "../../components/UnitsList/UnitsList";

export function MyPage() {
  const [cookies] = useCookies(["SKFX-TEACHER-AUTH"]);

  const [tokenValid, setTokenValid] = useState<boolean | null>(null);

  const { category, id } = useParams();

  useEffect(() => {
    if (!!!category) {
      window.location.href = "/my/groups";
    }
  }, [category]);

  useEffect(() => {
    setTokenValid(null);
    if (cookies["SKFX-TEACHER-AUTH"]) {
      fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
        headers: {
          Authorization: `Bearer ${cookies["SKFX-TEACHER-AUTH"]}`,
        },
      })
        .then((res) => {
          if (res.status === 401) throw new Error("Unauthorized");
          return res.json();
        })
        .then(() => {
          setTokenValid(true);
        })
        .catch((err) => {
          console.log(err);
          setTokenValid(false);
        });
    } else {
      setTokenValid(false);
    }
  }, [cookies]);

  return (
    <Layout theme="light" mode="teacher">
      <div className={styles.content}>
        {tokenValid ? (
          <>
            <section className={styles.menu}>
              <div className={styles.menu__options}>
                <Link to="/my/groups" className={styles.menu__option}>
                  Панель
                </Link>
              </div>
              <div className={styles.menu__buttons}>
                <Link to="/my/groups" className={styles.button}>
                  Группы
                </Link>
                <Link to="/my/units" className={styles.button}>
                  Ученики
                </Link>
                <Link to="/my/addUnit" className={styles.button}>
                  Создать ученика
                </Link>
                <Link to="/my/addGroup" className={styles.button}>
                  Создать группу
                </Link>
              </div>
            </section>
            <section className={styles.main}>
              {category === "groups" && !!!id ? (
                <Groups />
              ) : category === "myworks" ? (
                ""
              ) : category === "queue" ? (
                <Works />
              ) : // ) : category === 'qr' ? (
              //   <QRLink unitId={id} />
              category === "addUnit" ? (
                <AddUnit />
              ) : category === "addGroup" ? (
                <AddGroup />
              ) : category === "groups" && !!id ? (
                <GroupList groupId={id} />
              ) : category === "units" ? (
                <UnitsList />
              ) : (
                <Groups />
              )}
            </section>
          </>
        ) : tokenValid === null ? (
          "Загрузка..."
        ) : (
          <LoginForm />
        )}
      </div>
    </Layout>
  );
}
