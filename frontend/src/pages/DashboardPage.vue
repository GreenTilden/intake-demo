<script setup lang="ts">
import { ref } from 'vue'

// Mock data for demo (replace with API calls when backend is connected)
const stats = ref({
  total: 2847,
  openQueue: 143,
  last30Days: 623,
  last7Days: 156,
  avgResolutionDays: 4.2,
  byStatus: { new: 47, reviewed: 31, assigned: 38, in_progress: 27, resolved: 512, closed: 2192 },
  bySource: { letter: 1139, web: 1424, email: 171, phone: 113 },
  byCategory: {
    'govt-surveillance': 891,
    'police-misconduct': 412,
    'discrimination': 387,
    'privacy': 298,
    'free-speech': 245,
    'housing': 201,
    'immigration': 178,
    'voting': 112,
    'other': 123,
  },
  caseloads: { 'Sarah Chen': 42, 'Marcus Johnson': 31, 'Priya Patel': 28, 'James Torres': 24, 'Kim Brooks': 18 },
})

const categoryLabels: Record<string, string> = {
  'govt-surveillance': 'Govt Surveillance',
  'police-misconduct': 'Police Misconduct',
  'discrimination': 'Discrimination',
  'privacy': 'Privacy / Data',
  'free-speech': 'Free Speech',
  'housing': 'Housing',
  'immigration': 'Immigration',
  'voting': 'Voting Rights',
  'other': 'Other',
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Dashboard</h2>
      <div style="display: flex; gap: 0.5rem;">
        <RouterLink to="/intakes/scan" class="btn btn-accent">Scan Letter</RouterLink>
        <RouterLink to="/intakes/new" class="btn btn-primary">+ New Intake</RouterLink>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card accent">
        <div class="stat-value">{{ stats.openQueue }}</div>
        <div class="stat-label">Open Queue</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.last7Days }}</div>
        <div class="stat-label">This Week</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.last30Days }}</div>
        <div class="stat-label">Last 30 Days</div>
      </div>
      <div class="stat-card green">
        <div class="stat-value">{{ stats.avgResolutionDays }}d</div>
        <div class="stat-label">Avg Resolution</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total.toLocaleString() }}</div>
        <div class="stat-label">Total All Time</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
      <!-- By Status -->
      <div class="card">
        <div class="card-header">Pipeline Status</div>
        <table>
          <tbody>
            <tr v-for="(count, status) in stats.byStatus" :key="status">
              <td><span :class="'badge badge-' + status">{{ String(status).replace('_', ' ') }}</span></td>
              <td style="text-align: right; font-weight: 600;">{{ count }}</td>
              <td style="width: 50%;">
                <div style="background: var(--border); border-radius: 3px; height: 8px; overflow: hidden;">
                  <div :style="{ width: Math.min(100, (count / stats.total) * 100 * 5) + '%', height: '100%', background: 'var(--navy)', borderRadius: '3px' }"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- By Source -->
      <div class="card">
        <div class="card-header">Intake Source</div>
        <table>
          <tbody>
            <tr v-for="(count, source) in stats.bySource" :key="source">
              <td><span :class="'badge badge-' + source">{{ source }}</span></td>
              <td style="text-align: right; font-weight: 600;">{{ count }}</td>
              <td style="width: 50%;">
                <div style="background: var(--border); border-radius: 3px; height: 8px; overflow: hidden;">
                  <div :style="{ width: (count / stats.total) * 100 + '%', height: '100%', background: source === 'letter' ? '#805ad5' : 'var(--green-light)', borderRadius: '3px' }"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- By Category -->
      <div class="card">
        <div class="card-header">Top Categories</div>
        <table>
          <tbody>
            <tr v-for="(count, cat) in stats.byCategory" :key="cat">
              <td style="font-size: 0.82rem;">{{ categoryLabels[cat as string] || cat }}</td>
              <td style="text-align: right; font-weight: 600;">{{ count }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Staff Caseloads -->
      <div class="card">
        <div class="card-header">Staff Caseloads (Active)</div>
        <table>
          <tbody>
            <tr v-for="(count, name) in stats.caseloads" :key="name">
              <td>{{ name }}</td>
              <td style="text-align: right; font-weight: 600;">{{ count }}</td>
              <td style="width: 40%;">
                <div style="background: var(--border); border-radius: 3px; height: 8px; overflow: hidden;">
                  <div :style="{ width: (count / 50) * 100 + '%', height: '100%', background: count > 35 ? 'var(--accent)' : 'var(--navy)', borderRadius: '3px' }"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
