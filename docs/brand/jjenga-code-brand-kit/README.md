# Jjenga Code web brand assets

Prepared from the original vector logo supplied in `JENGA CODE LOGO.pdf`, using
the two supplied camp posters as the current website art direction.

## Files

| File | Use |
| --- | --- |
| `jenga-code-gradient.svg` | Main wordmark for white or very light backgrounds. |
| `jenga-code-navy.svg` | One-colour wordmark for light surfaces. |
| `jenga-code-white.svg` | Reversed wordmark for navy or purple surfaces. |
| `jenga-pixel-pattern.svg` | Repeating decorative background derived from the original large letterforms. |
| `POSTER_TO_WEBSITE.md` | Art direction, content examples, missing source assets and implementation brief. |

The logo SVGs preserve the original ten outlined shapes, including the retro
lettering and period. They contain real vector paths, not embedded JPEG/PNG
images or a substitute font. The wordmark proportions are preserved. The gradient
is recreated from the approved yellow/pink/purple palette; the source PDF's
rasterised gradient shading is not embedded in these files.

Each wordmark has a transparent background and a viewBox of approximately
992.480469 × 143.942719. The pattern is a transparent 640 × 320 tile at 3.5% navy
opacity; its letterforms are deliberately quiet on a white surface.

## Add to the Nuxt project

Copy the four SVGs into `frontend/public/brand/`. Nuxt then serves them at `/brand/`.
Keep the editable paths as supplied; apply responsive sizing through CSS.

```html
<!-- Purpose: display the supplied logo with an accessible name. -->
<img class="brand-logo" src="/brand/jenga-code-gradient.svg" alt="Jjenga Code" />
```

```css
/* Purpose: keep the wordmark responsive without distorting its proportions. */
.brand-logo {
  display: block;
  width: clamp(11.5rem, 18vw, 17.5rem);
  max-width: 100%;
  height: auto;
}

/* Purpose: echo the poster's faint retro geometry behind a light section. */
.poster-pattern {
  background-color: #ffffff;
  background-image: url('/brand/jenga-pixel-pattern.svg');
  background-repeat: repeat;
  background-size: 640px 320px;
}
```

The logo files include accessible SVG titles. When using them through an `img`,
supply the appropriate HTML `alt` text. Use the pattern as a decorative background.
If embedding an SVG inline more than once, give each instance unique internal
title/description/gradient IDs and update its references.

## Verification

- XML parsed successfully for all four SVGs.
- No raster images, external fonts, scripts or external asset references.
- Navy silhouette matched the original rendered vector silhouette exactly in QA.
- Gradient, navy and white versions rendered in Chromium with ten logo paths each.
- Source photos and illustration strips are not included; obtain their originals
  for the website rather than extracting low-resolution copies from the posters.
