<script setup>
import { computed } from 'vue'

const props = defineProps({
  profiles: { type: Array, default: () => [] },
  modelValue: { type: String, default: '' },
  groupDefaultProfileId: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const activeProfiles = computed(() => (
  props.profiles.filter((profile) => String(profile?.status || '').toLowerCase() === 'active')
))

const showSelector = computed(() => {
  if (props.groupDefaultProfileId) return false
  return activeProfiles.value.length > 1
})

const lockedProfile = computed(() => {
  if (!props.groupDefaultProfileId) return null
  return activeProfiles.value.find(
    (profile) => String(profile.id) === String(props.groupDefaultProfileId),
  ) || null
})

const selectedProfile = computed(() => (
  activeProfiles.value.find((profile) => String(profile.id) === String(props.modelValue)) || null
))

const noProfileConfigured = computed(() => !props.loading && activeProfiles.value.length === 0)

function onChange(event) {
  emit('update:modelValue', event.target.value)
}
</script>

<template>
  <div data-testid="conversation-profile-selector">
    <div v-if="loading" class="small text-muted">Chargement des profils conversationnels…</div>

    <div v-else-if="noProfileConfigured" class="alert alert-warning py-2 px-3 small mb-0">
      Aucun profil conversationnel actif n’est disponible pour ton organisation.
      Demande à ton formateur de configurer un profil global avant de lancer une session.
    </div>

    <template v-else>
      <div v-if="showSelector" class="mb-3">
        <label class="form-label" for="selected-conversation-profile">Profil de conversation</label>
        <select
          id="selected-conversation-profile"
          class="form-select"
          :disabled="disabled"
          :value="modelValue"
          data-testid="conversation-profile-select"
          @change="onChange"
        >
          <option
            v-for="profile in activeProfiles"
            :key="profile.id"
            :value="profile.id"
          >
            {{ profile.name }}{{ profile.is_default ? ' (défaut org)' : '' }}
          </option>
        </select>
        <p class="small text-muted mb-0 mt-2">
          Ce profil regroupe les modes diagnostic, réflexif et bûchage. Tu pourras changer de mode en séance.
        </p>
      </div>

      <div v-else class="mb-3">
        <p class="small text-muted mb-1">Profil de conversation</p>
        <p class="mb-0 fw-semibold" data-testid="conversation-profile-single">
          {{ lockedProfile?.name || selectedProfile?.name || 'Profil du groupe' }}
        </p>
        <p
          v-if="lockedProfile?.description || selectedProfile?.description"
          class="small text-muted mb-0 mt-1"
        >
          {{ lockedProfile?.description || selectedProfile?.description }}
        </p>
        <p class="small text-muted mb-0 mt-1">
          {{ groupDefaultProfileId
            ? 'Profil imposé par ton groupe pour cette session.'
            : 'Un seul profil actif : il sera utilisé automatiquement pour cette session.' }}
        </p>
      </div>

      <p
        v-if="groupDefaultProfileId && String(groupDefaultProfileId) === String(modelValue)"
        class="small text-muted mb-0"
      >
        Profil recommandé pour ton groupe.
      </p>
    </template>
  </div>
</template>
