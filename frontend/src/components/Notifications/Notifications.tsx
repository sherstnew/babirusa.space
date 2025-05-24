import styles from './Notifications.module.scss';
import { Notification } from '../Notification/Notification';
import { useContext } from 'react';
import { NotificationsContext } from '../../contexts/NotificationsContext';

export function Notifications() {

  const { notifications } = useContext(NotificationsContext);

  return (
    <div className={styles.notifications}>
      {
        notifications.map(notification => (
          <Notification key={notification.id} id={notification.id} text={notification.text} time={notification.time} />
        ))
      }
    </div>
  );
}
