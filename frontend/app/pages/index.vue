<!--
  Jjenga Code — Public Homepage
  Directly reflects the visual identity of the Jjenga Code posters:
  - Bright white surfaces with subtle repeating pixel pattern background.
  - Heavy navy headlines with deliberate line breaks ("Raise a builder, not just a user.")
  - Approved palette: Navy #160D35, Purple #8C2ACA, Yellow #F9C41D, Pink #F6479A, Muted rose #9F555E, White #FFFFFF.
  - Curated high-resolution CDN photography with verified provenance and failure fallbacks.
  - Full pathway coverage, pedagogical breakdown, parent reassurance,
    dynamic November 2026 camp highlight, interactive building demo, and honest application journey.
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BRAND_IMAGES, imageUrl } from '~/utils/images'
import type { BrandImage } from '~/utils/images'
import type { components } from '~/api/generated/types'
import { useApplicationAvailability } from '~/features/programs/composables/useApplicationAvailability'
import InteractiveBuildingDemo from '~/components/home/InteractiveBuildingDemo.vue'
import BrandPhoto from '~/components/ui/BrandPhoto.vue'

definePageMeta({ layout: 'public' })

const { $api } = useNuxtApp()

// Dynamically fetch featured camp from server
const { data: featuredCamp } = useAsyncData(
  'featured-camp',
  () => $api<components['schemas']['ProgramDetailResponse']>('/programs/coding-robotics-camp-nov-2026').catch(() => null),
)

const campAvailability = computed(() => (featuredCamp.value ? useApplicationAvailability(featuredCamp.value) : null))

useHead({
  title: 'Jjenga Code — Raise a Builder, Not Just a User',
  meta: [
    {
      name: 'description',
      content: 'Hands-on coding and robotics where children ask questions, test ideas, and build something of their own. School-term programs, Saturday clubs, and holiday camps in Nairobi.',
    },
    { property: 'og:title', content: 'Jjenga Code — Raise a Builder, Not Just a User' },
    { property: 'og:description', content: 'Hands-on coding and robotics for young makers in Nairobi, Kenya.' },
    { property: 'og:image', content: imageUrl(BRAND_IMAGES.hero, 960) },
  ],
})

interface PathwayItem {
  key: string
  title: string
  schedule: string
  description: string
  image: BrandImage
  badgeColor: string
  accentBorder: string
  query: string
}

interface ProjectArea {
  id: string
  title: string
  tagline: string
  description: string
  image: BrandImage
  tags: string[]
}

// Pathways configuration
const pathways: PathwayItem[] = [
  {
    key: 'school_term',
    title: 'School-Term Programs',
    schedule: 'Weekly sessions throughout the term',
    description: 'Weekly coding and robotics sessions during the school term. Learners build structured projects, solve real problems, and graduate with a portfolio of completed work.',
    image: BRAND_IMAGES.school_term,
    badgeColor: 'border-purple-200 bg-purple-50 text-purple-700',
    accentBorder: 'hover:border-purple-500',
    query: 'school_term',
  },
  {
    key: 'saturday_club',
    title: 'Saturday Coding Club',
    schedule: 'Saturday morning sessions',
    description: 'A vibrant weekend maker lab for curiosity-driven exploration. Learners build games, construct sensors, and collaborate with peers who love creating with technology.',
    image: BRAND_IMAGES.saturday_club,
    badgeColor: 'border-yellow-200 bg-yellow-50 text-yellow-800',
    accentBorder: 'hover:border-yellow-500',
    query: 'saturday_club',
  },
  {
    key: 'holiday',
    title: 'Holiday Programs & Camps',
    schedule: '5-Day immersive holiday intensives',
    description: 'Intensive full-day camps during school holidays. Learners tackle a thematic challenge from initial concept to a functioning robotic prototype or software game.',
    image: BRAND_IMAGES.holiday_camp,
    badgeColor: 'border-pink-200 bg-pink-50 text-pink-700',
    accentBorder: 'hover:border-pink-500',
    query: 'holiday',
  },
]

// What young builders explore & make using verified photographs
const projectAreas: ProjectArea[] = [
  {
    id: 'robotics',
    title: 'Robotics & Hardware',
    tagline: 'From sensors to moving machines',
    description: 'Learners connect motors, ultrasonic distance sensors, and microcontrollers. They write real code to make machines respond to their environment.',
    image: BRAND_IMAGES.robot,
    tags: ['Micro:bit', 'Arduino', 'Sensors & Motors', 'Autonomous Vehicles'],
  },
  {
    id: 'coding',
    title: 'Game Development & Logic',
    tagline: 'Turn playtime into creative programming',
    description: 'Understanding loops, conditionals, and algorithms by constructing playable games, interactive stories, and multiplayer simulations.',
    image: BRAND_IMAGES.school_term,
    tags: ['Visual Block Coding', 'Python Fundamentals', '2D Game Physics', 'Logic & Loops'],
  },
  {
    id: 'electronics',
    title: 'Physical Computing',
    tagline: 'Bring ideas into the physical world',
    description: 'Hands-on breadboard prototyping, circuit design, LED matrix controls, and smart home inventions that bridge software and hardware.',
    image: BRAND_IMAGES.saturday_club,
    tags: ['Breadboards', 'LED Matrices', 'Circuits & Power', 'IoT Prototypes'],
  },
]

const activeArea = ref<ProjectArea>(projectAreas[0]!)

// How learning works steps
const learningSteps = [
  {
    number: '01',
    title: 'Hands-on Exploration',
    subtext: 'Try it. Change it. Try again.',
    description: 'We skip dry lectures. Learners immediately engage with tangible kits, starter code, and curiosity-driven puzzles designed to spark discovery.',
  },
  {
    number: '02',
    title: 'Purposeful Project Building',
    subtext: 'From \'what if?\' to \'I made this.\'',
    description: 'Every concept is anchored in a concrete project. Learners design and code artifacts that solve real challenges or bring their imaginations to life.',
  },
  {
    number: '03',
    title: 'Personalized Mentor Guidance',
    subtext: 'Safe support when code fails.',
    description: 'Experienced educators maintain a supportive teacher-to-learner ratio, debugging together, encouraging agency, and celebrating breakthrough moments.',
  },
  {
    number: '04',
    title: 'Reflection & Portfolio Growth',
    subtext: 'Demonstrable skill progression.',
    description: 'Learners articulate how their creation functions. We track real project performance, competencies, and problem-solving values across terms.',
  },
]

// Application Journey Steps
const applicationSteps = [
  {
    step: '1',
    title: 'Choose a Program',
    desc: 'Browse our school-term, weekend club, or holiday camp cohorts to find the right fit for your learner\'s age and schedule.',
  },
  {
    step: '2',
    title: 'Submit Application',
    desc: 'Fill out our brief online form without an account. You immediately receive a unique database submission receipt reference.',
  },
  {
    step: '3',
    title: 'Team Review',
    desc: 'Our academic team reviews learner age and prerequisites to confirm placement and prepare personalized materials.',
  },
  {
    step: '4',
    title: 'Enrolment & Welcome',
    desc: 'Upon approval, you receive a confirmed enrolment notice and your personal cohort welcome package.',
  },
]

// Confirmed FAQs with authentic, non-exaggerated details
const faqs = [
  {
    q: 'Does my child need previous coding or robotics experience?',
    a: 'Not at all. Our programs cater to beginners through to experienced young coders. Mentors adapt project complexity to each child\'s individual starting point.',
  },
  {
    q: 'What equipment does my child need to bring?',
    a: 'We provide specialized hardware kits, microcontrollers, robotics components, breadboards, and electronic sensors for every session. Specific device and software requirements for each cohort are confirmed during application review.',
  },
  {
    q: 'Where will the November 2026 Holiday Camp take place?',
    a: 'The upcoming 5-day holiday camp runs Monday to Friday, 9:00 AM – 5:00 PM at Maktaba Kuu, Upper Hill, Nairobi.',
  },
  {
    q: 'Does submitting an application guarantee a reserved seat?',
    a: 'Your submission generates a unique receipt reference confirming our database recorded your application. To ensure optimal mentor-to-student ratios, placements are formally confirmed following our team\'s admissions review.',
  },
  {
    q: 'How do you keep parents informed of their child\'s progress?',
    a: 'Mentors record routine project observations and competency evidence. In our upcoming portal, authorized guardians can view constructive feedback, projects, and milestone reports directly.',
  },
]
</script>

<template>
  <div class="relative bg-white selection:bg-pink-100 selection:text-navy-950">
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 1. HERO SECTION                                                     -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="relative overflow-hidden poster-pattern pt-8 pb-16 md:py-20 lg:py-24 border-b border-navy-100">
      <!-- Faint background geometric letterings -->
      <div class="absolute inset-0 pointer-events-none select-none overflow-hidden opacity-[0.035] flex items-center justify-center font-heading font-black text-[22vw] text-navy-950 tracking-tighter leading-none" aria-hidden="true">
        BUILD
      </div>

      <div class="relative max-w-7xl mx-auto px-5 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          <!-- Left column: Bold navy headlines and call to action -->
          <div class="lg:col-span-7 space-y-6">
            <div data-aos="fade-up" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-pink-200 bg-pink-50/80 text-pink-700 text-xs font-semibold tracking-wide uppercase">
              <span class="w-2 h-2 rounded-full bg-pink-500 animate-pulse" />
              Creative STEM Education in Nairobi
            </div>

            <h1 data-aos="fade-up" data-aos-delay="100" class="text-4xl sm:text-5xl md:text-6xl font-heading font-black text-navy-950 tracking-tight leading-[1.08]">
              Raise a builder,<br>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-700 via-pink-600 to-yellow-500">
                not just a user.
              </span>
            </h1>

            <p data-aos="fade-up" data-aos-delay="150" class="text-lg md:text-xl text-navy-700 max-w-xl font-normal leading-relaxed">
              Hands-on coding and robotics where children ask questions, test bold ideas, and build real projects of their own.
            </p>

            <!-- Key Proof Points / Highlights -->
            <div data-aos="fade-up" data-aos-delay="200" class="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
              <div class="p-3.5 rounded-2xl bg-navy-50/70 border border-navy-100">
                <span class="block text-2xl font-heading font-black text-purple-700">Ages 7–17</span>
                <span class="text-xs text-navy-600 font-medium">Tailored age pathways</span>
              </div>
              <div class="p-3.5 rounded-2xl bg-navy-50/70 border border-navy-100">
                <span class="block text-2xl font-heading font-black text-pink-600">3 Formats</span>
                <span class="text-xs text-navy-600 font-medium">Terms, clubs &amp; camps</span>
              </div>
              <div class="p-3.5 rounded-2xl bg-navy-50/70 border border-navy-100 col-span-2 sm:col-span-1">
                <span class="block text-2xl font-heading font-black text-yellow-600">100% Making</span>
                <span class="text-xs text-navy-600 font-medium">Real projects &amp; robots</span>
              </div>
            </div>

            <!-- CTAs with dual learner/parent focus -->
            <div data-aos="fade-up" data-aos-delay="250" class="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
              <NuxtLink to="/programs">
                <UButton size="xl" class="bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-full px-8 py-3.5 shadow-lg shadow-purple-200 hover:shadow-xl transition-all text-center justify-center w-full sm:w-auto">
                  Explore Programs &amp; Apply
                </UButton>
              </NuxtLink>
              <a href="#interactive-demo" class="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-full border-2 border-navy-200 text-navy-800 font-semibold hover:border-yellow-500 hover:bg-yellow-50/50 transition-colors text-center text-sm">
                <UIcon name="i-lucide-play-circle" class="w-4 h-4 text-purple-600" />
                Try Interactive Demo
              </a>
            </div>

            <!-- Child agency micro-copy -->
            <p data-aos="fade-up" data-aos-delay="300" class="text-xs text-navy-500 flex items-center gap-2 pt-1">
              <UIcon name="i-lucide-check-circle" class="w-4 h-4 text-pink-500 shrink-0" />
              <span>No prior coding experience needed. Mentors guide every step.</span>
            </p>
          </div>

          <!-- Right column: Photographic composition with hand-drawn accents -->
          <div class="lg:col-span-5 relative" data-aos="fade-left" data-aos-delay="200">
            <!-- Decorative colored backdrop shapes -->
            <div class="absolute -top-6 -right-6 w-72 h-72 bg-yellow-200/40 rounded-full blur-2xl -z-10" />
            <div class="absolute -bottom-8 -left-8 w-80 h-80 bg-purple-200/40 rounded-full blur-2xl -z-10" />

            <!-- Main photograph frame using BrandPhoto with responsive srcset and error fallback -->
            <div class="relative rounded-3xl overflow-hidden border-4 border-white shadow-2xl bg-navy-50 aspect-[4/3] sm:aspect-[5/4] lg:aspect-[4/5]">
              <BrandPhoto
                image-key="hero"
                priority
                sizes="(min-width: 1024px) 40vw, 90vw"
                class="w-full h-full object-cover object-center transform hover:scale-105 transition-transform duration-700"
              />

              <!-- Gradient overlay at the base for contrast -->
              <div class="absolute inset-0 bg-gradient-to-t from-navy-950/70 via-transparent to-transparent pointer-events-none" />

              <!-- Overlay badge at bottom -->
              <div class="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-md rounded-2xl p-4 shadow-lg border border-navy-100 flex items-center justify-between">
                <div>
                  <span class="block text-xs font-semibold text-purple-600 uppercase tracking-wider">Tournament &amp; Teamwork</span>
                  <span class="text-sm font-bold text-navy-900">Hands-on Robotic Challenges</span>
                </div>
                <div class="w-10 h-10 rounded-full bg-yellow-400 text-navy-950 flex items-center justify-center shrink-0 font-bold text-lg">
                  &gt;
                </div>
              </div>
            </div>

            <!-- Provenance note for illustrative stock photo -->
            <p class="text-[11px] text-navy-600 mt-2 text-right">
              Illustrative stock photograph: FIRST Finals Lego League (CC BY 2.0).
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 2. CONFIRMED CAMP SPOTLIGHT (Dynamically loaded)                     -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="bg-gradient-to-r from-navy-900 via-navy-950 to-purple-950 text-white py-12 relative overflow-hidden border-b border-navy-800">
      <div class="max-w-7xl mx-auto px-5 lg:px-8 relative z-10">
        <div class="rounded-3xl bg-white/5 border border-white/10 p-6 md:p-8 backdrop-blur-sm grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div class="lg:col-span-8 space-y-3">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-400 text-navy-950 text-xs font-bold uppercase tracking-wider">
              <UIcon name="i-lucide-flame" class="w-4 h-4" />
              Upcoming Camp Feature
            </div>
            <h2 class="text-2xl sm:text-3xl font-heading font-black text-white">
              {{ featuredCamp?.title || '5-Day Coding & Robotics Camp — November 2026' }}
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-sm text-navy-200">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-calendar" class="w-5 h-5 text-yellow-400 shrink-0" />
                <span>23–27 November 2026</span>
              </div>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-clock" class="w-5 h-5 text-yellow-400 shrink-0" />
                <span>Mon–Fri, 9:00 AM – 5:00 PM</span>
              </div>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-map-pin" class="w-5 h-5 text-pink-400 shrink-0" />
                <span>Maktaba Kuu, Upper Hill</span>
              </div>
            </div>
          </div>
          <div class="lg:col-span-4 flex flex-col sm:flex-row lg:flex-col gap-3 justify-center">
            <NuxtLink to="/programs/coding-robotics-camp-nov-2026" class="w-full">
              <UButton size="lg" block class="bg-yellow-400 hover:bg-yellow-300 text-navy-950 font-bold rounded-full py-3">
                View Camp Details &amp; Apply
              </UButton>
            </NuxtLink>
            <span class="text-xs text-center text-navy-300">
              Applications are currently {{ campAvailability?.label.toLowerCase() || 'open' }} for ages {{ featuredCamp?.min_age_years ?? 7 }}–{{ featuredCamp?.max_age_years ?? 17 }}.
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 3. THREE LEARNING PATHWAYS                                         -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="py-20 lg:py-28 bg-white border-b border-navy-100">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span class="inline-block text-xs font-bold tracking-widest text-purple-700 uppercase bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
            Learning Pathways
          </span>
          <h2 class="text-3xl sm:text-4xl font-heading font-black text-navy-950 tracking-tight">
            Designed for steady growth and creative confidence.
          </h2>
          <p class="text-base text-navy-600">
            Whether during the school term, on Saturday mornings, or during school holidays, learners build practical skills in an inspiring environment.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div
            v-for="pathway in pathways"
            :key="pathway.key"
            data-aos="fade-up"
            class="group rounded-3xl bg-white border-2 border-navy-100/80 hover:shadow-xl transition-all duration-300 flex flex-col overflow-hidden"
            :class="pathway.accentBorder"
          >
            <!-- Pathway image with BrandPhoto -->
            <div class="relative h-56 overflow-hidden bg-navy-100">
              <BrandPhoto
                :image-key="pathway.image.key"
                sizes="(min-width: 768px) 33vw, 100vw"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div class="absolute top-4 left-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold border backdrop-blur-md" :class="pathway.badgeColor">
                  {{ pathway.schedule }}
                </span>
              </div>
            </div>

            <!-- Content -->
            <div class="p-6 md:p-8 flex-1 flex flex-col justify-between space-y-4">
              <div class="space-y-2">
                <h3 class="text-xl font-heading font-bold text-navy-950 group-hover:text-purple-700 transition-colors">
                  {{ pathway.title }}
                </h3>
                <p class="text-sm text-navy-600 leading-relaxed">
                  {{ pathway.description }}
                </p>
              </div>

              <div class="pt-4 border-t border-navy-100 flex items-center justify-between">
                <NuxtLink :to="{ path: '/programs', query: { pathway: pathway.query } }">
                  <span class="inline-flex items-center gap-1.5 text-sm font-bold text-purple-600 hover:text-purple-800 transition-colors">
                    View cohorts &rarr;
                  </span>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 4. WHAT YOUNG BUILDERS EXPLORE & MAKE                               -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="py-20 lg:py-28 bg-navy-50/60 border-b border-navy-100">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <div class="max-w-3xl mb-12 space-y-4">
          <span class="inline-block text-xs font-bold tracking-widest text-pink-700 uppercase bg-pink-100 px-3 py-1 rounded-full border border-pink-200">
            Tangible Curriculum
          </span>
          <h2 class="text-3xl sm:text-4xl font-heading font-black text-navy-950">
            What young makers actually design and construct.
          </h2>
          <p class="text-base text-navy-600">
            Children don't just watch videos. They write loops, assemble real sensors, and create tangible artifacts they can explain with pride.
          </p>
        </div>

        <!-- Project area switcher -->
        <div class="flex flex-wrap gap-3 mb-8">
          <button
            v-for="area in projectAreas"
            :key="area.id"
            type="button"
            class="px-5 py-2.5 rounded-full text-sm font-semibold transition-all cursor-pointer"
            :class="activeArea.id === area.id ? 'bg-navy-950 text-white shadow-md' : 'bg-white text-navy-700 hover:bg-navy-100 border border-navy-200'"
            @click="activeArea = area"
          >
            {{ area.title }}
          </button>
        </div>

        <!-- Active area showcase -->
        <div class="rounded-3xl bg-white border border-navy-100 p-6 md:p-10 shadow-sm" data-aos="fade-up">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div class="lg:col-span-6 space-y-4">
              <span class="text-xs font-bold uppercase tracking-wider text-purple-600">
                {{ activeArea.tagline }}
              </span>
              <h3 class="text-2xl sm:text-3xl font-heading font-black text-navy-950">
                {{ activeArea.title }}
              </h3>
              <p class="text-base text-navy-700 leading-relaxed">
                {{ activeArea.description }}
              </p>

              <!-- Tags -->
              <div class="pt-3">
                <span class="block text-xs font-semibold text-navy-500 uppercase tracking-wider mb-2">Key Areas:</span>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in activeArea.tags"
                    :key="tag"
                    class="px-3 py-1 rounded-lg text-xs font-medium bg-purple-50 text-purple-700 border border-purple-100"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>

            <div class="lg:col-span-6">
              <div class="rounded-2xl overflow-hidden aspect-[4/3] bg-navy-100 border-2 border-navy-100 shadow-inner">
                <BrandPhoto
                  :image-key="activeArea.image.key"
                  sizes="(min-width: 1024px) 50vw, 100vw"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 4.5. INTERACTIVE BUILDING DEMONSTRATION ("A Small Act of Building")  -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section id="interactive-demo" class="py-16 lg:py-24 bg-navy-900 border-b border-navy-800">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <InteractiveBuildingDemo />
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 5. HOW PRACTICAL LEARNING WORKS                                     -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section id="how-learning-works" class="py-20 lg:py-28 bg-white border-b border-navy-100">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span class="inline-block text-xs font-bold tracking-widest text-yellow-800 uppercase bg-yellow-100 px-3 py-1 rounded-full border border-yellow-200">
            Our Learning Philosophy
          </span>
          <h2 class="text-3xl sm:text-4xl font-heading font-black text-navy-950">
            How learning, practice and reflection fit together.
          </h2>
          <p class="text-base text-navy-600">
            We move learners from passive consumers to active creators through a structured cycle of curiosity, guided building, and supportive feedback.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="step in learningSteps"
            :key="step.number"
            data-aos="fade-up"
            class="rounded-3xl p-6 bg-navy-50/50 border border-navy-100 hover:border-purple-300 transition-colors flex flex-col justify-between space-y-4"
          >
            <div class="space-y-3">
              <span class="text-3xl font-heading font-black text-purple-700/40">
                {{ step.number }}
              </span>
              <h3 class="text-xl font-heading font-bold text-navy-950">
                {{ step.title }}
              </h3>
              <p class="text-xs font-semibold text-pink-600 uppercase tracking-wide">
                {{ step.subtext }}
              </p>
              <p class="text-sm text-navy-600 leading-relaxed">
                {{ step.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 6. PARENT CONFIDENCE & TRANSPARENT REASSURANCE                      -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="py-20 lg:py-28 bg-navy-50/60 border-b border-navy-100">
      <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div class="lg:col-span-7 space-y-6">
            <span class="inline-block text-xs font-bold tracking-widest text-purple-700 uppercase bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
              Parent Peace of Mind
            </span>
            <h2 class="text-3xl sm:text-4xl font-heading font-black text-navy-950">
              Clear reassurance and transparent communication.
            </h2>
            <p class="text-base text-navy-700 leading-relaxed">
              We know introducing your child to coding is an investment in their future. Here is how we ensure their experience is safe, constructive, and inspiring.
            </p>

            <ul class="space-y-4 text-sm text-navy-800">
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                  <UIcon name="i-lucide-check" class="w-4 h-4" />
                </div>
                <div>
                  <strong class="font-bold text-navy-950">Structured, Supervised Learning:</strong>
                  Our workshops and camps operate in structured, mentor-supervised learning spaces with verified venue protocols.
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                  <UIcon name="i-lucide-check" class="w-4 h-4" />
                </div>
                <div>
                  <strong class="font-bold text-navy-950">Evidence-Based Growth:</strong>
                  We track project mastery, technical competencies, and values observations without stressful exams.
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                  <UIcon name="i-lucide-check" class="w-4 h-4" />
                </div>
                <div>
                  <strong class="font-bold text-navy-950">Honest Admissions Review:</strong>
                  Submitting an application issues an immediate database receipt. Placements are finalized by our educators to protect student-to-teacher ratios.
                </div>
              </li>
            </ul>
          </div>

          <div class="lg:col-span-5">
            <div class="rounded-3xl bg-navy-950 text-white p-8 space-y-6 shadow-xl border border-navy-800">
              <div class="space-y-2">
                <span class="text-xs font-bold tracking-widest text-yellow-400 uppercase">
                  Transparent Admission Journey
                </span>
                <h3 class="text-2xl font-heading font-black">
                  How Applications Work
                </h3>
              </div>

              <div class="space-y-4">
                <div
                  v-for="s in applicationSteps"
                  :key="s.step"
                  class="flex items-start gap-4 pb-4 border-b border-navy-800 last:border-0 last:pb-0"
                >
                  <div class="w-8 h-8 rounded-full bg-purple-600/30 border border-purple-500/50 flex items-center justify-center text-yellow-400 font-bold text-sm shrink-0">
                    {{ s.step }}
                  </div>
                  <div class="space-y-1">
                    <strong class="block text-sm font-bold text-white">{{ s.title }}</strong>
                    <p class="text-xs text-navy-300 leading-relaxed">{{ s.desc }}</p>
                  </div>
                </div>
              </div>

              <div class="pt-2">
                <NuxtLink to="/programs" class="w-full block">
                  <UButton block class="bg-yellow-400 hover:bg-yellow-300 text-navy-950 font-bold rounded-full py-3">
                    Start an Application
                  </UButton>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 7. FREQUENTLY ASKED QUESTIONS                                       -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="py-20 lg:py-28 bg-white border-b border-navy-100">
      <div class="max-w-4xl mx-auto px-5 lg:px-8 space-y-12">
        <div class="text-center space-y-3">
          <span class="inline-block text-xs font-bold tracking-widest text-pink-700 uppercase bg-pink-100 px-3 py-1 rounded-full border border-pink-200">
            Answers for Parents
          </span>
          <h2 class="text-3xl sm:text-4xl font-heading font-black text-navy-950">
            Frequently Asked Questions
          </h2>
        </div>

        <div class="space-y-4">
          <div
            v-for="(faq, idx) in faqs"
            :key="idx"
            class="rounded-2xl border border-navy-100 p-6 bg-navy-50/40 hover:bg-white transition-colors"
          >
            <h3 class="text-base sm:text-lg font-heading font-bold text-navy-950 mb-2">
              {{ faq.q }}
            </h3>
            <p class="text-sm text-navy-700 leading-relaxed">
              {{ faq.a }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- 8. BOTTOM CALL TO ACTION                                            -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <section class="py-20 lg:py-28 bg-navy-950 text-white relative overflow-hidden">
      <div class="relative max-w-5xl mx-auto px-5 lg:px-8 text-center space-y-6">
        <span class="inline-block text-xs font-bold tracking-widest text-yellow-400 uppercase bg-yellow-400/10 px-3 py-1 rounded-full border border-yellow-400/30">
          Begin Today
        </span>
        <h2 class="text-3xl sm:text-5xl font-heading font-black text-white tracking-tight">
          Help your child build what they imagine.
        </h2>
        <p class="text-base sm:text-lg text-navy-300 max-w-2xl mx-auto leading-relaxed">
          Explore our published curriculum cohorts, review dates and locations, and submit your application online.
        </p>

        <div class="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <NuxtLink to="/programs">
            <UButton size="xl" class="bg-yellow-400 hover:bg-yellow-300 text-navy-950 font-bold rounded-full px-10 py-4 shadow-xl">
              Browse All Programs
            </UButton>
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
