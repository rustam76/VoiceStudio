import type { ReactNode } from 'react';
import { Link } from '@tanstack/react-router';
import { AudioLinesIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useBackendStatus, isBackendReachable } from '@/hooks/use-backend-status';
import { useEngines } from '@/hooks/use-engines';
import { useAppActivities } from '@/lib/app-activity';
import { cn } from '@/lib/utils';

/** Narration status reuses engine discovery; retired tools must not be polled. */
export function StatusBar({
  compact = false,
  inline = false,
  footerLeading,
}: {
  compact?: boolean;
  inline?: boolean;
  footerLeading?: ReactNode;
}) {
  const { t } = useTranslation();
  const backend = useBackendStatus();
  const engines = useEngines();
  const activities = useAppActivities();
  const online = isBackendReachable(backend.stage);
  const available = online && !engines.isError && engines.activeTts?.available;
  const working = activities.synthesis > 0 || activities.longform > 0;
  const label = t(
    !online
      ? 'modelMaintenance.offline'
      : engines.isLoading
        ? 'preferences.loading'
        : !available
          ? 'modelSettings.unavailable'
          : working
            ? 'engineRuntime.working'
            : 'modelSettings.available',
  );
  return (
    <footer
      className={cn(
        'shrink-0 text-xs text-muted-foreground',
        inline ? 'contents' : 'border-t border-border/50 p-2',
      )}
    >
      {footerLeading}
      <Link
        to="/settings/models"
        aria-label={t('engineSidebar.tts')}
        title={`${engines.activeTts?.display_name || t('engineSidebar.tts')} · ${label}`}
        className={cn(
          'flex min-w-0 items-center gap-2 rounded-md p-2 hover:bg-sidebar-accent',
          compact && 'justify-center',
        )}
      >
        <AudioLinesIcon className="size-4 shrink-0" aria-hidden="true" />
        <span
          className={cn(
            'size-1.5 shrink-0 rounded-full',
            available ? 'bg-emerald-500' : 'bg-muted-foreground',
          )}
          aria-hidden="true"
        />
        <span role="status" className={cn('truncate', compact && 'sr-only')}>
          {label}
        </span>
      </Link>
    </footer>
  );
}
