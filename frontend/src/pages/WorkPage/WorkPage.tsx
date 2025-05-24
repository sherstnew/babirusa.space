import styles from './WorkPage.module.scss';
import { Layout } from '../../components/Layout/Layout';
import { useState } from 'react';
import { Enviroments } from '../../components/Enviroments/Enviroments';

export function WorkPage() {

  const [selectedOption, setSelectedOption] = useState<'enviroments' | 'results'>('enviroments');

  return (
    <Layout theme='dark'>
      <div className={styles.content}>
        <section className={styles.menu}>
          <div className={selectedOption === 'enviroments' ? styles.menu__option + ' ' + styles.menu__option_selected : styles.menu__option} onClick={() => setSelectedOption('enviroments')}>Выбор окружения</div>
          <div className={selectedOption === 'results' ? styles.menu__option + ' ' + styles.menu__option_selected : styles.menu__option} onClick={() => setSelectedOption('results')}>Результаты проверок</div>
        </section>
        {
          selectedOption === 'results' ? '' : <Enviroments />
        }
      </div>
    </Layout>
  );
}
