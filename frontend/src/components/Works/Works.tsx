import styles from './Works.module.scss';
import { Work } from '../Work/Work';
import { useEffect, useState } from 'react';
import { useCookies } from 'react-cookie';

export function Works() {

  const [works, setWorks] = useState<any>([]);
  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/`, {
      headers: {
        authorization: cookies['SKFX-TEACHER-AUTH']
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data) {
        setWorks(data);
      }
    })
    .catch(err => {
      console.log(err);
      
    })
  }, []);

  return (
    <div className={styles.works}>
      <header className={styles.works__header}>
          <div className={styles.header__column}>Имя</div>
          <div className={styles.header__column}>Действия</div>
      </header>
      <div className={styles.works__list}>
        {
          works.map((work: any) => (
            <Work name={work.name} />
          ))
        }
      </div>
    </div>
  );
}
