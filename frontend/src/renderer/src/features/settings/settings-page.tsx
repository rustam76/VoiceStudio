import { MirrorSettings } from './mirror-settings';
import { PrivacySettings } from './privacy-settings';
import { StorageSettings } from './storage-settings';
import { MediaTools } from './media-tools';
import { LogSettings } from './log-settings';
import { PronunciationSettings } from './pronunciation-settings';
import { PauseFillSettings } from './pause-fill-settings';
import { UsageSettings } from './usage-settings';
import { OpenApiSettings } from './openapi-settings';
import { ModelSettings } from './model-settings';
import { modelFamilies } from './model-family';
import { Link, useRouterState } from '@tanstack/react-router';
import {
  BarChart3Icon,
  BracesIcon,
  ChevronRightIcon,
  HardDriveIcon,
  ShieldCheckIcon,
  SpellCheckIcon,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { isMac } from '@/components/bridge';
import { cn } from '@/lib/utils';
import { SettingsContent, SettingsPageTitleContext } from './settings-layout';
import { SettingsNav, type SettingsLocation } from './settings-nav';
import { AppearanceResetButton, AppearanceSettings, GeneralSettings } from './settings-preferences';
import { rememberSettingsRoute } from '@/lib/settings-route';

// the generated speech sounds.
function SpeechOutputSettings() {
  return (
    <>
      <PauseFillSettings />
      <PronunciationSettings />
    </>
  );
}

const extraSettings = [
  {
    to: '/settings/pronunciation',
    label: 'pronunciation.title',
    Icon: SpellCheckIcon,
    Component: SpeechOutputSettings,
    fields: [
      'pronunciation.title',
      'pronunciation.help',
      'pronunciation.test_label',
      'pronunciation.backup_title',
      'pauseFill.title',
      'pauseFill.room_tone',
    ],
  },
  {
    to: '/settings/usage',
    label: 'settings.usage',
    Icon: BarChart3Icon,
    Component: UsageSettings,
    fields: [
      'settings.usage',
      'settings.usage_takes',
      'settings.usage_audio',
      'settings.usage_by_language',
    ],
  },
  {
    to: '/settings/privacy',
    label: 'settings.privacy',
    Icon: ShieldCheckIcon,
    Component: PrivacySettings,
    fields: [
      'settings.privacy',
      'privacy.analytics_title',
      'privacy.watermark_title',
      'settings.history_retention',
    ],
  },
  {
    to: '/settings/storage',
    label: 'settings.storage',
    Icon: HardDriveIcon,
    Component: StorageSettings,
    fields: [
      'settings.storage',
      'settings.storage_usage',
      'settings.history_retention',
      'updates.backup_line',
    ],
  },
  {
    to: '/settings/openapi',
    label: 'openapi.title',
    Icon: BracesIcon,
    Component: OpenApiSettings,
    fields: ['openapi.title', 'openapi.copy_url', 'openapi.open_raw'],
  },
] as const;

/** Settings → Account is listed only when this build offers VoiceStudio Cloud accounts. */
export function extraSettingsFor(cloudAccountsAvailable: boolean) {
  void cloudAccountsAvailable;
  return extraSettings;
}

export function SettingsPage() {
  const { t } = useTranslation();
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  });
  const extras = extraSettingsFor(false);
  const extra = extras.find((item) => pathname === item.to);
  const isOpenApi = pathname === '/settings/openapi';
  const isModels = pathname.includes('/models');
  const isMedia = pathname.endsWith('/media');
  const isLogs = pathname.endsWith('/logs');
  const modelFamily = modelFamilies.find((family) => pathname.endsWith('/models/' + family));
  // /settings opens General, the first entry in the list.
  const section = pathname.endsWith('/appearance') ? 'appearance' : 'general';
  const [target, setTarget] = useState<string | null>(null);
  useEffect(() => rememberSettingsRoute(pathname), [pathname]);
  useEffect(() => {
    if (!target) return;
    const field = document.getElementById(target);
    if (field) {
      field.scrollIntoView({ block: 'center' });
      field.focus({ preventScroll: true });
      setTarget(null);
    }
  }, [pathname, target]);
  const location: SettingsLocation = extra
    ? { kind: 'extra', to: extra.to }
    : isMedia
      ? { kind: 'media' }
      : isLogs
        ? { kind: 'logs' }
        : isModels
          ? { kind: 'models', family: modelFamily }
          : { kind: 'section', section };
  const title = extra
    ? t(extra.label)
    : isMedia
      ? t('settings.audio_tools')
      : isLogs
        ? t('settings.logs')
        : isModels
          ? t(modelFamily ? 'engineSidebar.' + modelFamily : 'modelSettings.models')
          : t(`preferences.${section}`);

  return (
    <div className="flex h-full min-h-0">
      <SettingsNav extras={extras} location={location} onTarget={setTarget} />
      <section className="flex min-w-0 flex-1 flex-col bg-background">
        <header
          className={cn(
            'workspace-titlebar flex shrink-0 items-center gap-2 px-5 text-sm',
            isMac() ? 'account-corner-safe' : 'native-controls-right',
          )}
        >
          <span className="text-muted-foreground">{t('nav.settings')}</span>
          <ChevronRightIcon aria-hidden="true" className="size-3.5 text-muted-foreground/60" />
          {modelFamily && (
            <>
              <Link
                to="/settings/models"
                className="text-muted-foreground hover:text-foreground hover:underline"
              >
                {t('modelSettings.models')}
              </Link>
              <ChevronRightIcon aria-hidden="true" className="size-3.5 text-muted-foreground/60" />
            </>
          )}
          <h1 className="font-medium">{title}</h1>
          {location.kind === 'section' && section === 'appearance' && <AppearanceResetButton />}
        </header>
        <SettingsPageTitleContext.Provider value={title}>
          <SettingsContent
            fullBleed={isOpenApi || isLogs}
            key={
              extra?.to ||
              (isMedia ? 'media' : isLogs ? 'logs' : isModels ? (modelFamily ?? 'models') : section)
            }
          >
            {extra ? (
              <extra.Component />
            ) : isMedia ? (
              <MediaTools />
            ) : isLogs ? (
              <LogSettings />
            ) : isModels ? (
              <>
                <ModelSettings key={modelFamily ?? 'all'} family={modelFamily} />
                {!modelFamily && <MirrorSettings />}
              </>
            ) : section === 'appearance' ? (
              <AppearanceSettings />
            ) : (
              <GeneralSettings />
            )}
          </SettingsContent>
        </SettingsPageTitleContext.Provider>
      </section>
    </div>
  );
}
