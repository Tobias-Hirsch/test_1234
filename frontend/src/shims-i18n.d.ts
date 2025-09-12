import 'vue-i18n';

declare module 'vue-i18n' {
  export interface DefineLocaleMessage {
    [key: string]: any;
  }

  export interface DefineDateTimeFormat {
    [key: string]: any;
  }

  export interface DefineNumberFormat {
    [key: string]: any;
  }
}

declare module '*.json' {
  const value: any;
  export default value;
}