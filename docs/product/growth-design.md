# Growth Support & Assessment Across Jjenga Code

## 1. Core Educational Philosophy & Growth Principles

Jjenga Code designs learning around **meaningful agency, authentic challenges, progressive scaffolding, collaboration, and iterative reflection**. We normalize debugging, revision, and testing as intrinsic parts of building rather than signals of deficiency.

Key pedagogical tenets:
- **Agency & Meaningful Choice:** Learners choose project themes, coding approaches, and creative variations within structured curricular goals.
- **Normalizing Iteration:** Code failure is treated as informative feedback. Error messages and unexpected behaviors are framed as puzzles to investigate, not mistakes to penalize.
- **Comparative Self-Referencing:** Learners track progress against their own previous projects and skill milestones, rather than against peer rankings or competitive leaderboards.
- **Formative Feedback:** Feedback always identifies a specific working strategy, celebrates authentic effort, and suggests a concrete next experiment.

---

## 2. Portal Milestone Architecture & Experience Principles

The Jjenga Code platform architecture plans four authenticated portal experiences. During the current public website milestone, these portals remain cleanly decoupled and preserved as future milestones.

### 2.1 Learner Experience (Future Milestone)
- **Project Portfolio:** A living record of built artifacts (Scratch games, Python algorithms, robotics behaviors, and web pages).
- **Interactive Workspace:** Embedded execution environments (Blockly canvas, Python terminal, robotics simulator) with scaffolded hints.
- **Reflective Journaling:** Prompts at the conclusion of each project asking learners: *What worked? What surprised you? What would you change next time?*
- **Privacy & Safety:** Learner profiles do not expose personal data or contact details. Profiles can exist and record work without requiring external social media or public sharing.

### 2.2 Teacher Experience (Future Milestone)
- **Formative Observation Logging:** Simple, low-friction tools to record qualitative observations of technical persistence, collaborative problem-solving, and creative execution during live sessions.
- **Rubric-Based Practical Assessment:** Multi-dimensional assessment templates separating technical syntax, algorithmic logic, and visual/mechanical design.
- **Workload Protection:** Streamlined bulk actions, reusable feedback snippets, and automated submission verification to keep administrative overhead low and maximize instructional contact time.
- **Private Reflection Notes:** Private instructor annotations to track instructional interventions and individualized support needs across terms.

### 2.3 Parent & Guardian Experience (Future Milestone)
- **Artifact Showcase:** Parents see actual learner creations (playable links, videos of moving robots, screenshots of code) rather than abstract letter grades.
- **Constructive Conversation Prompts:** Contextual prompts suggesting dinner-table questions: *"Ask Alex how they solved the obstacle-avoidance loop in robotics club this Saturday."*
- **Attendance & Logistical Clarity:** Live calendars, session dates, venue details, and attendance confirmations.
- **Consent & Relation Verification:** Strict verification of guardian relationships before granting access to learner project records.

### 2.4 Administrator Experience (Future Milestone)
- **Curriculum & Pathway Governance:** Managing pathway definitions (School Term, Saturday Club, Holiday Camps), course syllabi, and age recommendations.
- **Class & Schedule Management:** Assigning lead instructors, assistant mentors, physical venues (e.g., Maktaba Kuu), and session capacities.
- **Admissions Processing:** Reviewing public enrolment applications, verifying age eligibility, managing waitlists, and issuing confirmed registration credentials.
- **Audit & Compliance:** Complete, append-only audit trail of admissions decisions, account role modifications, and system configuration changes.

---

## 3. Evidence-Based Assessment Boundaries & Safeguards

To prevent educational harm and maintain ethical software boundaries, Jjenga Code adheres to strict guardrails:

### 3.1 Separation of Evidence Domains
- **Practical Competency Evidence:** Objective demonstration of code concepts (loops, conditionals, functions, hardware sensors).
- **Process Observations:** Qualitative notes on collaboration, curiosity, and iterative troubleshooting.
- **Administrative Records:** Attendance, completion status, and tuition/application records.
- These three domains are stored in distinct database entities and are never collapsed into a single speculative "intelligence score" or "aptitude rating."

### 3.2 Guardrails Against Covert Behavioral Profiling
- **No Covert Psychological Scoring:** The system strictly prohibits automated algorithms that claim to detect emotional state, personality types, or innate "grit" from typing speeds, mouse clicks, or camera feeds.
- **No Dark Patterns or Online Coercion:** No artificial streaks, countdown timers, or notification spam designed to compel daily engagement.
- **Transparency of Records:** Learners and parents have the right to view all assessment rubrics, recorded observations, and teacher comments associated with their profile.
- **Human Decision Authority:** Automated tools may assist in syntax verification or unit testing, but all evaluations of student mastery and enrolment decisions remain under direct human teacher and administrator control.

---

## 4. Current Milestone Scope Boundary

The current development milestone focuses exclusively on:
1. Public Website & Campaign Communication
2. Responsive Brand Presentation & Verified Media Provenance
3. Dynamic Program Catalogue & Real-Time Availability
4. Secure, Idempotent Public Enrolment Application Flow
5. Local PostgreSQL 17 Database Defense & RLS Policies

All portal routes (`/portal/*`, `/admin/*`, `/teacher/*`, `/learner/*`) and corresponding database migrations remain scheduled for subsequent release phases.
