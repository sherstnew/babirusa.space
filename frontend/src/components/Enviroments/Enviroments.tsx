import * as React from 'react';
import styles from './Enviroments.module.scss';
import { enviroments } from './../../data/enviroments';
import { Enviroment } from '../Enviroment/Enviroment';

export interface IEnviromentsProps {
}

export function Enviroments (props: IEnviromentsProps) {
  return (
    <section className={styles.enviroments}>
      <header className={styles.enviroments__header}>
        <span className={styles.header__column}>Название</span>
        <span className={styles.header__column}>Посл. использование</span>
      </header>
      <section className={styles.enviroments__list}>
        {
          enviroments.map(env => <Enviroment enviroment={env} />)
        }
      </section>
    </section>
  );
}
