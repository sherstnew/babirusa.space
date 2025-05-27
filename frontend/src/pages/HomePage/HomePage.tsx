import { Layout } from '../../components/Layout/Layout';
import styles from './HomePage.module.scss';
import { Link } from 'react-router-dom';

export function HomePage() {

  return (
      <Layout theme='dark'>
        <div className={styles.content}>
          <section className={styles.slogan}>
            <h1 className={styles.slogan__header}>Облачная среда разработки</h1>
            <h4 className={styles.slogan__description}>Удобная система для коротких сессий разработки, ориентированная для школ и других учебных заведений</h4>
            <section className={styles.slogan__buttons}>
              {/* <button className={styles.button}>Узнать больше</button> */}
              <Link to="/my">
                <button className={styles.button}>Вход для сотрудников</button>
              </Link>
            </section>
          </section>
        </div>
      </Layout>
  );
}
