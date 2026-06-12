<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  firstName: '',
  lastName: '',
  phone: '',
  email: '',
  preferredContact: 'phone',
  address: '',
  state: '',
  source: 'web',
  category: '',
  urgency: 'normal',
  description: '',
})

const saving = ref(false)

async function submit() {
  if (!form.value.firstName || !form.value.lastName || !form.value.description) {
    alert('First name, last name, and description are required.')
    return
  }
  saving.value = true
  // In production: apiFetch('/intakes', { method: 'POST', body: JSON.stringify(form.value) })
  // For demo, just simulate
  setTimeout(() => {
    saving.value = false
    alert('Intake created! (Demo mode — backend not connected)')
    router.push('/intakes')
  }, 500)
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>New Intake</h2>
    </div>

    <form @submit.prevent="submit">
      <div class="card">
        <div class="card-header">Complainant Information</div>
        <div class="form-row">
          <div class="form-group">
            <label>First Name *</label>
            <input v-model="form.firstName" required />
          </div>
          <div class="form-group">
            <label>Last Name *</label>
            <input v-model="form.lastName" required />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Phone</label>
            <input v-model="form.phone" type="tel" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Preferred Contact</label>
            <select v-model="form.preferredContact">
              <option value="phone">Phone</option>
              <option value="email">Email</option>
              <option value="mail">Mail</option>
            </select>
          </div>
          <div class="form-group">
            <label>State</label>
            <input v-model="form.state" maxlength="2" placeholder="IN" />
          </div>
        </div>
        <div class="form-group">
          <label>Address</label>
          <input v-model="form.address" />
        </div>
      </div>

      <div class="card">
        <div class="card-header">Intake Details</div>
        <div class="form-row">
          <div class="form-group">
            <label>Source</label>
            <select v-model="form.source">
              <option value="web">Web Form</option>
              <option value="letter">Letter</option>
              <option value="email">Email</option>
              <option value="phone">Phone Call</option>
              <option value="walk_in">Walk-In</option>
            </select>
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="form.category">
              <option value="">Select...</option>
              <option value="govt-surveillance">Government Surveillance / Gangstalking</option>
              <option value="police-misconduct">Police Misconduct</option>
              <option value="discrimination">Discrimination</option>
              <option value="immigration">Immigration</option>
              <option value="free-speech">Free Speech / First Amendment</option>
              <option value="privacy">Privacy / Data Rights</option>
              <option value="housing">Housing Discrimination</option>
              <option value="voting">Voting Rights</option>
              <option value="prisoners">Prisoners' Rights</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Urgency</label>
          <select v-model="form.urgency">
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div class="form-group">
          <label>Description *</label>
          <textarea v-model="form.description" rows="6" placeholder="Describe the complaint, incident details, and any relevant context..." required></textarea>
        </div>
      </div>

      <div style="display: flex; gap: 0.75rem; margin-top: 1rem;">
        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner"></span>
          {{ saving ? 'Saving...' : 'Create Intake' }}
        </button>
        <RouterLink to="/intakes" class="btn btn-outline">Cancel</RouterLink>
      </div>
    </form>
  </div>
</template>
