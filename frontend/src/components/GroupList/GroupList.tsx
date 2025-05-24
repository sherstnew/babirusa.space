import styles from './GroupList.module.scss';
import backIcon from '../../static/icons/back.svg';
import { Unit } from '../Unit/Unit';
import { useState, useEffect } from 'react';
import { useCookies } from 'react-cookie';
import { Link } from 'react-router-dom';

export interface IGroupListProps {
  groupId: string;
}

export function GroupList(props: IGroupListProps) {
  const [units, setUnits] = useState<any[]>([]);
  const [groupInfo, setGroupInfo] = useState<any>({});

  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/groups`, {
      headers: {
        authorization: cookies['SKFX-TEACHER-AUTH'],
      },
    })
      .then((res) => res.json())
      .then((data: any) => {
        setGroupInfo(data.groups.find((group: any) => group.glid === props.groupId));
        fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/teacher/groups/${props.groupId}/participants`,
          {
            headers: {
              authorization: cookies['SKFX-TEACHER-AUTH'],
            },
          }
        )
          .then((res) => res.json())
          .then((units) => {
            if (!!units) {
              setUnits(units);
            }
          })
          .catch((err) => {
            console.log(err);
          });
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className={styles.card}>
      <header className={styles.header}>
        <Link to='/my/groups'>
          <img src={backIcon} alt='' className={styles.header__back} />
        </Link>
        <div className={styles.header__name}>{groupInfo.name || ''}</div>
      </header>
      <div className={styles.units}>
        <header className={styles.units__header}>
          <div className={styles.header__column}>Имя</div>
          <div className={styles.header__column}>Действия</div>
        </header>
        <section className={styles.units__list}>
          {units.map((unit) => (
            <Unit
              key={unit.glid}
              unitId={unit.glid}
              name={unit.fname + ' ' + unit.lname}
            />
          ))}
        </section>
      </div>
    </div>
  );
}
