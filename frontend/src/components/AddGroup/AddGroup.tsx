import { useState } from 'react';
import styles from './AddGroup.module.scss';
import backIcon from '../../static/icons/back.svg';
import { useCookies } from 'react-cookie';
import { useContext } from 'react';
import { NotificationsContext } from '../../contexts/NotificationsContext';
import { v4 } from 'uuid';
import { Link } from 'react-router-dom';

export function AddGroup() {
  const { notifications, setNotifications } = useContext(NotificationsContext);

  const [groupName, setGroupName] = useState('');
  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  const createGroup = (event: any) => {
    event.preventDefault();
    if (groupName !== '') {
      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/groups/new`, {
        method: 'POST',
        headers: {
          authorization: cookies['SKFX-TEACHER-AUTH'],
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: groupName,
        }),
      })
        .then((res) => {
          if (res.status === 200) {
            window.location.href = '/my/groups';
          } else {
            setNotifications([
              ...notifications,
              {
                id: v4(),
                text: 'Не удалось создать группу',
                time: 5000,
              },
            ]);
          }
        })
        .catch((err) => {
          console.log(err);

          setNotifications([
            ...notifications,
            {
              id: v4(),
              text: 'Неизвестная ошибка',
              time: 5000,
            },
          ]);
        });
    } else {
      setNotifications([
        ...notifications,
        {
          id: v4(),
          text: 'Введите имя группы',
          time: 5000,
        },
      ]);
    }
  };

  return (
    <div className={styles.add}>
      <header className={styles.header}>
        <Link to='/my/groups'>
          <img src={backIcon} alt='' className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>Добавить группу</div>
      </header>
      <form className={styles.form}>
        <input
          type='text'
          placeholder='Введите название группы'
          className={styles.input}
          value={groupName}
          onChange={(event) => setGroupName(event.target.value)}
        />
        <button className={styles.button} onClick={createGroup}>
          Создать группу
        </button>
      </form>
    </div>
  );
}
