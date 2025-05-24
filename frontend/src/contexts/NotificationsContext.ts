import { createContext } from 'react';
import { INotification } from '../types/INotification';

interface INotificationsContext {
  notifications: [] | INotification[],
  setNotifications: Function,
}

export const NotificationsContext = createContext<INotificationsContext>({
  notifications: [],
  setNotifications: () => {},
});