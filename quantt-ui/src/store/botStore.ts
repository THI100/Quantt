import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface UISettings {
  darkMode: boolean;
  compactMode: boolean;
  refreshRate: "500ms" | "1s" | "5s";
  showNotifications: boolean;
}

export interface BotSettings {
  // Extend here with bot-specific config (API keys, strategy params, etc.)
  [key: string]: unknown;
}

export interface BotStoreState {
  ui: UISettings;
  bot: BotSettings;

  // Actions
  setUISettings: (patch: Partial<UISettings>) => void;
  setBotSettings: (patch: Partial<BotSettings>) => void;
  resetUISettings: () => void;
  resetBotSettings: () => void;
  resetAll: () => void;

  // Export / Import as JSON
  exportJSON: () => string;
  importJSON: (json: string) => void;
}

// ─── Defaults ─────────────────────────────────────────────────────────────────

const DEFAULT_UI: UISettings = {
  darkMode: true,
  compactMode: false,
  refreshRate: "1s",
  showNotifications: true,
};

const DEFAULT_BOT: BotSettings = {};

// ─── Store ────────────────────────────────────────────────────────────────────

export const useBotStore = create<BotStoreState>()(
  persist(
    (set, get) => ({
      ui: { ...DEFAULT_UI },
      bot: { ...DEFAULT_BOT },

      setUISettings: (patch) =>
        set((state) => ({ ui: { ...state.ui, ...patch } })),

      setBotSettings: (patch) =>
        set((state) => ({ bot: { ...state.bot, ...patch } })),

      resetUISettings: () => set({ ui: { ...DEFAULT_UI } }),

      resetBotSettings: () => set({ bot: { ...DEFAULT_BOT } }),

      resetAll: () => set({ ui: { ...DEFAULT_UI }, bot: { ...DEFAULT_BOT } }),

      exportJSON: () =>
        JSON.stringify({ ui: get().ui, bot: get().bot }, null, 2),

      importJSON: (json: string) => {
        try {
          const parsed = JSON.parse(json) as Partial<BotStoreState>;
          set({
            ui: { ...DEFAULT_UI, ...(parsed.ui ?? {}) },
            bot: { ...DEFAULT_BOT, ...(parsed.bot ?? {}) },
          });
        } catch {
          console.error("[botStore] importJSON: invalid JSON");
        }
      },
    }),
    {
      name: "store", // localStorage key  →  store.json
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        ui: state.ui,
        bot: state.bot,
      }),
    },
  ),
);

// ─── Convenience selectors (use these in components) ──────────────────────────

export const selectUI = (s: BotStoreState) => s.ui;
export const selectBot = (s: BotStoreState) => s.bot;
