<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const file = ref<File | null>(null)
const dragover = ref(false)
const scanning = ref(false)
const ocrText = ref('')
const ocrDone = ref(false)

function onDrop(e: DragEvent) {
  dragover.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) handleFile(f)
}

function onFileSelect(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) handleFile(f)
}

function handleFile(f: File) {
  const valid = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']
  const ext = f.name.toLowerCase().slice(f.name.lastIndexOf('.'))
  if (!valid.includes(ext)) {
    alert(`Unsupported file type: ${ext}\nSupported: PDF, JPG, PNG, TIFF`)
    return
  }
  file.value = f
  ocrText.value = ''
  ocrDone.value = false
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function scan() {
  if (!file.value) return
  scanning.value = true

  // In production: apiUpload('/intakes/scan', file.value, { category: 'govt-surveillance' })
  // For demo, simulate OCR
  setTimeout(() => {
    ocrText.value = `March 15, 2026

To Whom It May Concern,

I am writing to report what I believe to be ongoing government surveillance
of my person and property. Since approximately January 2026, I have
noticed the following:

1. Unmarked vehicles parked outside my residence at 412 Quillhaven Court,
   Lakemont, IN for extended periods (photographs enclosed)
2. Unusual interference with my phone calls and internet service
3. Individuals appearing to follow me to and from work

I have documented these incidents with dates and photographs which I am
including with this letter. I am requesting Northwind Legal Group's assistance in
investigating whether my civil rights are being violated.

Sincerely,
Davood J. Bowee
412 Quillhaven Court
Lakemont, IN 47000
(555) 555-0173`
    scanning.value = false
    ocrDone.value = true
  }, 2000)
}

function createIntake() {
  // In production, the /intakes/scan endpoint already creates the intake
  // This would navigate to the edit page for the newly created intake
  alert('Intake created from scanned letter! (Demo mode)')
  router.push('/intakes')
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Scan Letter</h2>
    </div>

    <div class="card">
      <div class="card-header">Upload Scanned Document</div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
        Upload a scanned letter, PDF, or photograph. The system will extract the text automatically using OCR.
        You can then review, correct, and submit as an intake.
      </p>

      <!-- Drop Zone -->
      <div
        v-if="!file"
        class="drop-zone"
        :class="{ dragover }"
        @dragover.prevent="dragover = true"
        @dragleave="dragover = false"
        @drop.prevent="onDrop"
        @click="($refs.fileInput as HTMLInputElement).click()"
      >
        <div class="drop-icon">&#128196;</div>
        <p><strong>Drop a scanned letter here</strong> or click to browse</p>
        <p class="drop-hint">PDF, JPG, PNG, or TIFF &mdash; up to 20MB</p>
      </div>
      <input ref="fileInput" type="file" accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif" style="display: none;" @change="onFileSelect" />

      <!-- File Selected -->
      <div v-if="file && !ocrDone" class="card" style="margin-top: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div>
          <strong>{{ file.name }}</strong>
          <span style="color: var(--text-muted); margin-left: 0.5rem;">{{ formatSize(file.size) }}</span>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-primary" @click="scan" :disabled="scanning">
            <span v-if="scanning" class="spinner"></span>
            {{ scanning ? 'Extracting text...' : 'Run OCR' }}
          </button>
          <button class="btn btn-outline" @click="file = null">Remove</button>
        </div>
      </div>
    </div>

    <!-- OCR Result -->
    <div v-if="ocrDone" class="card">
      <div class="card-header">Extracted Text</div>
      <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.75rem;">
        Review the extracted text below. You can edit it before creating the intake.
      </p>

      <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="badge badge-letter">Letter</span>
        <span style="font-size: 0.82rem; color: var(--text-secondary);">{{ file?.name }} &mdash; {{ formatSize(file?.size || 0) }}</span>
      </div>

      <textarea
        v-model="ocrText"
        class="ocr-result"
        style="width: 100%; min-height: 300px; font-family: 'Courier New', monospace; font-size: 0.85rem; border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;"
      ></textarea>

      <div style="display: flex; gap: 0.75rem; margin-top: 1rem;">
        <button class="btn btn-primary" @click="createIntake">Create Intake from Letter</button>
        <button class="btn btn-outline" @click="file = null; ocrDone = false; ocrText = ''">Start Over</button>
      </div>
    </div>
  </div>
</template>
