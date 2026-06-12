<script setup lang="ts">
import { ref } from 'vue'

const staff = ref([
  { id: 's1', name: 'Sarah Chen', email: 'sarah.chen@northwind-legal.local', role: 'attorney', areas: ['govt-surveillance', 'privacy'], activeCaseload: 42 },
  { id: 's2', name: 'Marcus Johnson', email: 'marcus.j@northwind-legal.local', role: 'attorney', areas: ['police-misconduct', 'discrimination'], activeCaseload: 31 },
  { id: 's3', name: 'Priya Patel', email: 'priya.p@northwind-legal.local', role: 'staff', areas: ['immigration', 'housing'], activeCaseload: 28 },
  { id: 's4', name: 'James Torres', email: 'james.t@northwind-legal.local', role: 'staff', areas: ['free-speech', 'voting'], activeCaseload: 24 },
  { id: 's5', name: 'Kim Brooks', email: 'kim.b@northwind-legal.local', role: 'admin', areas: [], activeCaseload: 18 },
  { id: 's6', name: 'Alex Rivera', email: 'alex.r@northwind-legal.local', role: 'volunteer', areas: ['govt-surveillance'], activeCaseload: 8 },
  { id: 's7', name: 'Dana Kim', email: 'dana.k@northwind-legal.local', role: 'volunteer', areas: ['police-misconduct'], activeCaseload: 5 },
])

const roleColors: Record<string, string> = {
  attorney: 'badge-critical',
  staff: 'badge-assigned',
  admin: 'badge-in_progress',
  volunteer: 'badge-reviewed',
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Staff</h2>
      <button class="btn btn-primary">+ Add Staff</button>
    </div>

    <div class="card" style="padding: 0; overflow: hidden;">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Areas</th>
            <th>Active Cases</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td style="font-weight: 600;">{{ s.name }}</td>
            <td style="font-size: 0.82rem; color: var(--text-muted);">{{ s.email }}</td>
            <td><span :class="'badge ' + (roleColors[s.role] || '')">{{ s.role }}</span></td>
            <td>
              <div style="display: flex; gap: 0.25rem; flex-wrap: wrap;">
                <span v-for="a in s.areas" :key="a" class="badge" style="background: var(--paper); color: var(--text-secondary);">{{ a }}</span>
              </div>
            </td>
            <td>
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-weight: 600;">{{ s.activeCaseload }}</span>
                <div style="flex: 1; max-width: 80px; background: var(--border); border-radius: 3px; height: 6px; overflow: hidden;">
                  <div :style="{ width: Math.min(100, (s.activeCaseload / 50) * 100) + '%', height: '100%', background: s.activeCaseload > 35 ? 'var(--accent)' : 'var(--navy)', borderRadius: '3px' }"></div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
