# Jjenga Code — Public Website Architecture & Visual Design System

## 1. Visual Identity & Brand System

The public website translates the visual language of the original Jjenga Code campaign posters into an engaging, responsive digital experience for children and parents.

### 1.1 Brand Palette & Design Tokens
Defined in `frontend/app/assets/styles/tokens.css` and mapped to Nuxt UI in `frontend/app/app.config.ts`:

| Token | Hex | Role & Rendering |
| :--- | :--- | :--- |
| `--jc-navy` | `#160D35` | Dominant text color, deep contrast headers, solid backgrounds |
| `--jc-purple` | `#8C2ACA` | Primary brand accent, primary CTA buttons (`.jc-btn-primary`), focus rings |
| `--jc-yellow` | `#F9C41D` | Energy highlight, badges, interactive goal markers, secondary accents |
| `--jc-pink` | `#F6479A` | Hand-drawn SVG flourishes, energetic accents, playful highlights |
| `--jc-muted-rose` | `#9F555E` | Supporting borders, secondary metadata labels, subtle dividers |
| `--jc-white` | `#FFFFFF` | Reading canvas, elevated card surfaces, crisp text on dark surfaces |

Supporting scales (`--jc-purple-50` to `--jc-purple-950`, `--jc-navy-50` to `--jc-navy-950`, etc.) provide WCAG 2.1 AA accessible contrast ratios for borders, states, and subtle backdrops.

### 1.2 Typography
- **Headings:** Sora (self-hosted via `@fontsource-variable/sora`), variable weights 600–800. Bold, geometric character echoing retro computing.
- **Body & Controls:** DM Sans (self-hosted via `@fontsource-variable/dm-sans`), weights 400–700. High legibility, neutral character for dense instructional copy and form inputs.
- **Brand Wordmark:** Authentic vector SVG (`frontend/public/brand/jenga-code-gradient.svg` and `jenga-code-white.svg`) preserving the 8-bit retro gaming typography without raster degradation.

---

## 2. Interactive Sequence Builder Architecture

Mounted on the homepage (`#interactive-demo`) via `frontend/app/components/home/InteractiveBuildingDemo.vue`, the sequence builder delivers "a small act of building" directly in the browser before registration.

### 2.1 Technical & Simulation Structure
- **Grid Engine:** 5x5 SVG Cartesian grid (`0,0` to `4,4`) rendered with smooth SVG coordinate transformations.
- **Actor State:** Retro rover robot with Cartesian coordinates `(x, y)` and heading angle (`0°` = East, `90°` = South, `180°` = West, `270°` = North).
- **Instruction Pipeline:** Ordered queue of maximum 8 command blocks selected by the learner:
  - `FORWARD`: Advances 1 grid unit along current vector, bounded by grid boundaries.
  - `TURN_RIGHT`: Rotates heading by +90°.
  - `TURN_LEFT`: Rotates heading by -90°.
  - `CHIRP`: Triggers animated soundwave ripples from the rover's antenna.
  - `GLOW`: Illuminates the rover's LED sensor array.
- **Tick Dispatcher:** Step-by-step execution at 600ms intervals with active step highlighting and sound/light effects.

### 2.2 Dual-Audience Pedagogical Integration
- **Child-Facing Layer:**
  - Direct tactile agency: drag-free button sequencing, immediate visual feedback.
  - Non-punitive experimentation: running into boundaries triggers gentle rebound without failure penalties.
  - Celebratory feedback: reaching the goal crystal unleashes an SVG particle celebration and the invitation *"You made it! What will you build next?"*
- **Parent-Facing Layer:**
  - Explanatory pedagogical cards adjacent to the grid explaining algorithmic decomposition, spatial reasoning, and debugging resilience.
  - Bridges the playful simulation to actual curriculum outcomes in the Python, Scratch, and Robotics pathways.

### 2.3 Accessibility & Inclusive Design
- Live announcements via `aria-live="polite"` and `role="status"` narrate simulation actions ("Rover moved to position 1, 2", "Rover chirped", "Goal crystal reached!").
- Fully operable via keyboard navigation (Tab, Enter, Space).
- Supports `prefers-reduced-motion` by reducing transition durations to zero and replacing continuous motion with discrete placement.

---

## 3. Photographic Direction & Provenance Verification

### 3.1 Provenance Architecture
All imagery is tracked via `docs/evidence/images/provenance.json` and verified with `scripts/verify-image-provenance.ps1`. Images originate from Wikimedia Commons under Creative Commons / Public Domain licenses:
- `hero`: African children collaborating in a computer classroom (CC BY-SA 4.0).
- `school_term`: Students engaged in a classroom technology project (CC BY-SA 4.0).
- `saturday_club`: Students working with hands-on robotics kits (CC BY 2.0).
- `holiday_camp`: Collaborative group solving technical build challenges (CC BY-SA 4.0).
- `robot`: Close-up of educational modular rover chassis (CC BY-SA 4.0).

### 3.2 Responsive Delivery (`BrandPhoto.vue`)
- Generates dynamic `srcset` for 500w, 960w, and 1280w resolutions.
- Emits pre-hydration inline SVG fallback to prevent layout shifts (CLS) if network assets fail.
- Captions and alt text explicitly identify images as illustrative learner activities, preserving integrity without fictitious endorsements.

---

## 4. Catalogue & Enrolment Application Flow

### 4.1 Two-Way Catalogue Synchronization (`programs/index.vue`)
- Immediate reactive synchronization between component state (`selectedPathway`, `currentPage`) and URL query parameters (`pathway`, `page`).
- Full support for browser back/forward history navigation and deep-linking from marketing campaigns.
- Deterministic pagination ordering via PostgreSQL `display_order ASC, created_at ASC, id ASC`.

### 4.2 Program-Scoped Receipt & Idempotency Defense (`applicationDraft.ts`)
- Receipts are indexed by both program ID (`receiptsByProgramId`) and slug (`receiptsBySlug`). Submitting an application for Program A never leaks or displays a receipt on Program B.
- A fresh UUIDv4 idempotency key is generated on every new payload build (`buildPayload`). Replay of idempotency keys is strictly restricted to retrying uncertain attempts.
- Monotonic attempt sequence counter ensures late responses from previous submissions are safely discarded.
- In `apply.vue`, the confirmed receipt screen renders before the closed-program gate, ensuring applicants can always view their issued reference number even if program admissions subsequently close.
- Form inputs feature `aria-describedby` linking to an accessible `#error-summary` alert with dynamic age validation (`program.max_age_years`).

---

## 5. Motion Lifecycle & Progressive Enhancement

- **AOS (`frontend/app/plugins/aos.client.ts`):** CSS is dynamically injected upon client mount and purged on unmount, avoiding SSR hydration mismatches.
- **Lenis (`frontend/app/plugins/lenis.client.ts`):** Smooth scrolling is disabled for touch devices and users with `prefers-reduced-motion: reduce`. Native browser wheel events remain unblocked.
- **Router Options (`frontend/app/router.options.ts`):** Native hash anchor navigation (`#interactive-demo`, `#pathways`) and popstate scroll positions are reliably restored across Nuxt page transitions.

