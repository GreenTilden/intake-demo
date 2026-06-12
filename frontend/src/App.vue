<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'

// A fun little "verify you're human" gate on load. (The demo is ALSO basic-auth
// gated at the edge — this is flavor that fits the secure-intake theme.) Uses
// Cloudflare Turnstile's always-pass TEST sitekey, so it needs no account setup;
// swap SITEKEY below for a real Turnstile sitekey for actual bot protection.
const SITEKEY = '1x00000000000000000000AA'
const verified = ref(sessionStorage.getItem('nw_verified') === '1')
function pass() {
  verified.value = true
  sessionStorage.setItem('nw_verified', '1')
}
onMounted(() => {
  if (verified.value) return
  let tries = 0
  const tick = () => {
    const ts = (window as any).turnstile
    const el = document.querySelector('.cf-turnstile')
    if (ts && el) {
      ts.render(el, { sitekey: SITEKEY, callback: pass, theme: 'light' })
      return
    }
    // fail-open after ~4s so a demo visitor is never trapped by a slow widget
    if (++tries > 20) { pass(); return }
    setTimeout(tick, 200)
  }
  tick()
})
</script>

<template>
  <div v-if="!verified" class="ts-gate">
    <div class="ts-card">
      <svg viewBox="0 0 800 800" class="ts-mark" aria-hidden="true">
        <line x1="194" y1="400" x2="655.31" y2="400" stroke="#1f6feb" stroke-width="46" stroke-linecap="round"/>
        <line x1="400" y1="116" x2="400" y2="684" stroke="#1f6feb" stroke-width="46" stroke-linecap="round"/>
        <line x1="400" y1="116" x2="131.17" y2="486.61" stroke="#1f6feb" stroke-width="46" stroke-linecap="round"/>
      </svg>
      <h2>Northwind Legal — Intake</h2>
      <p class="ts-sub">Quick check before you come in.</p>
      <div class="cf-turnstile"></div>
      <p class="ts-foot">Demo environment · synthetic data only</p>
    </div>
  </div>

  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <h1>Northwind Legal Group</h1>
        <p>Litigation Support</p>
      </div>
      <nav>
        <RouterLink to="/">
          <span class="nav-icon">&#9632;</span> Dashboard
        </RouterLink>
        <RouterLink to="/intakes">
          <span class="nav-icon">&#9776;</span> All Intakes
        </RouterLink>
        <RouterLink to="/intakes/new">
          <span class="nav-icon">&#43;</span> New Intake
        </RouterLink>
        <RouterLink to="/intakes/scan">
          <span class="nav-icon">&#128196;</span> Scan Letter
        </RouterLink>
        <RouterLink to="/staff">
          <span class="nav-icon">&#9679;</span> Staff
        </RouterLink>
      </nav>
      <div class="sidebar-footer">
        <a href="https://darn-tech.com" target="_blank" rel="noopener" class="darntech-mark" aria-label="Built by DArnTech">
          <svg viewBox="0 0 800 800" class="darntech-mark-svg" aria-hidden="true">
            <line x1="194" y1="400" x2="655.31" y2="400" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
            <line x1="400" y1="116" x2="400" y2="684" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
            <line x1="400" y1="116" x2="131.17" y2="486.61" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
            <line x1="400" y1="684" x2="726.85" y2="320.43" stroke="currentColor" stroke-width="40" stroke-linecap="round"/>
          </svg>
          <span class="darntech-mark-text">
            <span class="darntech-mark-built">Built by</span>
            <span class="darntech-mark-name">DArnTech</span>
          </span>
        </a>
        <p class="sidebar-footer-note">Pro bono engagement</p>
      </div>
    </aside>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.ts-gate {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(120% 90% at 50% -10%, #1b2430 0%, #0e141b 60%);
  z-index: 9999;
}
.ts-card {
  background: #fff;
  border-radius: 16px;
  padding: 36px 40px;
  text-align: center;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
  max-width: 380px;
  width: 90%;
}
.ts-mark { width: 42px; height: 42px; margin-bottom: 10px; }
.ts-card h2 { margin: 0 0 4px; font-size: 20px; color: #1a2230; }
.ts-sub { margin: 0 0 20px; color: #5b6472; font-size: 14px; }
.ts-card .cf-turnstile { display: flex; justify-content: center; min-height: 65px; }
.ts-foot { margin: 18px 0 0; color: #98a0ad; font-size: 12px; }
</style>
