import { useCookies } from "react-cookie";
import styles from "./Header.module.scss";
import graduationHat from "../../static/icons/graduation-hat.png";
import { Link } from "react-router-dom";

export interface IHeaderProps {
  mode?: "student" | "teacher";
}

export function Header(props: IHeaderProps) {
  const [cookies, , removeCookie] = useCookies(["SKFX-TEACHER-AUTH"]);

  return (
    <header className={styles.header}>
      <Link to={props.mode === "teacher" ? "/my/groups" : "/"}>
        <img
          src={graduationHat}
          alt="Логотип"
          className={styles.header__logo}
        />
      </Link>
      {cookies["SKFX-TEACHER-AUTH"] ? (
        <div className={styles.logged}>
          <span
            className={styles.logged__exit}
            onClick={() => removeCookie("SKFX-TEACHER-AUTH", {path: '/'})}
          >
            Выйти
          </span>
        </div>
      ) : (
        ""
      )}
    </header>
  );
}
