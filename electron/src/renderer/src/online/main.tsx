import { StrictMode, useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import VoiceSelector from '@shared/components/VoiceSelector.jsx';
import { exchangeApiKey, CSRF_HEADER_NAME } from '@shared/api/authSession';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import '@fontsource-variable/inter';
import '../styles/globals.css';
import '../i18n';

const queryClient = new QueryClient();
const base = import.meta.env.DEV ? '/api' : '';
const repo = 'Supertone/supertonic-3';
const voices = ['M1', 'M3', 'M4', 'M5', 'F3', 'F4', 'F5'].map(id => ({ id, name: id }));

async function request(path: string, init: RequestInit = {}) {
  const response = await fetch(base + path, { ...init, credentials: 'same-origin',
    headers: { [CSRF_HEADER_NAME]: '1', ...init.headers } });
  if (!response.ok) throw new Error(String(response.status));
  return response;
}

function Online() {
  const { t } = useTranslation();
  const [authenticated, setAuthenticated] = useState(false);
  const [key, setKey] = useState('');
  const [text, setText] = useState('');
  const [voice, setVoice] = useState('preset:M1');
  const [speed, setSpeed] = useState(1);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [takes, setTakes] = useState<{ id: string; text: string; audio_path: string }[]>([]);
  const [terms, setTerms] = useState<{ accepted: boolean; fingerprint: string }>();
  const [confirmed, setConfirmed] = useState(false);

  async function refresh() {
    const [history, licence] = await Promise.all([
      request('/history').then(r => r.json()),
      request('/models/licenses/acceptance/' + repo).then(r => r.json()),
    ]);
    setTakes(history); setTerms(licence); setAuthenticated(true);
  }
  useEffect(() => { void refresh().catch(() => {}); }, []);

  async function run(action: () => Promise<void>) {
    setPending(true); setError('');
    try { await action(); }
    catch (e) {
      const status = e instanceof Error ? e.message : '';
      if (status === '401') setAuthenticated(false);
      setError(t('settings.remote_backend_error_http', { status: /^\d+$/.test(status) ? status : '503' }));
    } finally { setPending(false); }
  }
  function login(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      const credential = key; setKey('');
      await exchangeApiKey(credential, { apiBase: new URL(base || '/', location.href).href });
      await refresh();
    });
  }
  function generate(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      const data = new FormData();
      for (const [key, value] of Object.entries({ text, language: 'id', engine: 'supertonic3',
        preset_voice: voice.replace('preset:', ''), speed: String(speed), num_step: '8',
        effect_preset: 'raw', postprocess_output: 'false' })) data.set(key, value);
      await request('/generate', { method: 'POST', body: data });
      await refresh();
    });
  }
  return <main className="mx-auto min-h-screen max-w-4xl space-y-8 px-5 py-10 text-foreground">
    <header className="border-b border-border pb-5">
      <h1 className="text-2xl font-semibold tracking-tight">VoiceStudio Online</h1>
      <p className="mt-2 text-sm text-muted-foreground">Supertonic-3 · Bahasa Indonesia · OpenRAIL-M</p>
    </header>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    {!authenticated ? <form onSubmit={login} className="max-w-md space-y-4">
      <label className="block space-y-2"><span>{t('settings.remote_backend_key')}</span>
        <Input aria-label={t('settings.remote_backend_key')} type="password" value={key}
          onChange={e => setKey(e.target.value)} autoComplete="off" required disabled={pending} /></label>
      <Button type="submit" disabled={pending || !key.trim()}>{t('network.connect')}</Button>
    </form> : <>
      {terms && !terms.accepted && <section className="space-y-4 rounded-lg border border-border p-5">
        <h2 className="font-medium">{t('license.title')}</h2>
        <p className="text-sm text-muted-foreground">{t('modelLicense.acceptNotice')}</p>
        <a className="text-sm underline" href="https://huggingface.co/Supertone/supertonic-3/blob/724fb5abbf5502583fb520898d45929e62f02c0b/LICENSE" target="_blank" rel="noreferrer">OpenRAIL-M</a>
        <label className="flex items-start gap-3 text-sm"><input type="checkbox" checked={confirmed}
          onChange={e => setConfirmed(e.target.checked)} />{t('modelLicense.acceptConfirm')}</label>
        <Button disabled={!confirmed || pending} onClick={() => void run(async () => {
          await request('/models/licenses/accept', { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_id: repo, fingerprint: terms.fingerprint, accepted: true }) });
          await refresh();
        })}>{t('modelLicense.accept')}</Button>
      </section>}
      <form onSubmit={generate} className="space-y-5">
        <div className="flex flex-wrap items-end gap-6">
          <label className="block min-w-40 space-y-2"><span className="text-sm">{t('clone.voice_kicker')}</span>
            <VoiceSelector value={voice} onChange={setVoice} profiles={[]} gallery={false}
              presets={voices} engineDefault={false} ariaLabel={t('clone.voice_kicker')} menuPortal disabled={pending} /></label>
          <label className="space-y-2 text-sm"><span>{t('clone.speed')} · {speed.toFixed(2)}×</span>
            <input className="block w-48" aria-label={t('clone.speed')} type="range" min="0.7" max="2" step="0.05"
              value={speed} onChange={e => setSpeed(Number(e.target.value))} disabled={pending} /></label>
        </div>
        <label className="block space-y-2"><span className="text-sm">{t('clone.text_label')} · {text.length}/6000</span>
          <Textarea className="min-h-64 text-base leading-relaxed" value={text} onChange={e => setText(e.target.value)}
            aria-label={t('clone.text_label')} maxLength={6000} placeholder={t('clone.prompt_placeholder')} required disabled={pending} /></label>
        <Button type="submit" disabled={pending || !text.trim() || !terms?.accepted}>
          {pending ? t('preferences.loading') : t('dub.generate')}
        </Button>
      </form>
      <section className="space-y-4">
        <h2 className="font-medium">{t('clone.history_title')}</h2>
        {takes.map(take => <article key={take.id} className="space-y-3 border-t border-border py-4">
          <p className="line-clamp-3 text-sm text-muted-foreground">{take.text}</p>
          <audio className="w-full" controls preload="none" src={`${base}/audio/${take.id}.wav`} />
          <a className="text-sm underline" href={`${base}/audio/${take.id}.wav`} download={`${take.id}.wav`}>{t('clone.download')}</a>
        </article>)}
      </section>
    </>}
    <footer className="border-t border-border pt-5 text-xs text-muted-foreground">
      <a href="https://github.com/debpalash/VoiceStudio" rel="noreferrer" target="_blank">VoiceStudio</a> · AGPL-3.0-only
    </footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<StrictMode>
  <QueryClientProvider client={queryClient}><Online /></QueryClientProvider>
</StrictMode>);
