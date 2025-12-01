import styles from "./TeacherList.module.scss";
import { Teacher } from "../../../types/Teacher";

interface Props {
  teachers: Teacher[];
  onDelete?: () => void;
}

export const TeacherList = ({ teachers, onDelete }: Props) => {
  async function handleDelete(id: string) {
    const pass = sessionStorage.getItem("admin_pass") || "";
    if (!confirm("Удалить учителя?")) return;
    const res = await fetch(
      `${import.meta.env.VITE_BACKEND_URL}/api/teacher/${id}`,
      {
        method: "DELETE",
        headers: { "x-admin-password": pass },
      }
    );
    if (res.ok) {
      onDelete && onDelete();
    } else {
      alert("Ошибка при удалении");
    }
  }

  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Логин</th>
            <th>Пользователей</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {teachers.map((t) => (
            <tr key={t.id}>
              <td>{t.login}</td>
              <td>{t.pupils ? t.pupils.length : 0}</td>
              <td>
                <button onClick={() => handleDelete(t.id)}>Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TeacherList;
