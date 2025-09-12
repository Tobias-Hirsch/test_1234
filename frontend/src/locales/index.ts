import { createI18n } from 'vue-i18n';

// Import language files
import en from './en.json';
import zh from './zh.json';

const messages = {
  en,
  zh,
};

const determineLocale = () => {
  // Check localStorage first
  const savedLanguage = localStorage.getItem('language');
  if (savedLanguage) {
    return savedLanguage;
  }

  // If no language in localStorage, use browser language
  const browserLanguage = navigator.language.split('-')[0]; // Get primary language tag
  const supportedLocales = Object.keys(messages);
  if (supportedLocales.includes(browserLanguage)) {
    return browserLanguage;
  }

  // Fallback to default locale
  return 'en';
};

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: determineLocale(), // Set locale based on localStorage or browser language
  fallbackLocale: 'en', // Fallback locale
  messages,
});

export default i18n;