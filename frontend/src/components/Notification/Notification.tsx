import styles from './Notification.module.scss';
import crossIcon from '../../static/icons/cross.svg';
import { useContext, useEffect, useState } from 'react';
import { NotificationsContext } from '../../contexts/NotificationsContext';

export interface INotificationProps {
  id: number,
  text: string;
  time: number
}

export function Notification (props: INotificationProps) {

  const {notifications, setNotifications} = useContext(NotificationsContext);

  const [hidden, setHidden] = useState(false);

  const removeNotification = () => {
    setHidden(true);
    setTimeout(() => {
      setNotifications(notifications.filter(notification => notification.id !== props.id));
    }, 1000);
  };

  useEffect(() => {
    setTimeout(() => {
      removeNotification();
    }, 1000 + props.time);
  }, []);

  return (
    <div className={hidden ? styles.notification + ' ' + styles.notification_hidden : styles.notification} onClick={removeNotification}>
      <div className={styles.text}>
        {props.text}
      </div>
      <img src={crossIcon} alt="" className={styles.cross} />
    </div>
  );
}
