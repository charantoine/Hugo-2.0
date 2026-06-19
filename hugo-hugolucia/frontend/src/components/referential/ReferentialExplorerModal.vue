<script setup>
import { ref, watch, computed } from 'vue'
import api from '../../api/client'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  referentialId: { type: String, default: '' },
  referentialName: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)
const loadError = ref('')
const items = ref([])

const blockGroups = computed(() => {
  const map = new Map()
  for (const item of items.value) {
    const bc = String(item.block_code || '').trim()
    const bl = String(item.block_label || '').trim()
    const key = !bc && !bl ? '__none__' : `${bc}\n${bl}`
    if (!map.has(key)) {
      map.set(key, { block_code: bc, block_label: bl, items: [] })
    }
    map.get(key).items.push(item)
  }
  const arr = [...map.values()]
  arr.sort((a, b) => {
    const c = (a.block_code || '').localeCompare(b.block_code || '', 'fr', { sensitivity: 'base' })
    if (c !== 0) return c
    return (a.block_label || '').localeCompare(b.block_label || '', 'fr', { sensitivity: 'base' })
  })
  for (const g of arr) {
    g.items.sort((x, y) => String(x.code || '').localeCompare(String(y.code || ''), 'fr', { numeric: true }))
  }
  return arr
})

function sortedCriteria(row) {
  const list = Array.isArray(row.criteria) ? [...row.criteria] : []
  list.sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0))
  return list
}

function close() {
  emit('update:modelValue', false)
}

async function load() {
  if (!props.referentialId) {
    items.value = []
    return
  }
  loading.value = true
  loadError.value = ''
  items.value = []
  try {
    const { data } = await api.get(`/referentials/${props.referentialId}/items/`)
    const list = Array.isArray(data) ? data : (data?.results || [])
    items.value = list
  } catch (e) {
    loadError.value = e.response?.data?.detail || 'Impossible de charger les items du référentiel.'
    items.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.referentialId],
  ([open, id]) => {
    if (open && id) load()
    if (!open) {
      loadError.value = ''
    }
  },
  { flush: 'post' },
)
</script>

<template>
  <div v-if="modelValue">
    <div
      class="modal fade show d-block"
      tabindex="-1"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="'referential-explorer-title'"
    >
      <div class="modal-dialog modal-xl modal-dialog-scrollable" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 id="referential-explorer-title" class="modal-title mb-0">Référentiel</h5>
              <div v-if="referentialName" class="small text-muted">{{ referentialName }}</div>
            </div>
            <button type="button" class="btn-close" aria-label="Fermer" @click="close" />
          </div>
          <div class="modal-body">
            <div v-if="loading" class="d-flex justify-content-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement…</span>
              </div>
            </div>
            <div v-else-if="loadError" class="alert alert-danger mb-0">{{ loadError }}</div>
            <div v-else-if="!blockGroups.length" class="text-muted">Aucune compétence dans ce référentiel.</div>
            <div v-else class="ref-explorer-blocks">
              <details
                v-for="(group, gIdx) in blockGroups"
                :key="`${group.block_code}-${group.block_label}-${gIdx}`"
                class="border rounded mb-2"
                :open="gIdx === 0"
              >
                <summary class="px-3 py-2 bg-light rounded-top user-select-none" style="cursor: pointer;">
                  <span class="fw-semibold">
                    <template v-if="group.block_code || group.block_label">
                      <span v-if="group.block_label">{{ group.block_label }}</span>
                      <code v-if="group.block_code" class="ms-1 small">{{ group.block_code }}</code>
                      <span v-if="!group.block_label && group.block_code" class="ms-1">{{ group.block_code }}</span>
                    </template>
                    <template v-else>Bloc non renseigné</template>
                  </span>
                  <span class="badge bg-secondary ms-2">{{ group.items.length }}</span>
                </summary>
                <div class="p-2 pt-0">
                  <div
                    v-for="row in group.items"
                    :key="row.id"
                    class="card mb-3 border-light shadow-sm"
                  >
                    <div class="card-body py-3">
                      <div class="d-flex flex-wrap justify-content-between gap-2 mb-2">
                        <div>
                          <code class="small text-muted">{{ row.code }}</code>
                          <div class="fw-medium">{{ row.title }}</div>
                        </div>
                      </div>

                      <div v-if="row.tasks?.length" class="mb-3">
                        <div class="text-secondary small text-uppercase mb-1">Tâches liées</div>
                        <ul class="list-unstyled small mb-0">
                          <li v-for="(t, ti) in row.tasks" :key="`${row.id}-t-${ti}`" class="mb-1">
                            <span class="text-muted">{{ t.activity_code }}</span>
                            <span v-if="t.activity_label" class="text-muted"> — {{ t.activity_label }}</span>
                            <br />
                            <code>{{ t.code }}</code> — {{ t.label }}
                          </li>
                        </ul>
                      </div>

                      <div v-if="sortedCriteria(row).length">
                        <div class="text-secondary small text-uppercase mb-1">Critères</div>
                        <ul class="list-unstyled small mb-0">
                          <li
                            v-for="c in sortedCriteria(row)"
                            :key="c.id"
                            class="mb-2 border-start border-3 border-primary ps-2"
                          >
                            <div>
                              <code class="small">{{ c.code }}</code>
                              <span v-if="c.is_active === false" class="badge bg-light text-muted ms-1">inactif</span>
                            </div>
                            <div>{{ c.label }}</div>
                          </li>
                        </ul>
                      </div>
                      <p
                        v-if="!row.tasks?.length && !sortedCriteria(row).length"
                        class="small text-muted mb-0"
                      >
                        Aucune tâche ni critère structuré pour cette compétence.
                      </p>
                    </div>
                  </div>
                </div>
              </details>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="close">Fermer</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" @click="close"></div>
  </div>
</template>
