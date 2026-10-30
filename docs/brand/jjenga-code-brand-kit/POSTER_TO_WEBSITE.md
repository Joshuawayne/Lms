# Jjenga Code: from poster to website

Use the two supplied camp posters as the primary visual reference for this pass.
The earlier website inspiration images remain secondary references for composition
and interaction. Continue implementation in the existing Antigravity project;
preserve its APIs, enrolment behaviour, configuration and engineering standards.

## The visual idea

The posters combine hands-on learning, bold navy messages, real learner imagery,
retro game lettering and bright, friendly accents. Translate that combination into
a responsive website with a clear route from interest to program discovery and
application. Treat the printed design as a visual language, not a full-page image
to place inside a browser.

Keep these relationships:

- Bright white reading surfaces, generous breathing space and faint oversized
  geometric letterforms in the background.
- A dominant learner/project photograph with its cutout extending into the composition.
- Short, heavy navy headlines with deliberate line breaks and restrained emphasis.
- The supplied retro wordmark with its warm gradient, supported by pink, purple
  and yellow details.
- Hand-drawn lines, arrows and playful illustration used to frame or connect content.

Keep the Game Boy-era character in the logo, small labels and occasional visual
details. Use clear modern typography for body text, navigation, forms and feedback.
Sora headings and DM Sans body remain a suitable implementation starting point.
Ask for the original poster font names if an exact headline-font match is required.

## Exact palette

| Colour | Hex |
| --- | --- |
| Navy | `#160D35` |
| Purple | `#8C2ACA` |
| Yellow | `#F9C41D` |
| Pink | `#F6479A` |
| Muted rose | `#9F555E` |
| White | `#FFFFFF` |

Use the included pixel pattern selectively on white backgrounds. Make other colour
tints explicit design tokens. Give text, focus states and controls adequate contrast;
decorate around readable content. Use gradients for selected brand moments.

## First implementation slice

### Header

Use the actual SVG logo. Build restrained navigation and one clear program-discovery
action. Preserve mobile menu usability, keyboard focus and the homepage logo link.

### Hero

Use a white, faintly patterned background. Put a short, oversized navy headline on
the left and a substantial approved learner/project cutout on the right. Allow
controlled overlap without covering the words, the learner's face or key project
details. Use one pink hand-drawn accent and a restrained yellow or purple detail.

Keep the primary action `Explore programs` connected to the real catalogue. A
secondary `See how learning works` action can lead to the corresponding section.
Maintain semantic HTML text and a clear reading order at every viewport width.

### Three pathways

Give School-Term Programs, Saturday Coding Club and Holiday Programs distinct
compositions using real project images, selected geometric frames and deliberate
colour blocking. Keep consistent information hierarchy and action placement. Program
availability and dates still come from the backend. Use useful empty/unavailable
states when records are not configured.

Then extend the established visual system through learning examples, the application
journey and the footer. Work in reviewable passes, with desktop and mobile screenshots
of the implemented result.

## Voice and quiet growth support

Aim for curiosity, agency, practice, belonging and clear next steps. Present making
as something a learner can explore and improve, with a teacher's support. Keep
project performance, competency evidence and values observations separate.

Suggested website wording, subject to editorial review:

- Campaign line from the poster: `Raise a builder, not just a user.`
- Positive hero alternative: `Big ideas start with curious hands.`
- Supporting copy: `Hands-on coding and robotics. A place to ask questions, test
  ideas and build something of your own.`
- Learner invitation: `What will you build next?`
- Practice cue: `Try it. Change it. Try again.`
- Parent action: `Explore programs`.
- Application confirmation: `Application received. Your reference is [reference].
  Our team will review it before confirming enrolment.`
- Uncertain submission: `We couldn't confirm your application yet. Your details
  are still here. You can try again.`

Treat these as tone and interaction choices, not claims of measured psychological
outcomes. Make progress visible through real project evidence and useful feedback.
Use genuine availability information; publish only verified claims and testimonials.

## Motion and interaction

Retain the agreed Lenis/AOS approach where it fits the installed Nuxt stack. Use
short reveals, gentle movement of selected decorative layers and clear button
feedback. A subtle pixel assembly effect for the logo can be an optional enhancement.
Keep a crisp, immediately available static logo as the default.

Respect reduced motion. Keep navigation, forms, touch scrolling and browser history
reliable. Avoid animation delays that hold back an action. Verify the page without
animation enhancements as well as with them.

## Source assets needed

The current posters are flattened JPEGs. Request the following originals:

1. The learner/project photographs used in the posters, ideally at least 2000 pixels
   along the long edge. Transparent PNG cutouts are useful if already available.
2. The bottom illustration strip from the first poster as editable vector artwork
   or a high-resolution transparent image.
3. The editable poster file or exact headline font names, if available.

The SVG logo and faint pixel pattern are included here; no additional stock texture
is necessary to begin this direction. Confirm that photography supplied for the
website is approved for that use.

## Details visible in the supplied posters

These details are transcribed from the supplied campaign artwork; they are not live
database records or a statement of current availability:

- Five-day coding and robotics camp.
- 23–27 November 2026, Monday–Friday, 9am–5pm.
- Maktaba Kuu, Upper Hill, Nairobi.
- `hello@jengacode.tech`.
- `+254 792 696 592`.

Confirm campaign details and availability before publishing a real catalogue record.
An application reference confirms receipt; enrolment and account invitation follow
administrator approval. Preserve that distinction in all website copy.

## Completion evidence

Report the source files changed, the assets used and still missing, and the checks
actually run. Inspect desktop and mobile composition, image cropping, type hierarchy,
contrast, focus, reduced motion, page loading and application-flow behaviour. Keep
database tests and deployment readiness reported separately from visual verification.
