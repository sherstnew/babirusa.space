import styles from './GroupList.module.scss';
import backIcon from '../../static/icons/back.svg';
import { Unit } from '../Unit/Unit';
import { useState, useEffect } from 'react';
import { useCookies } from 'react-cookie';
import { Link } from 'react-router-dom';
import { Group } from '../../types/Group';
import { Pupil } from '../../types/Pupil';

export interface IGroupListProps {
  groupId: string;
}

export function GroupList(props: IGroupListProps) {
  const [units, setUnits] = useState<Pupil[]>([]);
  const [groupInfo, setGroupInfo] = useState<Group>();

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        Authorization: `Bearer ${cookies['SKFX-TEACHER-AUTH']}`,
      },
    })
      .then((res) => res.json())
      .then((groups: Group[]) => {
        const groupInfo = groups.find((group) => group.id === props.groupId);
        if (groupInfo) {
          setGroupInfo(groupInfo);
          setUnits(groupInfo.pupils);
        }
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className={styles.card}>
      <header className={styles.header}>
        <Link to='/my/groups'>
          <img src={backIcon} alt='' className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>{groupInfo?.name || ''}</div>
      </header>
      <div className={styles.units}>
        <header className={styles.units__header}>
          <div className={styles.header__column}>Имя</div>
          <div className={styles.header__column}>Действия</div>
        </header>
        <section className={styles.units__list}>
          {units.map((unit, index) => (
            <Unit
              key={index}
              unitId={unit.id}
              name={unit.firstname + ' ' + unit.lastname}
            />
          ))}
        </section>
      </div>
    </div>
  );
}
