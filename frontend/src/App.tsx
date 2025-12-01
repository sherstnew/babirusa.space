import { useState } from "react";
import { INotification } from "./types/INotification";
import { NotificationsContext } from "./contexts/NotificationsContext";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { HomePage } from "./pages/HomePage/HomePage";
import { AdminPage } from "./pages/AdminPage/AdminPage";
import { ScanPage } from "./pages/ScanPage/ScanPage";
import { WorkPage } from "./pages/WorkPage/WorkPage";
import { MyPage } from "./pages/MyPage/MyPage";
import { CookiesProvider } from "react-cookie";

function App() {
  const [notifications, setNotifications] = useState<[] | INotification[]>([]);

  return (
    <CookiesProvider>
      <NotificationsContext.Provider
        value={{
          notifications: notifications,
          setNotifications: setNotifications,
        }}
      >
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/workspace" element={<WorkPage />} />
            <Route path="/qr" element={<ScanPage />} />
            <Route path="/my/:category?/:id?" element={<MyPage />} />
          </Routes>
        </BrowserRouter>
      </NotificationsContext.Provider>
    </CookiesProvider>
  );
}

export default App;
