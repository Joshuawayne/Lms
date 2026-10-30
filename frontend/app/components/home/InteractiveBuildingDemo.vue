<!--
  Interactive Building Demonstration — "A Small Act of Building"

  Provides children and parents with an immediate, tangible taste of the Jjenga Code experience:
  - Child layer: Hands-on command sequencing for a retro mini-robot with instant visual response.
  - Parent layer: Concrete explanation of computational thinking, debugging, and spatial logic.
  - Accessibility: Full keyboard support, ARIA live region for screen readers, prefers-reduced-motion respected.
-->
<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'

export interface BotCommand {
  id: string
  name: string
  action: 'forward' | 'turn_right' | 'turn_left' | 'beep' | 'light_led'
  color: string
  icon: string
  desc: string
}

const AVAILABLE_COMMANDS: BotCommand[] = [
  { id: 'fwd', name: 'Step Forward', action: 'forward', color: 'bg-purple-600 hover:bg-purple-700 text-white', icon: 'i-lucide-arrow-up', desc: 'Moves robot 1 grid unit ahead' },
  { id: 'right', name: 'Turn Right', action: 'turn_right', color: 'bg-pink-500 hover:bg-pink-600 text-white', icon: 'i-lucide-rotate-cw', desc: 'Rotates robot 90° clockwise' },
  { id: 'left', name: 'Turn Left', action: 'turn_left', color: 'bg-yellow-400 hover:bg-yellow-500 text-navy-950', icon: 'i-lucide-rotate-ccw', desc: 'Rotates robot 90° counter-clockwise' },
  { id: 'beep', name: 'Chirp Sound', action: 'beep', color: 'bg-purple-100 hover:bg-purple-200 text-purple-900 border border-purple-300', icon: 'i-lucide-volume-2', desc: 'Emits a sound wave signal' },
  { id: 'led', name: 'Glow LED', action: 'light_led', color: 'bg-yellow-100 hover:bg-yellow-200 text-yellow-900 border border-yellow-300', icon: 'i-lucide-sparkles', desc: 'Lights up the sensor array' },
]

// State of the sequence
const sequence = ref<BotCommand[]>([
  AVAILABLE_COMMANDS[0]!, // Forward
  AVAILABLE_COMMANDS[1]!, // Turn Right
  AVAILABLE_COMMANDS[0]!, // Forward
  AVAILABLE_COMMANDS[4]!, // Glow LED
])

// Grid & Robot Position (5x5 grid: x 0..4, y 0..4, start at 1, 3 facing 0° North)
// Facing angles: 0 = North (Up), 90 = East (Right), 180 = South (Down), 270 = West (Left)
const botX = ref(1)
const botY = ref(3)
const botHeading = ref(0)
const isBeeping = ref(false)
const isLedGlowing = ref(false)
const isRunning = ref(false)
const activeStepIndex = ref<number | null>(null)
const statusMessage = ref('Add commands or click Run Sequence to watch your robot execute code.')
const reachedTarget = ref(false)

// Target position (gem at x=2, y=2)
const targetX = 2
const targetY = 2

let executionTimer: ReturnType<typeof setTimeout> | null = null

function addCommand(cmd: BotCommand) {
  if (sequence.value.length < 8 && !isRunning.value) {
    sequence.value.push(cmd)
    statusMessage.value = `Added ${cmd.name}. Program now has ${sequence.value.length} steps.`
  }
}

function removeCommand(index: number) {
  if (!isRunning.value) {
    const removed = sequence.value.splice(index, 1)[0]
    if (removed) {
      statusMessage.value = `Removed ${removed.name}.`
    }
  }
}

function resetBoard() {
  if (executionTimer) clearTimeout(executionTimer)
  isRunning.value = false
  activeStepIndex.value = null
  botX.value = 1
  botY.value = 3
  botHeading.value = 0
  isBeeping.value = false
  isLedGlowing.value = false
  reachedTarget.value = false
  statusMessage.value = 'Robot reset to starting position (1, 3).'
}

function clearSequence() {
  if (!isRunning.value) {
    sequence.value = []
    resetBoard()
    statusMessage.value = 'Sequence cleared. Select blocks below to compose your program.'
  }
}

async function runSequence() {
  if (isRunning.value || sequence.value.length === 0) return

  resetBoard()
  isRunning.value = true
  statusMessage.value = 'Running sequence…'

  for (let i = 0; i < sequence.value.length; i++) {
    activeStepIndex.value = i
    const step = sequence.value[i]!

    await new Promise<void>((resolve) => {
      executionTimer = setTimeout(() => {
        executeStep(step)
        resolve()
      }, 650)
    })

    // Check if reached target
    if (botX.value === targetX && botY.value === targetY) {
      reachedTarget.value = true
      isLedGlowing.value = true
      statusMessage.value = 'Success! Robot reached the target crystal! Try building another sequence.'
    }
  }

  executionTimer = setTimeout(() => {
    isRunning.value = false
    activeStepIndex.value = null
    if (!reachedTarget.value) {
      statusMessage.value = `Sequence finished at (${botX.value}, ${botY.value}). Try adjusting your commands to collect the crystal!`
    }
  }, 400)
}

function executeStep(step: BotCommand) {
  isBeeping.value = false
  isLedGlowing.value = false

  switch (step.action) {
    case 'forward': {
      // Move in direction of heading
      const rad = (botHeading.value * Math.PI) / 180
      const dx = Math.round(Math.sin(rad))
      const dy = Math.round(-Math.cos(rad))
      const newX = Math.max(0, Math.min(4, botX.value + dx))
      const newY = Math.max(0, Math.min(4, botY.value + dy))
      botX.value = newX
      botY.value = newY
      statusMessage.value = `Robot stepped to column ${newX + 1}, row ${newY + 1}.`
      break
    }
    case 'turn_right':
      botHeading.value = (botHeading.value + 90) % 360
      statusMessage.value = `Robot turned right, now facing ${getHeadingName(botHeading.value)}.`
      break
    case 'turn_left':
      botHeading.value = (botHeading.value + 270) % 360
      statusMessage.value = `Robot turned left, now facing ${getHeadingName(botHeading.value)}.`
      break
    case 'beep':
      isBeeping.value = true
      statusMessage.value = 'Robot sent a sensor chirp!'
      break
    case 'light_led':
      isLedGlowing.value = true
      statusMessage.value = 'Robot illuminated its LED matrix.'
      break
  }
}

function getHeadingName(deg: number): string {
  if (deg === 0) return 'North'
  if (deg === 90) return 'East'
  if (deg === 180) return 'South'
  return 'West'
}

onUnmounted(() => {
  if (executionTimer) clearTimeout(executionTimer)
})

const maxStepsReached = computed(() => sequence.value.length >= 8)
</script>

<template>
  <div class="rounded-3xl bg-navy-950 text-white p-6 sm:p-8 md:p-10 border-2 border-purple-500/30 shadow-2xl relative overflow-hidden">
    <!-- Retro background grid pattern -->
    <div class="absolute inset-0 bg-[radial-gradient(#8C2ACA_1px,transparent_1px)] [background-size:24px_24px] opacity-20 pointer-events-none" />

    <!-- Header Section -->
    <div class="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-400 text-navy-950 text-xs font-bold uppercase tracking-wider mb-2">
          <UIcon name="i-lucide-terminal" class="w-4 h-4" />
          Interactive Experience
        </div>
        <h3 class="text-2xl sm:text-3xl font-heading font-black text-white">
          A Small Act of Building
        </h3>
        <p class="text-navy-300 text-sm sm:text-base mt-1 max-w-xl">
          Children think like engineers by giving clear commands, watching immediate results, and debugging when the path turns. Try it yourself below!
        </p>
      </div>

      <!-- Quick status indicator -->
      <div class="shrink-0 bg-navy-900/90 border border-purple-500/40 rounded-2xl px-4 py-2.5 flex items-center gap-3">
        <span class="w-3 h-3 rounded-full animate-pulse" :class="isRunning ? 'bg-yellow-400' : 'bg-emerald-400'" />
        <span class="text-xs font-mono font-medium text-navy-200">
          {{ isRunning ? 'Robot executing program…' : 'Ready for input' }}
        </span>
      </div>
    </div>

    <!-- Main Builder Grid (Dual Layer: Child Simulator on Left, Parent Pedagogy on Right) -->
    <div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- ── Left Side: Interactive Robot Arena & Controls (7 cols) ──── -->
      <div class="lg:col-span-7 space-y-6">
        <!-- Visual Grid Arena (SVG) -->
        <div class="bg-navy-900/80 rounded-2xl border border-navy-700/80 p-4 sm:p-6 shadow-inner relative flex flex-col items-center">
          <div class="w-full max-w-[340px] aspect-square relative">
            <!-- 5x5 SVG Simulation Arena -->
            <svg
              class="w-full h-full rounded-xl bg-navy-950 border border-purple-900/60 shadow-lg"
              viewBox="0 0 500 500"
              role="img"
              aria-label="5 by 5 robot simulation grid"
            >
              <!-- Grid lines -->
              <defs>
                <pattern id="arena-grid" width="100" height="100" patternUnits="userSpaceOnUse">
                  <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#8C2ACA" stroke-width="1" stroke-opacity="0.25" />
                </pattern>
                <!-- Target Glow Filter -->
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              <rect width="500" height="500" fill="url(#arena-grid)" />

              <!-- Start Cell Marker (x=1, y=3) -->
              <rect x="105" y="305" width="90" height="90" rx="10" fill="#8C2ACA" fill-opacity="0.12" stroke="#8C2ACA" stroke-dasharray="4" stroke-opacity="0.4" />
              <text x="150" y="380" fill="#9F555E" font-size="12" font-family="DM Sans" text-anchor="middle">START</text>

              <!-- Target Crystal (x=2, y=2) -->
              <g transform="translate(250, 250)">
                <circle r="28" fill="#F9C41D" fill-opacity="0.2" class="animate-pulse" />
                <!-- Diamond Star Shape -->
                <polygon
                  points="0,-20 18,-6 12,18 -12,18 -18,-6"
                  fill="#F9C41D"
                  stroke="#FFFFFF"
                  stroke-width="2"
                  filter="url(#glow)"
                />
                <circle cx="0" cy="0" r="4" fill="#FFFFFF" />
              </g>

              <!-- Sound wave visual ripples when beeping -->
              <g v-if="isBeeping" :transform="`translate(${botX * 100 + 50}, ${botY * 100 + 50})`">
                <circle r="36" fill="none" stroke="#F9C41D" stroke-width="2" opacity="0.8" class="animate-ping" />
                <circle r="48" fill="none" stroke="#F6479A" stroke-width="1.5" opacity="0.6" class="animate-ping" />
              </g>

              <!-- Robot Token with dynamic coordinates and rotation -->
              <g
                :style="{
                  transform: `translate(${botX * 100 + 50}px, ${botY * 100 + 50}px) rotate(${botHeading}deg)`,
                  transformOrigin: 'center',
                  transition: 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
                }"
              >
                <!-- Rover body -->
                <rect x="-30" y="-30" width="60" height="60" rx="14" fill="#160D35" stroke="#F6479A" stroke-width="3" />

                <!-- Wheels on sides -->
                <rect x="-36" y="-22" width="7" height="18" rx="3" fill="#F9C41D" />
                <rect x="-36" y="4" width="7" height="18" rx="3" fill="#F9C41D" />
                <rect x="29" y="-22" width="7" height="18" rx="3" fill="#F9C41D" />
                <rect x="29" y="4" width="7" height="18" rx="3" fill="#F9C41D" />

                <!-- Sensor / Direction pointer (Front of robot) -->
                <polygon points="0,-24 -10,-12 10,-12" fill="#F9C41D" />

                <!-- LED Matrix face -->
                <circle
                  cx="0"
                  cy="6"
                  r="12"
                  :fill="isLedGlowing ? '#F9C41D' : '#8C2ACA'"
                  :stroke="isLedGlowing ? '#FFFFFF' : '#8C2ACA'"
                  stroke-width="2"
                />
                <circle v-if="isLedGlowing" cx="0" cy="6" r="18" fill="none" stroke="#F9C41D" stroke-width="2" opacity="0.6" class="animate-ping" />
              </g>
            </svg>
          </div>

          <!-- Live screen reader announcements & user feedback bar -->
          <div
            id="arena-status"
            role="status"
            aria-live="polite"
            class="w-full mt-4 text-xs font-mono py-2 px-3.5 rounded-xl bg-navy-950/80 border border-navy-700 text-yellow-300 flex items-center justify-between"
          >
            <span>&gt; {{ statusMessage }}</span>
            <span v-if="reachedTarget" class="text-emerald-400 font-bold ml-2 shrink-0">🎯 GOAL REACHED!</span>
          </div>
        </div>

        <!-- Sequence Strip (Program code blocks) -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-navy-300">
              Active Program Sequence ({{ sequence.length }} / 8)
            </span>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="text-xs text-navy-400 hover:text-pink-400 transition-colors cursor-pointer disabled:opacity-40"
                :disabled="isRunning || sequence.length === 0"
                @click="clearSequence"
              >
                Clear
              </button>
              <button
                type="button"
                class="text-xs text-navy-400 hover:text-yellow-400 transition-colors cursor-pointer"
                :disabled="isRunning"
                @click="resetBoard"
              >
                Reset Bot
              </button>
            </div>
          </div>

          <!-- Blocks Container -->
          <div
            class="min-h-[58px] p-2.5 rounded-2xl bg-navy-900 border border-purple-900/50 flex flex-wrap items-center gap-2"
            role="region"
            aria-label="Sequence block editor"
          >
            <p v-if="sequence.length === 0" class="text-xs text-navy-400 italic px-2">
              Program is empty. Click commands below to add actions.
            </p>

            <div
              v-for="(cmd, idx) in sequence"
              :key="`${cmd.id}-${idx}`"
              class="relative group inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold font-mono transition-all duration-200"
              :class="[
                cmd.color,
                activeStepIndex === idx ? 'ring-4 ring-yellow-400 scale-105 shadow-lg' : 'opacity-90 hover:opacity-100',
              ]"
            >
              <span class="text-[10px] opacity-60">#{{ idx + 1 }}</span>
              <UIcon :name="cmd.icon" class="w-3.5 h-3.5" />
              <span>{{ cmd.name }}</span>

              <!-- Remove block button -->
              <button
                type="button"
                class="ml-1 w-4 h-4 rounded-full bg-black/20 hover:bg-black/50 flex items-center justify-center text-[10px] cursor-pointer"
                :disabled="isRunning"
                :aria-label="`Remove step ${idx + 1}: ${cmd.name}`"
                @click="removeCommand(idx)"
              >
                &times;
              </button>
            </div>
          </div>
        </div>

        <!-- Command Block Palette (Buttons to add) -->
        <div class="space-y-2">
          <span class="block text-xs font-bold uppercase tracking-wider text-navy-300">
            Click to Append Command
          </span>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button
              v-for="cmd in AVAILABLE_COMMANDS"
              :key="cmd.id"
              type="button"
              :disabled="isRunning || maxStepsReached"
              class="flex items-center gap-2 p-2.5 rounded-xl text-xs font-semibold border border-purple-500/20 bg-navy-900 hover:bg-purple-900/30 text-navy-200 hover:text-white transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed text-left"
              @click="addCommand(cmd)"
            >
              <div class="w-6 h-6 rounded-lg flex items-center justify-center shrink-0" :class="cmd.color">
                <UIcon :name="cmd.icon" class="w-3.5 h-3.5" />
              </div>
              <div class="truncate">
                <span class="block truncate">{{ cmd.name }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- Run Execution CTA -->
        <div class="pt-2 flex flex-wrap items-center gap-4">
          <UButton
            size="lg"
            :loading="isRunning"
            :disabled="isRunning || sequence.length === 0"
            class="bg-yellow-400 hover:bg-yellow-300 text-navy-950 font-black rounded-full px-8 py-3 text-sm sm:text-base cursor-pointer shadow-lg hover:shadow-yellow-400/20"
            @click="runSequence"
          >
            <UIcon name="i-lucide-play" class="w-4 h-4 mr-1" />
            {{ isRunning ? 'Executing…' : 'Run Sequence' }}
          </UButton>

          <span class="text-xs text-navy-400">
            Goal: Guide the robot from START to the yellow crystal.
          </span>
        </div>
      </div>

      <!-- ── Right Side: Parent Pedagogical Layer (5 cols) ─────────── -->
      <div class="lg:col-span-5 bg-navy-900/90 rounded-2xl border border-purple-500/30 p-6 md:p-8 space-y-6">
        <div>
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold mb-2">
            <UIcon name="i-lucide-lightbulb" class="w-3.5 h-3.5" />
            For Parents &amp; Educators
          </div>
          <h4 class="text-xl font-heading font-bold text-white">
            What your child is actually practising here
          </h4>
          <p class="text-xs text-navy-300 mt-1">
            Coding is not about memorising syntax. It is a structured way of thinking through problems:
          </p>
        </div>

        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <div class="w-7 h-7 rounded-lg bg-purple-600/30 border border-purple-500/50 flex items-center justify-center text-yellow-400 font-bold text-xs shrink-0 mt-0.5">
              1
            </div>
            <div>
              <strong class="block text-sm font-bold text-white">Algorithmic Decomposition</strong>
              <p class="text-xs text-navy-300 mt-0.5 leading-relaxed">
                Breaking a complex journey into individual, deterministic instructions that a computer can follow without ambiguity.
              </p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="w-7 h-7 rounded-lg bg-pink-600/30 border border-pink-500/50 flex items-center justify-center text-pink-300 font-bold text-xs shrink-0 mt-0.5">
              2
            </div>
            <div>
              <strong class="block text-sm font-bold text-white">Fearless Debugging &amp; Iteration</strong>
              <p class="text-xs text-navy-300 mt-0.5 leading-relaxed">
                When the robot takes an unexpected turn, it is not an error to be punished—it is an invitation to inspect, modify, and re-test.
              </p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="w-7 h-7 rounded-lg bg-yellow-400/20 border border-yellow-400/40 flex items-center justify-center text-yellow-300 font-bold text-xs shrink-0 mt-0.5">
              3
            </div>
            <div>
              <strong class="block text-sm font-bold text-white">Perspective &amp; Spatial Reasoning</strong>
              <p class="text-xs text-navy-300 mt-0.5 leading-relaxed">
                Rotating right or left requires mentally projecting oneself into the machine's viewpoint rather than observer coordinates.
              </p>
            </div>
          </div>
        </div>

        <!-- Pedagogical quote / reassurance -->
        <div class="p-4 rounded-xl bg-purple-950/60 border border-purple-700/40 text-xs text-purple-200 leading-relaxed italic">
          "At Jjenga Code, we take this foundation into tangible motors, ultrasonic sensors, breadboards, and Python code. Children build real confidence because they understand why things work."
        </div>

        <div class="pt-2">
          <NuxtLink to="/programs">
            <span class="inline-flex items-center gap-1.5 text-xs font-bold text-yellow-400 hover:text-yellow-300 transition-colors">
              Explore our curriculum pathways &rarr;
            </span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

