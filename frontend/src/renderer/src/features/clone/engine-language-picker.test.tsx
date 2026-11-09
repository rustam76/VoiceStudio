import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import '@/i18n';
import { EngineLanguagePicker } from './engine-language-picker';
vi.mock('@/hooks/use-engines', () => ({
  useEngines: () => ({ activeTts: { supported_language_names: ['English', 'Indonesian'] } }),
}));
vi.mock('@/lib/store/clone-settings', () => ({ useCloneSetting: () => 'Indonesian' }));

it('offers only Indonesian and English for the hosted narration studio', async () => {
  vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(320);
  vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockReturnValue(340);
  render(<EngineLanguagePicker />);
  fireEvent.click(screen.getByRole('button', { name: 'Language' }));
  expect(await screen.findByRole('option', { name: 'Indonesian' })).toBeEnabled();
  expect(screen.getByRole('option', { name: 'English' })).toBeEnabled();
  expect(screen.queryByRole('option', { name: 'Japanese' })).toBeNull();
  expect(screen.queryByRole('option', { name: 'Auto' })).toBeNull();
});
