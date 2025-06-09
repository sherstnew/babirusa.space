import { useContext } from 'react';
import styles from './Group.module.scss';
import { NotificationsContext } from '../../contexts/NotificationsContext';
import { v4 } from 'uuid';
import { useCookies } from 'react-cookie';
import { Link } from 'react-router-dom';

export interface IGroupProps {
  groupId: string;
  name: string;
  units: number;
}

export function Group(props: IGroupProps) {

  const { notifications, setNotifications } = useContext(NotificationsContext);

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  const deleteGroup = (groupId: string) => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups?groups_id=${groupId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${cookies['SKFX-TEACHER-AUTH']}`,
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
    <div className={styles.group}>
      <div className={styles.group__name}>{props.name}</div>
      <div className={styles.group__units}>{props.units}</div>
      <div className={styles.group__actions}>
        <div className={styles.action} onClick={() => deleteGroup(props.groupId)}>
          Удалить
        </div>
        <Link to={`/my/groups/${props.groupId}`} className={styles.action}>Подробнее</Link>
      </div>
    </div>
  );
}
