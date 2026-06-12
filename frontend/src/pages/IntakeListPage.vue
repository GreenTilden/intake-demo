<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const filter = ref({ status: '', category: '', source: '', search: '' })

// Mock data for demo
const intakes = ref([
  { id: '1', firstName: 'Davood', lastName: 'Bowee', source: 'letter', category: 'govt-surveillance', categoryLabel: 'Govt Surveillance', status: 'new', urgency: 'high', assignedName: null, createdAt: '2026-03-31T09:15:00Z' },
  { id: '2', firstName: 'Adelle', lastName: 'Atkins', source: 'web', category: 'police-misconduct', categoryLabel: 'Police Misconduct', status: 'assigned', urgency: 'critical', assignedName: 'Teena Fay', createdAt: '2026-03-30T14:22:00Z' },
  { id: '3', firstName: 'Eltun', lastName: 'Jorn', source: 'letter', category: 'govt-surveillance', categoryLabel: 'Govt Surveillance', status: 'reviewed', urgency: 'normal', assignedName: null, createdAt: '2026-03-30T11:05:00Z' },
  { id: '4', firstName: 'Doea', lastName: 'Leepa', source: 'email', category: 'privacy', categoryLabel: 'Privacy / Data', status: 'in_progress', urgency: 'normal', assignedName: 'Stove Martin', createdAt: '2026-03-29T16:45:00Z' },
  { id: '5', firstName: 'Freddy', lastName: 'Mercry', source: 'phone', category: 'discrimination', categoryLabel: 'Discrimination', status: 'assigned', urgency: 'high', assignedName: 'Maya Rudd', createdAt: '2026-03-29T10:30:00Z' },
  { id: '6', firstName: 'Beyawnce', lastName: 'Knolls', source: 'letter', category: 'free-speech', categoryLabel: 'Free Speech', status: 'new', urgency: 'normal', assignedName: null, createdAt: '2026-03-28T15:00:00Z' },
  { id: '7', firstName: 'Mick', lastName: 'Jaggar', source: 'web', category: 'govt-surveillance', categoryLabel: 'Govt Surveillance', status: 'resolved', urgency: 'low', assignedName: 'Aleck Baldween', createdAt: '2026-03-27T09:00:00Z' },
  { id: '8', firstName: 'Whitny', lastName: 'Hewston', source: 'letter', category: 'housing', categoryLabel: 'Housing', status: 'new', urgency: 'high', assignedName: null, createdAt: '2026-03-27T08:20:00Z' },
])

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>All Intakes</h2>
      <div style="display: flex; gap: 0.5rem;">
        <RouterLink to="/intakes/scan" class="btn btn-accent">Scan Letter</RouterLink>
        <RouterLink to="/intakes/new" class="btn btn-primary">+ New Intake</RouterLink>
      </div>
    </div>

    <!-- Filters -->
    <div class="card" style="margin-bottom: 1rem;">
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: end;">
        <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 200px;">
          <label>Search</label>
          <input v-model="filter.search" placeholder="Name or description..." />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Status</label>
          <select v-model="filter.status">
            <option value="">All</option>
            <option value="new">New</option>
            <option value="reviewed">Reviewed</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Source</label>
          <select v-model="filter.source">
            <option value="">All</option>
            <option value="letter">Letter</option>
            <option value="web">Web</option>
            <option value="email">Email</option>
            <option value="phone">Phone</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="card" style="padding: 0; overflow: hidden;">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Source</th>
            <th>Category</th>
            <th>Status</th>
            <th>Urgency</th>
            <th>Assigned</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in intakes" :key="i.id" style="cursor: pointer;" @click="$router.push(`/intakes/${i.id}`)">
            <td style="font-weight: 600;">{{ i.lastName }}, {{ i.firstName }}</td>
            <td><span :class="'badge badge-' + i.source">{{ i.source }}</span></td>
            <td style="font-size: 0.82rem;">{{ i.categoryLabel }}</td>
            <td><span :class="'badge badge-' + i.status">{{ i.status.replace('_', ' ') }}</span></td>
            <td><span :class="'badge badge-' + i.urgency">{{ i.urgency }}</span></td>
            <td style="font-size: 0.82rem; color: var(--text-muted);">{{ i.assignedName || '—' }}</td>
            <td style="font-size: 0.82rem; color: var(--text-muted);">{{ fmtDate(i.createdAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
