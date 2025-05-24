import styles from './ScanPage.module.scss';
import exampleImage from '../../static/images/example.png';
import { useSearchParams } from 'react-router-dom';
import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export function ScanPage () {

  const [searchParams] = useSearchParams();

  useEffect(() => {
    fetch('id.skfx.io/api/authcode', {
      method: 'POST',
      body: JSON.stringify({
        "authcode": searchParams.get('challenge'),
        "username": "skifry",
        "password": "skifry"
      }),
      headers: {
        'Content-Type': 'application/json',
      }
    })
  }, [searchParams]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
         Сейчас откроется среда разработки...
      </header>
      <section className={styles.help}>
        <img src={exampleImage} alt="Пример QR-кода" className={styles.example} />
        <ul className={styles.steps}>
            <li className={styles.steps__item}>1. Зайдите на <Link to="https://skfx.io/school">https://skfx.io/school</Link></li>
            <li className={styles.steps__item}>2. Отсканируйте QR-код</li>
        </ul>
      </section>
      {/* <div className={styles.button_scan}>Сканировать</div> */}
    </div>
  );
}
