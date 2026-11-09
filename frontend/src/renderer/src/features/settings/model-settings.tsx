import { EngineFamilyList } from './model-list/engine-family-list';
import type { ModelFamily } from './model-family';

export { DiarisationSettings } from './model-list/diarisation-list';

/** This hosted studio installs only its narration and voice converter models. */
export function ModelSettings({ family: _family }: { family?: ModelFamily }) {
  return <EngineFamilyList family="tts" />;
}
