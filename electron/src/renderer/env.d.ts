/// <reference types="vite/client" />

/** Injected by electron.vite.config.ts from the root package.json (single source of truth). */
declare const __APP_VERSION__: string;

/** First 9 characters of the commit this build was made from, or "unknown". */
declare const __BUILD_COMMIT__: string;

/** True only for the browser bundle served by the Python backend. */
declare const __WEB_DEPLOYMENT__: boolean;

// Shared JSX component reused by the Online entry without a desktop bridge.
declare module '@shared/components/VoiceSelector.jsx' {
  import type { ComponentType } from 'react';
  const VoiceSelector: ComponentType<{
    value: string;
    onChange: (value: string) => void;
    profiles?: { id: string; name: string }[];
    gallery?: boolean;
    presets?: boolean | { id: string; name: string }[];
    engineDefault?: boolean;
    ariaLabel: string;
    menuPortal?: boolean;
    disabled?: boolean;
  }>;
  export default VoiceSelector;
}
