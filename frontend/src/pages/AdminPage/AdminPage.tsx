import { useEffect, useState } from "react";
import { Layout } from "../../components/Layout/Layout";
import styles from "./AdminPage.module.scss";
import { Teacher } from "../../types/Teacher";
import { AddTeacher } from "../../components/Admin/AddTeacher/AddTeacher";
import { TeacherList } from "../../components/Admin/TeacherList/TeacherList";

export function AdminPage() {
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [password, setPassword] = useState<string>(
    sessionStorage.getItem("admin_pass") || ""
  );
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("admin_pass");
    if (saved === import.meta.env.VITE_ADMIN_PANEL_PASSWORD) {
      setAuthenticated(true);
      fetchTeachers(saved);
    }
  }, []);

  async function fetchTeachers(pass: string) {
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/teacher`, {
        headers: { "x-admin-password": pass },
      });
      if (!res.ok) throw new Error("Не удалось получить список");
      const data = await res.json();
      setTeachers(data);
    } catch (e: any) {
      setError(e.message || "Ошибка");
    }
  }

  function handleAuth(e: React.FormEvent) {
    e.preventDefault();
    if (password === import.meta.env.VITE_ADMIN_PANEL_PASSWORD) {
      sessionStorage.setItem("admin_pass", password);
      setAuthenticated(true);
      setError(null);
      fetchTeachers(password);
    } else {
      setError("Неверный пароль");
    }
  }

  return (
    <Layout theme="dark">
      <div className={styles.wrap}>
        <h2 className={styles.title}>Панель администратора</h2>
        {!authenticated ? (
          <form onSubmit={handleAuth} className={styles.form}>
            <input
              className={styles.input}
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button className={styles.button} type="submit">
              Войти
            </button>
            {error && <div className={styles.error}>{error}</div>}
          </form>
        ) : (
          <section className={styles.panel}>
            <AddTeacher
              onCreate={async () => {
                const pass = sessionStorage.getItem("admin_pass") || "";
                await fetchTeachers(pass);
              }}
            />
            <TeacherList
              teachers={teachers}
              onDelete={async () => {
                const pass = sessionStorage.getItem("admin_pass") || "";
                await fetchTeachers(pass);
              }}
            />
          </section>
        )}
      </div>
    </Layout>
  );
}

export default AdminPage;
