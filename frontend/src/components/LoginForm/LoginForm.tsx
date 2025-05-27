import { useState } from 'react';
import styles from './LoginForm.module.scss';
import { useCookies } from 'react-cookie';

export function LoginForm() {

  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const [, setCookie] = useCookies(['SKFX-TEACHER-AUTH']);

  const auth = (event: any) => {
    event.preventDefault();

    if (!!login && !!password) {
      const formData = new URLSearchParams();
      formData.append("username", login);
      formData.append("password", password);

      fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/login`, {
        method: 'POST',
        body: formData
      }).then((res) => {
        if (!res.ok) throw new Error(`Status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.access_token) {
          setCookie('SKFX-TEACHER-AUTH', data.access_token, { domain: '.babirusa.space', path: '/' });
        }
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
