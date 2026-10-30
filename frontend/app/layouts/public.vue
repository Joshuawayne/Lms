<!--
  Public website layout — used by homepage, programs and application pages.
  Renders the official Jjenga Code retro vector wordmark, accessible navigation,
  mobile menu drawer, and verified footer contact details.
-->
<script setup lang="ts">
/**
 * Mobile navigation state. Automatically closed on route change.
 */
const mobileOpen = ref(false)
const route = useRoute()

watch(() => route.path, () => {
  mobileOpen.value = false
})

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Programs', to: '/programs' },
  { label: 'How Learning Works', to: '/#how-learning-works' },
  { label: 'Why Jjenga', to: '/#parents' },
  { label: 'FAQ', to: '/#faq' },
  { label: 'Contact', to: '/#contact' },
] as const
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white text-navy-900 selection:bg-pink-100 selection:text-navy-950">
    <!-- ── site header ──────────────────────────────────────────────── -->
    <header class="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-navy-100/80 transition-shadow duration-200">
      <nav class="max-w-7xl mx-auto flex items-center justify-between px-5 py-3.5 lg:px-8" aria-label="Main Navigation">
        <!-- Logo / brand -->
        <NuxtLink to="/" class="flex items-center group focus-visible:outline-2 focus-visible:outline-purple-600 rounded" aria-label="Jjenga Code home">
          <img
            class="brand-logo transition-transform duration-200 group-hover:scale-[1.02]"
            src="/brand/jenga-code-gradient.svg"
            alt="Jjenga Code"
            width="280"
            height="40"
          >
        </NuxtLink>

        <!-- Desktop navigation -->
        <div class="hidden lg:flex items-center gap-7">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="text-sm font-medium text-navy-700 hover:text-purple-600 transition-colors duration-150 py-1"
            active-class="!text-purple-600 font-semibold"
          >
            {{ link.label }}
          </NuxtLink>
          <NuxtLink to="/programs" class="ml-2">
            <UButton
              color="primary"
              size="md"
              class="bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-full px-6 shadow-sm hover:shadow transition-all"
            >
              Explore programs
            </UButton>
          </NuxtLink>
        </div>

        <!-- Mobile hamburger -->
        <button
          class="lg:hidden p-2 rounded-lg hover:bg-navy-50 text-navy-700 transition-colors focus-visible:outline-2 focus-visible:outline-purple-600"
          :aria-expanded="mobileOpen"
          aria-label="Toggle navigation menu"
          @click="mobileOpen = !mobileOpen"
        >
          <UIcon :name="mobileOpen ? 'i-lucide-x' : 'i-lucide-menu'" class="w-6 h-6" />
        </button>
      </nav>

      <!-- Mobile menu drawer -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-200 ease-in"
        enter-from-class="opacity-0 -translate-y-2"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="mobileOpen" class="lg:hidden border-t border-navy-100 bg-white px-5 pb-6 pt-3 shadow-lg">
          <div class="space-y-1">
            <NuxtLink
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to"
              class="block py-2.5 px-3 rounded-lg text-base font-medium text-navy-800 hover:bg-navy-50 hover:text-purple-600 transition-colors"
              active-class="!text-purple-600 !bg-purple-50 font-semibold"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
          <div class="mt-4 pt-3 border-t border-navy-100">
            <NuxtLink to="/programs" class="block">
              <UButton color="primary" block class="bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-full py-2.5">
                Explore programs
              </UButton>
            </NuxtLink>
          </div>
        </div>
      </Transition>
    </header>

    <!-- ── page content ─────────────────────────────────────────────── -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- ── site footer ──────────────────────────────────────────────── -->
    <footer id="contact" class="bg-navy-950 text-navy-200 border-t border-navy-800/60">
      <WaveDivider color="var(--color-navy-950)" />

      <div class="max-w-7xl mx-auto px-5 lg:px-8 py-16">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10 lg:gap-12">
          <!-- Brand & philosophy column -->
          <div class="lg:col-span-5 space-y-4">
            <NuxtLink to="/" class="inline-block" aria-label="Jjenga Code home">
              <img
                class="brand-logo brightness-105"
                src="/brand/jenga-code-white.svg"
                alt="Jjenga Code"
                width="280"
                height="40"
              >
            </NuxtLink>
            <p class="text-base font-medium text-yellow-400 font-heading">
              Raise a builder, not just a user.
            </p>
            <p class="text-sm text-navy-300 max-w-sm leading-relaxed">
              Hands-on coding and robotics where children ask questions, test ideas, and build something of their own.
            </p>
            <p class="text-xs text-navy-400 border-l-2 border-yellow-400/60 pl-3 py-1">
              Submission confirms receipt. Enrolment is confirmed following administrator review.
            </p>
          </div>

          <!-- Quick pathways -->
          <div class="lg:col-span-3 space-y-3">
            <h3 class="text-xs font-semibold text-white uppercase tracking-wider">Learning Pathways</h3>
            <ul class="space-y-2.5 text-sm">
              <li>
                <NuxtLink to="/programs?pathway=school_term" class="text-navy-300 hover:text-yellow-400 transition-colors">
                  School-Term Programs
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/programs?pathway=saturday_club" class="text-navy-300 hover:text-yellow-400 transition-colors">
                  Saturday Coding Club
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/programs?pathway=holiday" class="text-navy-300 hover:text-yellow-400 transition-colors">
                  Holiday Programs &amp; Camps
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/programs" class="text-navy-300 hover:text-yellow-400 transition-colors">
                  All Published Programs
                </NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Verified campaign contact details -->
          <div class="lg:col-span-4 space-y-3">
            <h3 class="text-xs font-semibold text-white uppercase tracking-wider">Contact &amp; Venues</h3>
            <ul class="space-y-3 text-sm text-navy-300">
              <li class="flex items-start gap-3">
                <UIcon name="i-lucide-mail" class="w-4 h-4 text-yellow-400 mt-1 shrink-0" />
                <div>
                  <span class="block text-xs text-navy-400">Email</span>
                  <a href="mailto:hello@jengacode.tech" class="text-white hover:text-yellow-400 transition-colors font-medium">
                    hello@jengacode.tech
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-lucide-phone" class="w-4 h-4 text-yellow-400 mt-1 shrink-0" />
                <div>
                  <span class="block text-xs text-navy-400">Phone</span>
                  <a href="tel:+254792696592" class="text-white hover:text-yellow-400 transition-colors font-medium">
                    +254 792 696 592
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-lucide-map-pin" class="w-4 h-4 text-pink-400 mt-1 shrink-0" />
                <div>
                  <span class="block text-xs text-navy-400">Camp Venue (November 2026)</span>
                  <span class="text-white">Maktaba Kuu, Upper Hill, Nairobi</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Bottom bar -->
        <div class="mt-12 pt-6 border-t border-navy-800 text-center sm:flex sm:justify-between sm:items-center text-xs text-navy-400">
          <p>© {{ new Date().getFullYear() }} Jjenga Code. All rights reserved.</p>
          <p class="mt-2 sm:mt-0 text-navy-500">
            Stock photography used for illustrative purposes only.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>
