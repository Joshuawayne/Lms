import { defineStore } from 'pinia'

export const usePreferencesStore = defineStore('preferences', {
  state: () => ({ sidebarCollapsed: false }),
})
