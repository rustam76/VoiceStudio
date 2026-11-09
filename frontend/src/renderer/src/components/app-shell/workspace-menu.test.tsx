import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

const route = vi.hoisted(() => ({ pathname: '/personas' }));
vi.mock('@tanstack/react-router', () => ({
  useRouterState: ({ select }: any) => select({ location: route }),
  Link: ({ to, activeProps: _activeProps, children, ...props }: any) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
}));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock('@/lib/store/workspace', () => ({ setWorkspace: vi.fn() }));
import { WorkspaceNavigation } from './workspace-menu';

it('opens the current workflow, lets users collapse it, and follows route changes', () => {
  const { rerender } = render(<WorkspaceNavigation />);
  const voice = screen.getByRole('button', { name: 'nav.voice' });
  expect(voice).toHaveAttribute('aria-expanded', 'true');
  expect(screen.getByRole('link', { name: 'nav.saved' })).toHaveAttribute('href', '/personas');
  expect(screen.queryByRole('link', { name: 'workflows.title' })).toBeNull();
  expect(screen.queryByRole('button', { name: 'nav.dub' })).toBeNull();
  fireEvent.click(voice);
  expect(voice).toHaveAttribute('aria-expanded', 'false');
  route.pathname = '/stories';
  rerender(<WorkspaceNavigation />);
  expect(screen.getByRole('button', { name: 'nav.stories' })).toHaveAttribute(
    'aria-expanded',
    'true',
  );
  expect(screen.getByRole('link', { name: 'nav.stories' })).toHaveAttribute('href', '/stories');
});

it('keeps grouped destinations reachable from the compact rail', async () => {
  render(<WorkspaceNavigation compact />);
  fireEvent.click(screen.getByRole('button', { name: 'nav.voice' }));
  expect(await screen.findByRole('link', { name: 'nav.clone_short' })).toHaveAttribute(
    'href',
    '/clone',
  );
  expect(screen.getByRole('link', { name: 'nav.saved' })).toHaveAttribute('href', '/personas');
});

it('opens a compact group for a mouse hover while ignoring touch hover', async () => {
  render(<WorkspaceNavigation compact />);
  const voice = screen.getByRole('button', { name: 'nav.voice' });
  fireEvent.pointerEnter(voice, { pointerType: 'touch' });
  expect(screen.queryByRole('link', { name: 'nav.clone_short' })).toBeNull();
  fireEvent.pointerEnter(voice, { pointerType: 'mouse' });
  expect(await screen.findByRole('link', { name: 'nav.clone_short' })).toBeInTheDocument();
  expect(voice).toHaveAttribute('aria-expanded', 'true');
});

it('keeps the compact flyout mounted until navigation changes the route', async () => {
  route.pathname = '/personas';
  const { rerender } = render(<WorkspaceNavigation compact />);
  fireEvent.click(screen.getByRole('button', { name: 'nav.voice' }));
  const clone = await screen.findByRole('link', { name: 'nav.clone_short' });
  fireEvent.click(clone);
  expect(clone).toBeInTheDocument();
  route.pathname = '/clone';
  rerender(<WorkspaceNavigation compact />);
  await waitFor(() => expect(screen.queryByRole('link', { name: 'nav.clone_short' })).toBeNull());
});

it('closes the compact flyout when choosing the current route again', async () => {
  route.pathname = '/personas';
  render(<WorkspaceNavigation compact />);
  fireEvent.click(screen.getByRole('button', { name: 'nav.voice' }));
  fireEvent.click(await screen.findByRole('link', { name: 'nav.saved' }));
  await waitFor(() => expect(screen.queryByRole('link', { name: 'nav.saved' })).toBeNull());
});
