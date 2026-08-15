# CAPPED — public website

This folder is the **deploy-ready static site** for CAPPED. It exists so the app has a
publicly hosted Privacy Policy URL, which App Store Connect requires before submission.

Everything here is plain HTML and CSS. No build step is required to deploy, no JavaScript
runs on any page, and nothing is fetched from a CDN or a font service. Each page is fully
self-contained — the logo is embedded directly in the HTML as a base64 data URI.

See **[DEPLOY.md](DEPLOY.md)** for the exact steps to get this online.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Landing page — hero, how it works, features, pricing, download |
| `privacy.html` | Privacy Policy (the URL App Store Connect needs) |
| `terms.html` | Terms of Use, including the Health and Training Disclaimer |
| `404.html` | Branded not-found page (GitHub Pages serves this automatically) |
| `privacy-policy.html` | Redirect stub → `privacy.html`, so the old filename keeps working |

Every page carries the same sticky nav (Home / Privacy / Terms + Get the App) and the same
footer, so the legal pages no longer look like a different website to the landing page.

## Supporting files

| File | Purpose |
|---|---|
| `logo-mark.png` | Master logo, 512×512 with transparency. Used for `og:image` and as the source of truth if you need the artwork elsewhere. |
| `assets/logo-mark-256.png` | 256×256, 128-colour palette build. Inlined into every page at build time. |
| `assets/favicon-64.png` | 64×64 favicon. Also inlined. |
| `.nojekyll` | Tells GitHub Pages to serve the files as-is instead of running them through Jekyll. |
| `build.py` | Regenerates the four HTML pages. Optional — not needed to deploy. |

## Design

Brand tokens are declared once per page as CSS custom properties:

| Token | Value | Used for |
|---|---|---|
| `--bg` | `#0B0E0C` | Page background |
| `--bg2` | `#141714` | Section bands, page headers |
| `--card` | `#191D19` | Cards, contents panel |
| `--ink` | `#F2EDE2` | Primary text |
| `--muted` | `#8E948B` | Secondary text |
| `--gold` | `#C8A86A` | Accent, links, primary button |
| `--line` | `rgba(242,237,226,0.10)` | Hairline borders |

Type is the system font stack (`-apple-system`, `Segoe UI`, `Roboto`, …) so there is no
web-font download and no layout shift while fonts load.

Layout notes:

- Legal prose is capped at `68ch` with a `1.75` line height. On a phone this lands at
  roughly 60–70 characters per line, which is the readable range for long documents.
- The table of contents is a sticky sidebar at ≥900px and a plain card above the text
  below that. It is pure CSS — no JavaScript, no collapse toggle.
- The two data tables in the Privacy Policy collapse from two columns into stacked
  label/value rows below 560px, so nothing is squeezed on a phone.
- Legal pages have a print stylesheet: nav, footer and contents are dropped and the text
  prints as black on white.

Accessibility choices worth knowing about, since the App Store review will poke at these:

- Skip-to-content link on every page.
- Focus rings are a 2px gold outline with a 3px offset (WCAG 2.2 §2.4.11).
- Nav, footer and contents links are padded to at least 24×24px (WCAG 2.2 §2.5.8).
- Text contrast is ≥6:1 everywhere; gold on the dark background is ~8.5:1.
- The logo is decorative (`aria-hidden`) because the word CAPPED sits next to it in the
  nav and footer, so screen readers do not announce it twice.
- `prefers-reduced-motion` disables smooth scrolling and transitions.

## Editing the legal wording

**Do not hand-edit the prose inside `privacy.html` or `terms.html`.** Those pages are
generated, and the wording is copied character-for-character from the authored source
documents in `../marketing/`:

- `../marketing/privacy-policy.html`
- `../marketing/terms.html`
- `../marketing/landing-page.html`

Edit the source document, then regenerate:

```bash
cd ~/Desktop/CAPPED/site
python3 build.py
```

That rebuilds `index.html`, `privacy.html`, `terms.html`, `404.html` and the redirect stub
from the shared shell, and re-inlines the logo. It only ever reads from `../marketing/` —
it never writes there. Python 3.8+ with no third-party packages.

If you have moved the sources, point at them explicitly:

```bash
python3 build.py --src /path/to/marketing
```

The nav, footer, colours and typography live in `build.py` (the `CSS_CORE`, `CSS_LANDING`,
`CSS_LEGAL` and `CSS_404` blocks). Change them there so all four pages stay in step —
editing one page's `<style>` block by hand will be overwritten on the next build.

## Preview locally

```bash
cd ~/Desktop/CAPPED/site
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Ports 8081 (Metro) and 5178 (reel engine) are used by
the rest of the project, so 8000 stays free.

Opening the files directly with `file://` also works, since there are no fetches.

## Still to do after launch

1. **App Store link.** The App Store button on the landing page currently points at
   `#download` and is marked with a `TODO` comment in `build.py`. Swap in the real
   listing URL once CAPPED is live.
2. **Absolute URLs for social previews.** `og:image` is relative. Once the final domain is
   known, make it absolute so link previews render on every platform, and add a
   `<link rel="canonical">` to each page.
3. **Keep the in-app policy in sync.** `app/src/legal.ts` carries its own copy of the
   policy text. Two different policies for one service is a compliance problem — when the
   wording changes, update both.
4. `../marketing/HOSTING.md` describes an older plan targeting a repo named `capped-legal`
   with three loose files. `DEPLOY.md` in this folder supersedes it.
