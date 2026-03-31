// Augment the Window interface so TypeScript knows about our preload bridge
export {};

declare global {
  interface Window {
    electronAPI: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      platform: NodeJS.Platform;
    };
  }
}
