export type Language = 'en' | 'ru';

export const translations = {
  en: {
    sidebar: {
      newChat: 'New Chat',
      settings: 'Settings',
      about: 'About',
    },
    settings: {
      title: 'Settings',
      description: 'Customize the application according to your preferences',
      appearance: 'Appearance',
      theme: 'Theme',
      themeLight: 'Light',
      themeDark: 'Dark',
      themeAuto: 'Auto',
      language: 'Language',
      chat: 'Chat',
      fontSize: 'Font Size',
      fontSizeSmall: 'Small',
      fontSizeMedium: 'Medium',
      fontSizeLarge: 'Large',
      autoSave: 'Auto-save Chats',
      done: 'Done',
    },
    about: {
      title: 'About MedInsight',
      description: 'MedInsight is an advanced medical analytics platform powered by AI.',
      version: 'Version',
      developer: 'Developer',
      featuresTitle: 'Key Features:',
      feature1: 'Medical data analysis',
      feature2: 'Pattern recognition',
      feature3: 'Insight generation',
      feature4: 'Interactive chat interface',
      close: 'Close',
    },
    input: {
      placeholder: 'Ask a medical question...',
    },
    chat: {
      welcome: 'Hello! I am MedInsight AI. How can I help you today?',
      openChart: 'Open chart',
    }
  },
  ru: {
    sidebar: {
      newChat: 'Новый чат',
      settings: 'Настройки',
      about: 'О программе',
    },
    settings: {
      title: 'Настройки',
      description: 'Настройте приложение по своим предпочтениям',
      appearance: 'Внешний вид',
      theme: 'Тема',
      themeLight: 'Светлая',
      themeDark: 'Тёмная',
      themeAuto: 'Авто',
      language: 'Язык',
      chat: 'Чат',
      fontSize: 'Размер шрифта',
      fontSizeSmall: 'Мелкий',
      fontSizeMedium: 'Средний',
      fontSizeLarge: 'Крупный',
      autoSave: 'Автосохранение чатов',
      done: 'Готово',
    },
    about: {
      title: 'О MedInsight',
      description: 'MedInsight — это передовая платформа медицинской аналитики на базе ИИ.',
      version: 'Версия',
      developer: 'Разработчик',
      featuresTitle: 'Ключевые особенности:',
      feature1: 'Анализ медицинских данных',
      feature2: 'Распознавание паттернов',
      feature3: 'Генерация инсайтов',
      feature4: 'Интерактивный чат',
      close: 'Закрыть',
    },
    input: {
      placeholder: 'Задайте медицинский вопрос...',
    },
    chat: {
      welcome: 'Привет! Я MedInsight AI. Чем могу помочь сегодня?',
      openChart: 'Открыть график',
    }
  }
};
