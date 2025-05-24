import styles from './MyPage.module.scss';
import { useCookies } from 'react-cookie';
import { useParams } from 'react-router-dom';
import { useEffect } from 'react';
import { Link } from 'react-router-dom';

import { Layout } from '../../components/Layout/Layout';
import { LoginForm } from '../../components/LoginForm/LoginForm';
import { Groups } from '../../components/Groups/Groups';
import { GroupList } from '../../components/GroupList/GroupList';
import { QRLink } from '../../components/QRLink/QRLink';
import { AddUnit } from '../../components/AddUnit/AddUnit';
import { AddGroup } from '../../components/AddGroup/AddGroup';
import { Works } from '../../components/Works/Works';

export function MyPage() {
  const [cookies] = useCookies(['SKFX-TEACHER-AUTH']);

  const { category, id } = useParams();

  useEffect(() => {
    if (!!!category) {
      window.location.href = '/my/groups';
    }
  }, [category]);

  console.log(id);


  return (
    <Layout theme='light' mode='teacher'>
      <div className={styles.content}>
        {/* здесь проверка по токену */}
        {cookies['SKFX-TEACHER-AUTH'] ? (
          <>
            <section className={styles.menu}>
              <div className={styles.menu__options}>
                <Link
                  to='/my/groups'
                  className={
                    category === 'groups'
                      ? styles.menu__option + ' ' + styles.menu__option_selected
                      : styles.menu__option
                  }
                >
                  Мои классы
                </Link>
                {/* <Link
                  to='/my/myworks'
                  className={
                    category === 'works'
                      ? styles.menu__option + ' ' + styles.menu__option_selected
                      : styles.menu__option
                  }
                >
                  Мои работы
                </Link> */}
                {/* <Link
                  to='/my/queue'
                  className={
                    category === 'queue'
                      ? styles.menu__option + ' ' + styles.menu__option_selected
                      : styles.menu__option
                  }
                >
                  Очередь на проверку
                </Link> */}
              </div>
              <div className={styles.menu__buttons}>
                <Link to='/my/addUnit' className={styles.button}>
                  Добавить ученика
                </Link>
                <Link to='/my/addGroup' className={styles.button}>
                  Создать группу
                </Link>
              </div>
            </section>
            <section className={styles.main}>
              {category === 'groups' && !!!id ? (
                <Groups />
              ) : category === 'myworks' ? (
                ''
                ) : category === 'queue' ? (
                <Works />
              ) : category === 'qr' ? (
                <QRLink unitId={id} />
              ) : category === 'addUnit' ? (
                <AddUnit />
              ) : category === 'addGroup' ? (
                <AddGroup />
              ) : category === 'groups' && !!id ? (
                <GroupList groupId={id} />
              ) : (
                <Groups />
              )}
            </section>
          </>
        ) : (
          <LoginForm />
        )}
      </div>
    </Layout>
  );
}
