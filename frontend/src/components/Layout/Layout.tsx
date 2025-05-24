import * as React from 'react';
import styles from './Layout.module.scss';

import { Header } from '../Header/Header';
import { Notifications } from '../Notifications/Notifications';

export interface ILayoutProps {
  children: string | JSX.Element | React.ReactChild | React.ReactFragment | React.ReactPortal | boolean | null | undefined,
  theme: 'dark' | 'light',
  mode?: 'student' | 'teacher'
}

export function Layout (props: ILayoutProps) {
  return (
    <div className={props.theme === 'light' ? styles.layout + ' ' + styles.layout_light : styles.layout}>
        <Header mode={props.mode} />
        <main className={styles.container}>
          <Notifications />
          {
            props.children
          }
        </main>
        <footer className={styles.footer}>
          <div className={styles.team}>
            by skfx
          </div>
        </footer>
    </div>
  );
}
