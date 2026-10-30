/**
 * Jjenga Code — photograph registry.
 *
 * Every entry was checked against the Wikimedia Commons API (author, licence, file page)
 * by scripts/verify-image-provenance.ps1; the raw result is docs/evidence/images/
 * provenance.json and the human-readable record is docs/product/image-manifest.md.
 * Alt text describes what each photograph visibly shows (the images were inspected).
 *
 * Rule: these are illustrative stock photographs. They are never presented as Jjenga Code
 * learners, classes, staff or events, and the site says so wherever they appear.
 */

export type BrandImageKey = 'hero' | 'school_term' | 'saturday_club' | 'holiday_camp' | 'robot'

export interface BrandImage {
  readonly key: BrandImageKey
  /** Describes what the photograph shows, not what we wish it showed. */
  readonly alt: string
  readonly author: string
  readonly license: string
  readonly licenseUrl: string | null
  /** Commons file page: the verified source of author and licence. */
  readonly filePage: string
  /** Commons thumbnail folder, e.g. `e/e5/<encoded file name>`. */
  readonly thumbPath: string
  readonly fileName: string
  readonly width: number
  readonly height: number
  /** Focal point so cropping keeps faces and the project in frame. */
  readonly focus: string
}

const COMMONS = 'https://upload.wikimedia.org/wikipedia/commons/thumb'

/** Thumbnail widths published by Wikimedia (arbitrary widths are rejected). */
export const IMAGE_WIDTHS = [500, 960, 1280] as const

export const ILLUSTRATIVE_NOTE
  = 'Illustrative stock photograph. It does not show Jjenga Code learners, classes or events.'

export const BRAND_IMAGES: Record<BrandImageKey, BrandImage> = {
  hero: {
    key: 'hero',
    alt: 'Two children in matching orange team shirts grin and gesture excitedly behind a table of LEGO-built robots at a robotics tournament, while adults watch and film behind them.',
    author: 'U.S. Embassy Tel Aviv',
    license: 'CC BY 2.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/2.0',
    filePage: 'https://commons.wikimedia.org/wiki/File:FIRST_Finals-_Lego_League_and_Tech_Challenge_(33181655046).jpg',
    thumbPath: 'e/e5/FIRST_Finals-_Lego_League_and_Tech_Challenge_%2833181655046%29.jpg',
    fileName: 'FIRST_Finals-_Lego_League_and_Tech_Challenge_%2833181655046%29.jpg',
    width: 1500,
    height: 1300,
    focus: '50% 38%',
  },
  school_term: {
    key: 'school_term',
    alt: 'Two schoolgirls in white uniforms and headscarves share a computer. One uses the keyboard while both look at the screen, with other pupils at computers behind them.',
    author: 'Queen Asali',
    license: 'CC BY-SA 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0',
    filePage: 'https://commons.wikimedia.org/wiki/File:Girls_using_a_computer_in_Kenya.jpg',
    thumbPath: '2/2d/Girls_using_a_computer_in_Kenya.jpg',
    fileName: 'Girls_using_a_computer_in_Kenya.jpg',
    width: 5568,
    height: 3712,
    focus: '40% 40%',
  },
  saturday_club: {
    key: 'saturday_club',
    alt: 'A teacher in a patterned shirt leans over a bench to help four young children working on laptops in a plain classroom.',
    author: 'Advancedsolver',
    license: 'CC BY-SA 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0',
    filePage: 'https://commons.wikimedia.org/wiki/File:Introducing_digital_classroom.jpg',
    thumbPath: '5/55/Introducing_digital_classroom.jpg',
    fileName: 'Introducing_digital_classroom.jpg',
    width: 4000,
    height: 3000,
    focus: '55% 45%',
  },
  holiday_camp: {
    key: 'holiday_camp',
    alt: 'Two students in yellow team shirts set a small robot down on a mission table in a gymnasium while adults in referee shirts and other team members look on.',
    author: 'U.S. Air Force photo/Holly Peterson',
    license: 'Public domain',
    licenseUrl: null,
    filePage: 'https://commons.wikimedia.org/wiki/File:Local_students_participate_in_FIRST%C2%AE_LEGO%C2%AE_League_Regional_Qualifier_Tournament.jpg',
    thumbPath: '8/89/Local_students_participate_in_FIRST%C2%AE_LEGO%C2%AE_League_Regional_Qualifier_Tournament.jpg',
    fileName: 'Local_students_participate_in_FIRST%C2%AE_LEGO%C2%AE_League_Regional_Qualifier_Tournament.jpg',
    width: 3264,
    height: 2448,
    focus: '65% 70%',
  },
  robot: {
    key: 'robot',
    alt: 'A small wheeled robot built from grey and white LEGO bricks, with a control brick and sensors, on a wooden floor.',
    author: 'Eirik Refsdal from Trondheim, NORWAY',
    license: 'CC BY 2.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/2.0',
    filePage: 'https://commons.wikimedia.org/wiki/File:Lego_Mindstorms_Nxt-FLL.jpg',
    thumbPath: '8/8c/Lego_Mindstorms_Nxt-FLL.jpg',
    fileName: 'Lego_Mindstorms_Nxt-FLL.jpg',
    width: 3456,
    height: 2304,
    focus: '50% 50%',
  },
}

/** Thumbnail URL at one of the published widths. */
export function imageUrl(image: BrandImage, width: (typeof IMAGE_WIDTHS)[number]): string {
  return `${COMMONS}/${image.thumbPath}/${width}px-${image.fileName}`
}

/** `srcset` covering every published width, capped at the original's own width. */
export function imageSrcset(image: BrandImage): string {
  return IMAGE_WIDTHS
    .filter(width => width <= image.width)
    .map(width => `${imageUrl(image, width)} ${width}w`)
    .join(', ')
}

/** Credit line shown next to the photograph. */
export function imageCredit(image: BrandImage): string {
  return `Photo: ${image.author}, ${image.license}`
}

/**
 * On-brand SVG shown when a photograph cannot load. It is decorative; the surrounding
 * alt text and caption still describe what the photograph would have shown.
 */
export function getPlaceholderSvg(): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600" fill="none">
  <rect width="800" height="600" fill="#160D35"/>
  <rect x="80" y="360" width="150" height="90" fill="#F6479A"/>
  <rect x="230" y="360" width="150" height="90" fill="#F9C41D"/>
  <rect x="155" y="270" width="150" height="90" fill="#8C2ACA"/>
  <rect x="305" y="270" width="150" height="90" fill="#FFFFFF" fill-opacity="0.9"/>
  <rect x="230" y="180" width="150" height="90" fill="#F6479A"/>
  <circle cx="620" cy="170" r="70" fill="#8C2ACA" fill-opacity="0.5"/>
</svg>`
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}
