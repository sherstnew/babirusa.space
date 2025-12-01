import { useState } from "react";
import styles from "./AddTeacher.module.scss";

interface Props {
  onCreate?: () => void;
}

export const AddTeacher = ({ onCreate }: Props) => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login, password }),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Ошибка создания");
      }
      setLogin("");
      setPassword("");
      onCreate && onCreate();
    } catch (e: any) {
      setError(e.message || "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className={styles.wrap} onSubmit={handleCreate}>
      <div className={styles.inputs}>
        <input
          placeholder="Логин"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
        />
        <input
          placeholder="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <div className={styles.actions}>
        <button disabled={loading || !login || !password}>Создать</button>
        {error && <div className={styles.error}>{error}</div>}
      </div>
    </form>
  );
};

export default AddTeacher;
