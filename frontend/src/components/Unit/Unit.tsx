import styles from './Unit.module.scss';
import { useCookies } from 'react-cookie';
import { useContext } from 'react';
import { NotificationsContext } from '../../contexts/NotificationsContext';
import { v4 } from 'uuid';
import { Link } from 'react-router-dom';

export interface IUnitProps {
  name: string;
  unitId: string;
}

export function Unit(props: IUnitProps) {

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);
  const { notifications, setNotifications } = useContext(NotificationsContext);

  const deleteUnit = (unitId: string) => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/pupils/${unitId}`, {
      method: 'DELETE',
      headers: {
        authorization: cookies['SKFX-TEACHER-AUTH'],
      }
    })
    .then(res => {
      if (res.status === 200) {
        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: 'Ученик успешно удален',
            time: 5000,
          },
        ]);
      } else {
        setNotifications([
          ...notifications,
          {
            id: v4(),
            text: 'Ошибка удаления ученика',
            time: 5000,
          },
        ]);
      }
      window.location.href = '/my';
    })
    .catch(err => {
      console.log(err);

      setNotifications([
        ...notifications,
        {
          id: v4(),
          text: 'Ошибка удаления ученика',
          time: 5000,
        },
      ]);
    })
  };

  return (
    <div className={styles.unit}>
      <div className={styles.unit__name}>
        {
          props.name
        }
      </div>
      <div className={styles.unit__actions}>
        <Link to="http://test.isch.skfx.io:9000/?folder=/home/coder" className={styles.action}>открыть рабочее пространство</Link>
        <Link to="/my/qr" className={styles.action}>код привязки</Link>
        <div className={styles.action} onClick={() => deleteUnit(props.unitId)}>удалить</div>
      </div>
    </div>
  );
}
