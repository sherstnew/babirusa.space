import styles from './Work.module.scss';
import { Link } from 'react-router-dom';

export interface IWorkProps {
  name: string,
};

export function Work(props: IWorkProps) {
  return (
    <div className={styles.work}>
      <div className={styles.work__name}>
        {
          props.name
        }
      </div>
      <div className={styles.work__actions}>
        <Link to="https://google.com" className={styles.action}>Посмотреть</Link>
      </div>
    </div>
  );
}
