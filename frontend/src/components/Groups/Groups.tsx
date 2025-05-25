import styles from './Groups.module.scss';
import { useEffect, useState } from 'react';
import { Group } from '../Group/Group';
import { useCookies } from 'react-cookie';

export function Groups(){
  const [groups, setGroups] = useState<any[]>([]);
  const [units, setUnits] = useState<any[]>([]);

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        authorization: cookies['SKFX-TEACHER-AUTH'],
      },
    })
      .then((res) => res.json())
      .then((data: any) => {
        setGroups(data.groups);
        setUnits(data.participants_count);
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <section className={styles.groups}>
      <header className={styles.groups__header}>
        <div className={styles.header__column}>Название</div>
        <div className={styles.header__column}>Кол-во учеников</div>
      </header>
      <section className={styles.groups__list}>
        {groups.map((group, index) => (
          <Group
            key={group.glid}
            groupId={group.glid}
            name={group.name}
            units={units[index]}
          />
        ))}
      </section>
    </section>
  );
}
