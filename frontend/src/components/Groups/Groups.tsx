import styles from './Groups.module.scss';
import { useEffect, useState } from 'react';
import { Group } from '../Group/Group';
import { useCookies } from 'react-cookie';
import { Group as IGroup } from '../../types/Group';

export function Groups(){
  const [groups, setGroups] = useState<IGroup[]>([]);

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        Authorization: `Bearer ${cookies['SKFX-TEACHER-AUTH']}`,
      },
    })
      .then((res) => res.json())
      .then((data: any) => {
        setGroups(data);
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
            key={index}
            groupId={group.id}
            name={group.name}
            units={group.pupils.length}
          />
        ))}
      </section>
    </section>
  );
}
