<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Mock data for demo
const intake = ref({
  id: route.params.id,
  firstName: 'Robert',
  lastName: 'Williams',
  phone: '(317) 555-0142',
  email: '',
  preferredContact: 'phone',
  address: '4215 Maple Street, Indianapolis, IN 46205',
  state: 'IN',
  source: 'letter',
  category: 'govt-surveillance',
  categoryLabel: 'Government Surveillance / Gangstalking',
  description: `I am writing to report what I believe to be ongoing government surveillance of my person and property. Since approximately January 2026, I have noticed the following:\n\n1. Unmarked vehicles parked outside my residence at 4215 Maple Street, Indianapolis, IN for extended periods (photographs enclosed)\n2. Unusual interference with my phone calls and internet service\n3. Individuals appearing to follow me to and from work\n\nI have documented these incidents with dates and photographs which I am including with this letter. I am requesting the Northwind Legal's assistance in investigating whether my civil rights are being violated.`,
  urgency: 'high',
  status: 'new',
  assignedTo: null,
  assignedName: null,
  resolution: '',
  createdAt: '2026-03-31T09:15:00Z',
  updatedAt: '2026-03-31T09:15:00Z',
  notes: [
    { id: '1', text: 'Letter received via USPS. Scanned and OCR processed. Text quality good.', author: 'Kim Brooks', createdAt: '2026-03-31T09:20:00Z' },
  ],
  attachments: [
    { id: '1', filename: 'williams_letter_20260331.pdf', sizeBytes: 847293, ocrStatus: 'complete', createdAt: '2026-03-31T09:15:00Z' },
    { id: '2', filename: 'photo_vehicle_1.jpg', sizeBytes: 2145000, ocrStatus: 'skipped', createdAt: '2026-03-31T09:16:00Z' },
  ],
})

const newNote = ref('')
const staffList = [
  { id: 's1', name: 'Sarah Chen' },
  { id: 's2', name: 'Marcus Johnson' },
  { id: 's3', name: 'Priya Patel' },
  { id: 's4', name: 'James Torres' },
  { id: 's5', name: 'Kim Brooks' },
]

function addNote() {
  if (!newNote.value.trim()) return
  intake.value.notes.push({
    id: String(Date.now()),
    text: newNote.value,
    author: 'You',
    createdAt: new Date().toISOString(),
  })
  newNote.value = ''
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function fmtSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>{{ intake.lastName }}, {{ intake.firstName }}</h2>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <span :class="'badge badge-' + intake.source">{{ intake.source }}</span>
        <span :class="'badge badge-' + intake.status">{{ intake.status.replace('_', ' ') }}</span>
        <span :class="'badge badge-' + intake.urgency">{{ intake.urgency }}</span>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem;">
      <!-- Main Content -->
      <div>
        <!-- Description -->
        <div class="card">
          <div class="card-header">Description</div>
          <p style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.7;">{{ intake.description }}</p>
        </div>

        <!-- Notes -->
        <div class="card">
          <div class="card-header">Notes ({{ intake.notes.length }})</div>
          <div v-for="note in intake.notes" :key="note.id" style="padding: 0.75rem 0; border-bottom: 1px solid var(--border);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
              <strong style="font-size: 0.82rem;">{{ note.author }}</strong>
              <span style="font-size: 0.75rem; color: var(--text-muted);">{{ fmtDate(note.createdAt) }}</span>
            </div>
            <p style="font-size: 0.88rem; margin: 0;">{{ note.text }}</p>
          </div>

          <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
            <input v-model="newNote" placeholder="Add a note..." @keyup.enter="addNote" style="flex: 1; padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: var(--radius); font-size: 0.88rem;" />
            <button class="btn btn-primary btn-sm" @click="addNote">Add</button>
          </div>
        </div>

        <!-- Attachments -->
        <div class="card">
          <div class="card-header">Attachments ({{ intake.attachments.length }})</div>
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Size</th>
                <th>OCR</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in intake.attachments" :key="a.id">
                <td style="font-weight: 500;">{{ a.filename }}</td>
                <td>{{ fmtSize(a.sizeBytes) }}</td>
                <td><span :class="'badge badge-' + (a.ocrStatus === 'complete' ? 'in_progress' : 'closed')">{{ a.ocrStatus }}</span></td>
                <td style="font-size: 0.82rem; color: var(--text-muted);">{{ fmtDate(a.createdAt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Sidebar -->
      <div>
        <!-- Contact Info -->
        <div class="card">
          <div class="card-header">Contact Information</div>
          <div style="font-size: 0.88rem;">
            <p v-if="intake.phone"><strong>Phone:</strong> {{ intake.phone }}</p>
            <p v-if="intake.email"><strong>Email:</strong> {{ intake.email }}</p>
            <p v-if="intake.address"><strong>Address:</strong> {{ intake.address }}</p>
            <p><strong>Preferred:</strong> {{ intake.preferredContact }}</p>
          </div>
        </div>

        <!-- Workflow -->
        <div class="card">
          <div class="card-header">Workflow</div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="intake.status">
              <option value="new">New</option>
              <option value="reviewed">Reviewed</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div class="form-group">
            <label>Assign To</label>
            <select v-model="intake.assignedTo">
              <option :value="null">Unassigned</option>
              <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Urgency</label>
            <select v-model="intake.urgency">
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="intake.category">
              <option value="govt-surveillance">Govt Surveillance</option>
              <option value="police-misconduct">Police Misconduct</option>
              <option value="discrimination">Discrimination</option>
              <option value="privacy">Privacy / Data</option>
              <option value="free-speech">Free Speech</option>
              <option value="housing">Housing</option>
              <option value="immigration">Immigration</option>
              <option value="voting">Voting Rights</option>
              <option value="other">Other</option>
            </select>
          </div>
          <button class="btn btn-primary" style="width: 100%;">Save Changes</button>
        </div>

        <!-- Meta -->
        <div class="card">
          <div class="card-header">Meta</div>
          <div style="font-size: 0.82rem; color: var(--text-muted);">
            <p><strong>Created:</strong> {{ fmtDate(intake.createdAt) }}</p>
            <p><strong>Updated:</strong> {{ fmtDate(intake.updatedAt) }}</p>
            <p><strong>ID:</strong> {{ intake.id }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
