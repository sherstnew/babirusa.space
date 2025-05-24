import { useState } from 'react';
import styles from './LoginForm.module.scss';
import { useCookies } from 'react-cookie';

export function LoginForm() {

  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const [cookies, setCookie] = useCookies(['SKFX-TEACHER-AUTH']);

  const auth = (event: any) => {
    event.preventDefault();
    if (!!login && !!password) {
      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/authorize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: login,
          password: password
        })
      }).then(response => response.json())
      .then(data => {
        setCookie('SKFX-TEACHER-AUTH', data.token);
      })
      .catch(err => {
        console.log(err);
      })
    }
  };

  return (
    <form className={styles.form}>
      <input placeholder='Введите логин' type="text" value={login} onChange={(event) => setLogin(event.target.value)} className={styles.input} />
      <input placeholder='Введите пароль' type="password" value={password} onChange={(event) => setPassword(event.target.value)} className={styles.input} />
      <button className={styles.button} onClick={auth}>Войти</button>
    </form>
  );
}
