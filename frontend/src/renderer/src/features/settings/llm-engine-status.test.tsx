import { render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

vi.mock('./model-list/engine-family-list', () => ({
  EngineFamilyList: ({ family }: { family: string }) => <div>{family}</div>,
}));
import { ModelSettings } from './model-settings';

it('shows narration models even for an old bookmarked LLM route', () => {
  render(<ModelSettings family="llm" />);
  expect(screen.getByText('tts')).toBeVisible();
  expect(screen.queryByText('llm')).toBeNull();
});
