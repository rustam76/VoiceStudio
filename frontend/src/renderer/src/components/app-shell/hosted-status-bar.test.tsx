import { render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

const state = vi.hoisted(() => ({ stage: 'ready' }));
const api = vi.hoisted(() => vi.fn());
vi.mock('@/lib/api/client', () => ({ apiJson: api }));
vi.mock('@/hooks/use-engines', () => ({
  useEngines: () => ({ activeTts: { available: true, display_name: 'Supertonic + OpenVoice' } }),
}));
vi.mock('@/hooks/use-backend-status', () => ({
  useBackendStatus: () => state,
  isBackendReachable: (stage: string) => stage === 'ready',
}));
vi.mock('@/lib/app-activity', () => ({ useAppActivities: () => ({ synthesis: 0, longform: 0 }) }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: any) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
}));
import { StatusBar } from './status-bar';

it('shows narration status without requesting retired engine families', () => {
  state.stage = 'ready';
  render(<StatusBar footerLeading={<span>Settings</span>} />);
  expect(screen.getByRole('status')).toHaveTextContent('modelSettings.available');
  expect(screen.getByRole('link')).toHaveAttribute('href', '/settings/models');
  expect(screen.getByText('Settings')).toBeVisible();
  expect(api).not.toHaveBeenCalled();
});

it('reports offline even when engine metadata is cached', () => {
  state.stage = 'failed';
  render(<StatusBar compact />);
  expect(screen.getByRole('status')).toHaveTextContent('modelMaintenance.offline');
});
