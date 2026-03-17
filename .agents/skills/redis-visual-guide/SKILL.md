---
name: redis-visual-guide
description: >-
  Use when building frontend apps or UI components.
license: See LICENSE in repository root
metadata:
  author: redis
  version: "1.0"
  category: reference
  triggers: frontend, UI, colors, typography, brand, theme, icons, buttons
---

## Typography

Use `rem` for measurements that should scale with the root font size, and keep `px` for intentionally pixel-specific or optical values. Base conversion: `1rem = 16px`.

Redis uses two font families, assigned to CSS custom properties.

### Font Families

| Variable           | Font Family   | Type       | Weights       | Usage                                                                            |
| ------------------ | ------------- | ---------- | ------------- | -------------------------------------------------------------------------------- |
| `--primary-font`   | Space Grotesk | Sans-serif | 400, 500, 700 | Large display headings (h1, hero text), Body text, smaller headings, buttons, UI |
| `--secondary-font` | Space Mono    | Monospace  | 400, 700      | Code, eyebrow labels, technical text                                             |

Always include a `sans-serif` fallback for primary and primary fonts, and `monospace` for the secondary font.

### Heading Scale

Headings use the primary font at large display sizes and transition to the primary font for smaller headings.

| Size Token | Font               | Desktop Size | Mobile Size | Line Height | Notes                           |
| ---------- | ------------------ | ------------ | ----------- | ----------- | ------------------------------- |
| `3xl`      | `--primary-font`   | 11.25rem     | 5.25rem     | 90%         | letter-spacing: -0.01em         |
| `2xl`      | `--primary-font`   | 6.25rem      | 5rem        | 85%         | uppercase, letter-spacing: -1px |
| `xl`       | `--primary-font`   | 7.5rem       | 5rem        | 82%         | letter-spacing: -0.01em         |
| `lg`       | `--primary-font`   | 4rem         | 2.5rem      | 105%        |                                 |
| `md`       | `--primary-font`   | 3.125rem     | 1.875rem    | 110%        | letter-spacing: -0.02em         |
| `rg`       | `--primary-font`   | 2.5rem       | 1.875rem    | 105%        |                                 |
| `sm`       | `--primary-font`   | 1.625rem     | 1.375rem    | 1.9375rem   |                                 |
| `xs`       | `--secondary-font` | 0.875rem     | 0.75rem     | 1.05rem     | letter-spacing: 1px             |

### Body Text Scale

Body text always uses `--primary-font` (Space Grotesk).

| Size Token | Desktop Size | Mobile Size | Line Height |
| ---------- | ------------ | ----------- | ----------- |
| `3xl`      | 2rem         | 1.5rem      | 120%        |
| `2xl`      | 1.5rem       | —           | 120%        |
| `xl`       | 1.375rem     | —           | —           |
| `lg`       | 1.25rem      | —           | 145%        |
| `md`       | 1.125rem     | —           | 150%        |
| `sm`       | 1rem         | 0.875rem    | 160%        |
| `rg`       | 0.875rem     | 0.75rem     | 150%        |
| `xs`       | 0.75rem      | —           | 150%        |
| `2xs`      | 0.625rem     | —           | 150%        |

### Font Weights

| Token      | Weight |
| ---------- | ------ |
| `regular`  | 400    |
| `medium`   | 500    |
| `semibold` | 600    |
| `bold`     | 700    |

## Colors

### Brand Core

| Name          | Variable          | Hex       | Usage                          |
| ------------- | ----------------- | --------- | ------------------------------ |
| Primary Color | `--primary-color` | `#FF4438` | Primary brand color            |
| Midnight      | `--midnight`      | `#091A23` | Dark backgrounds, primary text |
| Yellow (Volt) | `--yellow`        | `#DCFF1E` | Accent on dark, highlights     |
| White         | `--base-white`    | `#FFFFFF` | Light backgrounds              |
| Black         | `--base-black`    | `#000000` | —                              |

### Red / Hyper Scale

The primary action color scale, used for buttons, links, and interactive elements.

| Name     | Variable     | Hex       | Usage                           |
| -------- | ------------ | --------- | ------------------------------- |
| Hyper 04 | `--hyper-04` | `#FD736A` | Light red, hover accents        |
| Hyper 05 | `--hyper-05` | `#FF4438` | Same as Primary Color           |
| Hyper 06 | `--hyper-06` | `#EB352A` | Slightly darker red             |
| Hyper 07 | `--hyper-07` | `#E4291E` | Primary button bg, links        |
| Hyper 08 | `--hyper-08` | `#D1281E` | Button hover bg                 |
| Hyper 09 | `--hyper-09` | `#8A221C` | Deep red, active states         |
| Hyper 10 | `--hyper-10` | `#351D22` | Darkest red, dark theme buttons |

### Neutrals (Black Scale)

| Name     | Variable     | Hex       |
| -------- | ------------ | --------- |
| Black 90 | `--black-90` | `#191919` |
| Black 70 | `--black-70` | `#4C4C4C` |
| Black 60 | `--black-60` | `#6D6E71` |
| Black 50 | `--black-50` | `#808080` |
| Black 30 | `--black-30` | `#B2B2B2` |
| Black 10 | `--black-10` | `#E5E5E5` |

### Neutrals (Grey Scale)

| Name       | Variable       | Hex       |
| ---------- | -------------- | --------- |
| Grey 50    | `--grey-50`    | `#F9FAFB` |
| Grey 20    | `--grey-20`    | `#E9E9E9` |
| Grey 10    | `--grey-10`    | `#FCFCFC` |
| Light Gray | `--light-gray` | `#F8F8F8` |

### Dusk Scale (Blue-Grey)

Used for dark themes, muted text, borders, and subtle backgrounds.

| Name    | Variable    | Hex       | Usage                            |
| ------- | ----------- | --------- | -------------------------------- |
| Dusk    | `--dusk`    | `#163341` | Dark UI surfaces                 |
| Dusk 01 | `--dusk-01` | `#F3F3F3` | Light primary button bg          |
| Dusk 09 | `--dusk-09` | `#0D212C` | Deepest dark surface             |
| Dusk 90 | `--dusk-90` | `#2D4754` | Dark surface variant             |
| Dusk 50 | `--dusk-50` | `#8A99A0` | Placeholder text, dividers       |
| Dusk 30 | `--dusk-30` | `#B9C2C6` | Borders, muted text (dark theme) |
| Dusk 10 | `--dusk-10` | `#D9D9D9` | Borders, body text (dark theme)  |

### Yellow / Volt Scale

Used as an accent color, especially on dark backgrounds.

| Name      | Variable      | Hex       |
| --------- | ------------- | --------- |
| Yellow    | `--yellow`    | `#DCFF1E` |
| Yellow 06 | `--yellow-06` | `#D0F41D` |
| Yellow 07 | `--yellow-07` | `#BFE112` |
| Yellow 08 | `--yellow-08` | `#A9CA03` |
| Yellow 09 | `--yellow-09` | `#8CAA00` |
| Yellow 11 | `--yellow-11` | `#4E5F02` |
| Yellow 50 | `--yellow-50` | `#F1FFA5` |
| Yellow 10 | `--yellow-10` | `#FBFFE8` |

### Purple Scale

| Name      | Variable      | Hex       |
| --------- | ------------- | --------- |
| Purple 05 | `--purple-05` | `#B76BE2` |
| Purple 07 | `--purple-07` | `#8F2EC4` |
| Violet    | `--violet`    | `#C795E3` |
| Violet 90 | `--violet-90` | `#5925E8` |
| Violet 50 | `--violet-50` | `#E3CAF1` |
| Violet 10 | `--violet-10` | `#F9F4FC` |
| Violet 09 | `--violet-09` | `#592479` |

### Sky Blue Scale

| Name        | Variable        | Hex       |
| ----------- | --------------- | --------- |
| Sky Blue    | `--sky-blue`    | `#80DBFF` |
| Sky Blue 50 | `--sky-blue-50` | `#BFEDFF` |
| Sky Blue 10 | `--sky-blue-10` | `#F2FBFF` |
| Sky Blue 09 | `--sky-blue-09` | `#0477A5` |
| Light Blue  | `--light-blue`  | `#F9FDFF` |

## Theming

Redis uses a dark theme

### Dark Theme

| Semantic Token     | Maps To        | Resolved Value |
| ------------------ | -------------- | -------------- |
| `--bg-default`     | `--midnight`   | `#091A23`      |
| `--fg-default`     | `--base-white` | `#FFFFFF`      |
| `--fg-body`        | `--dusk-10`    | `#D9D9D9`      |
| `--fg-muted`       | `--dusk-30`    | `#B9C2C6`      |
| `--fg-brand`       | `--yellow`     | `#DCFF1E`      |
| `--border`         | `--dusk`       | `#163341`      |
| `--stroke-divider` | `--dusk-50`    | `#8A99A0`      |

## Buttons

### Primary Button (Dark Theme)

| State   | Background   | Border       | Text Color     |
| ------- | ------------ | ------------ | -------------- |
| Default | `--hyper-10` | `--hyper-05` | `--base-white` |
| Hover   | `--hyper-09` | `--hyper-06` | `--base-white` |
| Active  | `--hyper-09` | `--hyper-06` | `--base-white` |

### Secondary Button (Dark Theme)

| State   | Background  | Border      | Text Color     |
| ------- | ----------- | ----------- | -------------- |
| Default | `--dusk`    | `--dusk-90` | `--base-white` |
| Hover   | `--dusk-90` | `--dusk-70` | `--base-white` |
| Active  | `--dusk-90` | `--dusk-70` | `--base-white` |

### Button Styling

- Font: `--primary-font` (Space Grotesk), 0.875rem, weight 500
- Border: 1px solid
- Variants: `pill` (border-radius: 200px), `rounded` (border-radius: 5px), `square` (border-radius: 0)
- Size tokens: `xs` (0.25rem 0.5rem), `sm` (0.5rem 0.75rem), `md` (0.625rem 1.5rem), `lg` (0.9375rem 2.25rem)

## Spacing Tokens

| Token | Desktop | Mobile |
| ----- | ------- | ------ |
| `xs`  | 1rem    | 1rem   |
| `sm`  | 1.5rem  | 1.5rem |
| `md`  | 2.5rem  | 2rem   |
| `rg`  | 3rem    | 2.625rem |
| `lg`  | 4.5rem  | 3.875rem |
| `xl`  | 6rem    | 3.75rem |

## Layout

- Max container width: 86.875rem (80rem below 100rem viewport)
- Container padding: 1.5rem (5rem between 78.75rem–100rem viewport)
- Base font size: 16px (1rem)
- Text rendering: `optimizeLegibility` with `-webkit-font-smoothing: antialiased`

## Redis Logo

The official Redis logo is available in four color variants as SVG files.

Directory: `assets/Redis Logo/`

| Variant  | File                          | Usage                                      |
| -------- | ----------------------------- | ------------------------------------------ |
| Red      | `Redis_Logo_Red_RGB.svg`      | Primary logo on light backgrounds          |
| Black    | `Redis_Logo_Black_RGB.svg`    | Monochrome use on light backgrounds        |
| Midnight | `Redis_Logo_Midnight_RGB.svg` | Dark-toned logo for dark-themed contexts   |
| White    | `Redis_Logo_White_RGB.svg`    | Logo for use on dark backgrounds           |

## Icons

For icon assets (Generic Marketing, Product Feature, Industry, and Redis Proprietary icons), see [references/icons.md](references/icons.md).
