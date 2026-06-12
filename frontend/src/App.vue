<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
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
        <a href="https://darntech.com" target="_blank" rel="noopener" class="darntech-mark" aria-label="Built by DArnTech">
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
