import * as React from 'react';
import { IEnviroment } from '../../types/IEnviroment';
import styles from './Enviroment.module.scss';

export interface IEnviromentProps {
  enviroment: IEnviroment
}

export function Enviroment (props: IEnviromentProps) {
  return (
    <div className={styles.enviroment}>
      <div className={styles.enviroment__name}>
        {
          props.enviroment.name
        }
      </div>
      <div className={styles.enviroment__lastUse}>
        {
          props.enviroment.lastUse
        }
      </div>
    </div>
  );
}
