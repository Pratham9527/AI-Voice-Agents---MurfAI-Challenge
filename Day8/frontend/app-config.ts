export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Eldoria Adventures',
  pageTitle: 'D&D Voice Game Master',
  pageDescription: 'An interactive fantasy adventure powered by voice AI',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#7c3aed',  // Fantasy purple
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#a78bfa',  // Light purple for dark mode
  startButtonText: '⚔️ Begin Adventure',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
