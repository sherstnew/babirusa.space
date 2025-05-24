import { useCookies } from 'react-cookie';
import styles from './Header.module.scss';
import graduationHat from '../../static/icons/graduation-hat.png';
import { Link } from 'react-router-dom';

export interface IHeaderProps {
  mode?: 'student' | 'teacher';
}

export function Header(props: IHeaderProps) {
  const [cookies, setCookies, removeCookie] = useCookies([
    'SKFX-SCH-AUTH',
    'SKFX-TEACHER-AUTH',
  ]);

  const logoutAccount = () => {
    if (props.mode === 'teacher') {
      removeCookie('SKFX-TEACHER-AUTH');
    } else {
      removeCookie('SKFX-SCH-AUTH');
    }
  };

  return (
    <header className={styles.header}>
      <Link to={props.mode === 'teacher' ? '/my/groups' : '/'}>
        <img
          src={graduationHat}
          alt='Логотип'
          className={styles.header__logo}
        />
      </Link>
      {(cookies['SKFX-SCH-AUTH'] && props.mode !== 'teacher') ||
      (cookies['SKFX-TEACHER-AUTH'] && props.mode === 'teacher') ? (
        <div className={styles.logged}>
          <span className={styles.logged__user}>
            Залогинен как Пользователь
          </span>
          <span className={styles.logged__exit} onClick={logoutAccount}>
            Выйти
          </span>
        </div>
      ) : (
        ''
      )}
    </header>
  );
}
