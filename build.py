#!/usr/bin/env python3
"""
CAPPED static site builder.

Generates the deployable pages in this folder from a single shared shell
(nav, footer, colour tokens, typography) so the four pages can never drift
apart visually.

  index.html    landing page      <- body copy lifted verbatim from SRC/landing-page.html
  privacy.html  privacy policy    <- body copy lifted verbatim from SRC/privacy-policy.html
  terms.html    terms of use      <- body copy lifted verbatim from SRC/terms.html
  404.html      not found
  privacy-policy.html             redirect stub -> privacy.html (old filename)

The legal wording is never rewritten here: the <section> blocks, the intro
paragraphs, the notice box and the contents list are copied across character
for character. Only the surrounding shell is this script's business.

Usage:  python3 build.py            (run from inside the site/ folder)
        python3 build.py --src /path/to/marketing

Requires Python 3.8+. No third-party packages.
"""

import argparse
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.abspath(os.path.join(HERE, "..", "marketing"))

EMAIL = "cappedhq@gmail.com"
YEAR = "2026"

# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------


def data_uri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


# --------------------------------------------------------------------------
# css
# --------------------------------------------------------------------------

CSS_CORE = """
  :root{
    --bg:#0B0E0C;
    --bg2:#141714;
    --card:#191D19;
    --ink:#F2EDE2;
    --muted:#8E948B;
    --gold:#C8A86A;
    --gold-dim:rgba(200,168,106,0.15);
    --line:rgba(242,237,226,0.10);
    --pitch:rgba(46,92,58,0.28);
    --max:1120px;
    --logo:url("__LOGO__");
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
  body{
    background:var(--bg);
    color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  a{color:inherit;text-decoration:none}
  img{max-width:100%;height:auto;display:block}
  .wrap{max-width:var(--max);margin:0 auto;padding:0 24px}

  /* WCAG 2.2 - 2.4.11 focus appearance */
  :focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:6px}

  .skip{
    position:absolute;left:-9999px;top:0;z-index:100;
    background:var(--gold);color:#161206;font-weight:800;font-size:14px;
    padding:12px 18px;border-radius:0 0 10px 0;
  }
  .skip:focus{left:0}

  /* ---------- brand mark (inlined logo, no network request) ---------- */
  .brand-mark{
    display:block;flex:none;
    width:30px;height:30px;
    background-image:var(--logo);
    background-size:contain;background-repeat:no-repeat;background-position:center;
  }

  /* ---------- nav ---------- */
  .site-nav{
    position:sticky;top:0;z-index:50;
    background:rgba(11,14,12,0.86);
    backdrop-filter:saturate(160%) blur(14px);
    -webkit-backdrop-filter:saturate(160%) blur(14px);
    border-bottom:1px solid var(--line);
  }
  .nav-in{display:flex;align-items:center;justify-content:space-between;gap:16px;height:64px}
  .brand{display:flex;align-items:center;gap:10px;padding:4px 0}
  .brand-word{font-size:14px;letter-spacing:5px;font-weight:800;line-height:1}
  .nav-right{display:flex;align-items:center;gap:10px}
  .nav-links{display:flex;align-items:center;gap:4px;list-style:none}
  .nav-links a{
    display:inline-block;padding:8px 10px;font-size:14px;font-weight:600;
    color:var(--muted);border-radius:8px;transition:color .15s ease;
  }
  .nav-links a:hover{color:var(--ink)}
  .nav-links a[aria-current="page"]{color:var(--gold)}

  .btn{
    /* inline-flex + line-height:1 so the label sits on the true vertical centre.
       With the inherited 1.6 line-height the text rendered ~3.6px high in the
       larger button, because Latin ascent exceeds descent. */
    display:inline-flex;align-items:center;justify-content:center;
    line-height:1;text-align:center;
    border-radius:10px;font-weight:800;
    padding:15px 20px;font-size:14px;letter-spacing:.2px;
    transition:transform .15s ease,opacity .15s ease;
  }
  .btn:active{transform:scale(.97)}
  .btn-gold{background:var(--gold);color:#161206}
  .btn-ghost{border:1px solid var(--line);color:var(--ink)}
  .btn-lg{padding:20px 30px;font-size:16px;border-radius:12px}

  .eyebrow{
    display:inline-flex;align-items:center;gap:8px;
    border:1px solid var(--line);border-radius:999px;
    padding:6px 14px;font-size:11px;letter-spacing:2px;
    font-weight:700;color:var(--gold);
  }
  .dot{width:6px;height:6px;border-radius:50%;background:var(--gold)}

  /* ---------- footer ---------- */
  .site-foot{border-top:1px solid var(--line);padding:44px 0;color:var(--muted);font-size:14px}
  .foot-in{display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between}
  .foot-brand{display:flex;align-items:center;gap:12px}
  .foot-brand .brand-mark{width:34px;height:34px}
  .foot-name{color:var(--ink);font-size:13px;letter-spacing:4px;font-weight:800;line-height:1.3}
  .foot-note{font-size:13px;margin-top:2px}
  .foot-links{display:flex;flex-wrap:wrap;gap:6px 18px}
  .foot-links a{display:inline-block;padding:5px 0;transition:color .15s ease}
  .foot-links a:hover{color:var(--gold)}

  @media (max-width:720px){
    .nav-cta{display:none}
  }
  @media (max-width:420px){
    .wrap{padding:0 18px}
    .brand-word{letter-spacing:3.5px;font-size:13px}
    .brand-mark{width:26px;height:26px}
    .nav-links a{font-size:13px;padding:8px 7px}
  }
  @media (max-width:640px){
    .foot-in{flex-direction:column;align-items:flex-start;gap:20px}
  }
  @media (prefers-reduced-motion:reduce){
    html{scroll-behavior:auto}
    *{transition-duration:.01ms !important;animation-duration:.01ms !important}
  }
"""

CSS_LANDING = """
  body{overflow-x:hidden}

  /* ---------- hero ---------- */
  .hero-band{
    position:relative;
    min-height:calc(100svh - 64px);
    display:flex;align-items:center;
    padding:64px 0 64px;
    overflow:hidden;
  }
  .hero-band::before{
    content:"";position:absolute;inset:0;z-index:0;
    background:
      /* one warm bloom sitting behind the headline, not in a corner */
      radial-gradient(74% 60% at 26% 58%, rgba(46,92,58,0.30) 0%, transparent 62%),
      /* a smaller gold catch opposite, for depth rather than decoration */
      radial-gradient(54% 46% at 86% 16%, rgba(200,168,106,0.10) 0%, transparent 64%);
  }
  /* Grain + vignette replace the diagonal stripe overlay, which read as a
     dated motif. The noise alpha is knocked down inside the SVG itself
     (feFuncA slope 0.09) — painted at full strength it lifts the black to
     grey and looks like TV static. Kept off ::before so the drift animation
     never scales the grain. */
  .hero-band::after{
    content:"";position:absolute;inset:0;z-index:0;pointer-events:none;
    background-image:
      radial-gradient(118% 90% at 46% 44%, transparent 38%, rgba(0,0,0,0.60) 100%),
      url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20width%3D%27180%27%20height%3D%27180%27%3E%3Cfilter%20id%3D%27n%27%3E%3CfeTurbulence%20type%3D%27fractalNoise%27%20baseFrequency%3D%270.9%27%20numOctaves%3D%273%27%20stitchTiles%3D%27stitch%27%2F%3E%3CfeColorMatrix%20type%3D%27saturate%27%20values%3D%270%27%2F%3E%3CfeComponentTransfer%3E%3CfeFuncA%20type%3D%27linear%27%20slope%3D%270.09%27%2F%3E%3C%2FfeComponentTransfer%3E%3C%2Ffilter%3E%3Crect%20width%3D%27180%27%20height%3D%27180%27%20filter%3D%27url%28%23n%29%27%2F%3E%3C%2Fsvg%3E");
    background-size:auto, 180px 180px;
  }

  .hero{position:relative;z-index:1;max-width:760px}
  .hero-mark{width:88px;height:88px;margin-bottom:26px}
  .hero .eyebrow{margin-bottom:26px}
  h1{
    font-size:clamp(44px,9vw,82px);
    line-height:1.02;letter-spacing:-2.2px;font-weight:800;
  }
  h1 .accent{color:var(--gold)}
  .sub{
    color:var(--muted);font-size:clamp(16px,2.3vw,20px);
    margin-top:22px;max-width:560px;line-height:1.55;
  }
  .cta-row{display:flex;flex-wrap:wrap;gap:14px;margin-top:38px}
  .fine{color:var(--muted);font-size:13px;margin-top:20px}

  /* ---------- proof bar ---------- */
  .proof{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--bg2)}
  .proof-in{padding-top:26px;padding-bottom:26px;text-align:center}
  .proof-label{color:var(--muted);font-size:12px;letter-spacing:2.5px;font-weight:700;text-transform:uppercase}
  .chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:16px}
  .chip{
    border:1px solid var(--line);border-radius:999px;
    padding:8px 16px;font-size:13px;font-weight:600;
    background:var(--card);
  }
  .chip b{color:var(--gold);font-weight:800}

  /* ---------- sections ---------- */
  section{padding:88px 0}
  .band{background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
  .sec-head{max-width:620px;margin-bottom:48px}
  .kicker{color:var(--gold);font-size:12px;letter-spacing:3px;font-weight:800;text-transform:uppercase}
  h2{font-size:clamp(30px,5vw,44px);line-height:1.1;letter-spacing:-1.2px;font-weight:800;margin-top:12px}
  .sec-head p{color:var(--muted);margin-top:14px;font-size:17px}

  .grid{display:grid;gap:18px}
  .g3{grid-template-columns:repeat(3,1fr)}
  .g2{grid-template-columns:repeat(2,1fr)}
  .g4{grid-template-columns:repeat(4,1fr)}

  .card{
    --mx:50%;--my:50%;
    background:var(--card);border:1px solid var(--line);
    border-radius:16px;padding:28px;
    /* Hover treatment. Deliberately restrained — a big bounce reads as cheap.
       transform + opacity only, so it stays on the compositor and never
       triggers layout. */
    position:relative;
    transition:transform .38s cubic-bezier(.22,.7,.28,1),
               border-color .38s ease,
               background-color .38s ease,
               box-shadow .38s ease;
  }
  /* A hairline of gold that grows out from the centre of the top edge —
     like light catching a machined surface. */
  .card::after{
    content:"";position:absolute;top:-1px;left:50%;
    width:0;height:1px;
    background:linear-gradient(90deg,transparent,var(--gold),transparent);
    transform:translateX(-50%);
    transition:width .45s cubic-bezier(.22,.7,.28,1);
    pointer-events:none;
  }
  @media (hover:hover){
    .card:hover{
      transform:translateY(-6px);
      border-color:rgba(200,168,106,.42);
      background-color:#161915;
      box-shadow:0 22px 44px -22px rgba(0,0,0,.85);
    }
    .card:hover::after{width:72%}
    .card:hover .ic{transform:translateY(-2px) scale(1.07)}
  }
  .card .ic{transition:transform .38s cubic-bezier(.22,.7,.28,1)}
  /* Touch devices get the same feedback on press, minus the hover-only lift. */
  .card:active{transform:translateY(-2px);border-color:rgba(200,168,106,.42)}
  @media (prefers-reduced-motion:reduce){
    .card,.card::after,.card .ic{transition:none}
    .card:hover{transform:none}
    .card:hover::after{width:0}
    .card:hover .ic{transform:none}
  }
  /* Pointer-tracked glow. ::after is already the top accent, so this uses
     ::before, and card children are lifted above it — a positioned pseudo
     element would otherwise paint over the text. */
  .card::before{
    content:"";position:absolute;inset:0;border-radius:inherit;
    background:radial-gradient(320px circle at var(--mx) var(--my),
               rgba(200,168,106,.11), transparent 62%);
    opacity:0;transition:opacity .4s ease;pointer-events:none;z-index:0;
  }
  .card > *{position:relative;z-index:1}
  @media (hover:hover){ .card:hover::before{opacity:1} }

  /* ---------- scroll reveal (applied by JS, so no-JS shows everything) */
  [data-reveal]{
    opacity:0;transform:translateY(14px);
    transition:opacity .68s cubic-bezier(.22,.7,.28,1),
               transform .68s cubic-bezier(.22,.7,.28,1);
  }
  [data-reveal].is-in{opacity:1;transform:none}

  /* ---------- nav condenses on scroll */
  .site-nav.is-scrolled{
    background:rgba(11,14,12,0.94);
    backdrop-filter:saturate(180%) blur(20px);
    -webkit-backdrop-filter:saturate(180%) blur(20px);
    border-bottom-color:rgba(200,168,106,.16);
    box-shadow:0 10px 30px -20px rgba(0,0,0,.9);
  }
  .site-nav .nav-in{transition:height .32s cubic-bezier(.22,.7,.28,1)}
  .site-nav.is-scrolled .nav-in{height:56px}

  /* ---------- hero ambient drift: 26s, barely perceptible */
  @keyframes capped-drift{
    from{transform:translate3d(0,0,0) scale(1)}
    to{transform:translate3d(0,-2.2%,0) scale(1.06)}
  }
  @media (prefers-reduced-motion:no-preference){
    header::before{animation:capped-drift 26s ease-in-out infinite alternate}
  }

  /* ---------- pricing: make the tier you want people on feel like the default */
  .price-card{transition:transform .38s cubic-bezier(.22,.7,.28,1),
                         border-color .38s ease, box-shadow .38s ease}
  .price-card.pop{
    box-shadow:0 0 0 1px rgba(200,168,106,.16),
               0 30px 70px -40px rgba(200,168,106,.34);
  }
  @media (hover:hover){
    .price-card:hover{transform:translateY(-5px);border-color:rgba(200,168,106,.42)}
    .price-card.pop:hover{box-shadow:0 0 0 1px rgba(200,168,106,.3),
                                    0 34px 80px -38px rgba(200,168,106,.44)}
  }

  @media (prefers-reduced-motion:reduce){
    [data-reveal]{opacity:1;transform:none;transition:none}
    .price-card,.site-nav .nav-in{transition:none}
    .price-card:hover{transform:none}
  }

  .step-n{
    width:38px;height:38px;border-radius:10px;
    background:var(--gold-dim);border:1px solid rgba(200,168,106,0.35);
    color:var(--gold);font-weight:800;font-size:15px;
    display:flex;align-items:center;justify-content:center;margin-bottom:18px;
  }
  .card h3{font-size:19px;font-weight:700;letter-spacing:-.3px}
  .card p{color:var(--muted);margin-top:8px;font-size:15px}

  .feat{padding:24px}
  .feat .ic{font-size:24px;margin-bottom:12px;display:block}
  .feat h3{font-size:16px}
  .feat p{font-size:14px;margin-top:6px}

  /* ---------- pricing ---------- */
  .price-card{position:relative;display:flex;flex-direction:column}
  .price-card.pop{border-color:rgba(200,168,106,0.45);background:linear-gradient(180deg,rgba(200,168,106,0.06),var(--card))}
  .badge{
    position:absolute;top:-11px;left:24px;
    background:var(--gold);color:#161206;
    font-size:10px;font-weight:800;letter-spacing:1.5px;
    padding:4px 11px;border-radius:999px;
  }
  .tier{font-size:13px;letter-spacing:2px;font-weight:800;color:var(--muted);text-transform:uppercase}
  .amt{font-size:36px;font-weight:800;letter-spacing:-1.5px;margin:10px 0 2px}
  .amt span{font-size:14px;color:var(--muted);font-weight:600;letter-spacing:0}
  .price-card ul{list-style:none;margin-top:18px;flex:1}


  /* ---------- Pricing: frosted cards over a large ghost word ----------
     The depth trick from the reference: an oversized word sits behind the row
     and is blurred *through* the cards by backdrop-filter, so the cards read as
     real glass rather than flat panels. */
  .price-stage{position:relative}
  .price-ghost{
    position:absolute;left:50%;top:-2px;transform:translateX(-50%);
    font-size:clamp(90px,15vw,210px);font-weight:800;letter-spacing:-.04em;
    line-height:.82;color:rgba(242,237,226,.055);
    white-space:nowrap;pointer-events:none;user-select:none;z-index:0;
  }
  .price-grid{position:relative;z-index:1}

  .price-card{
    display:flex;flex-direction:column;padding:0;overflow:hidden;
    background:rgba(22,25,22,.55);
    backdrop-filter:blur(26px) saturate(140%);
    -webkit-backdrop-filter:blur(26px) saturate(140%);
    border:1px solid rgba(242,237,226,.09);
  }
  .price-head{padding:26px 24px 22px;border-bottom:1px solid rgba(242,237,226,.08)}
  .price-card .tier{
    font-size:12px;letter-spacing:2.2px;font-weight:800;text-transform:uppercase;
    color:var(--muted);margin-bottom:10px;
  }
  .price-card .amt{font-size:38px;font-weight:800;letter-spacing:-1.6px;color:var(--ink)}
  .price-card .amt span{font-size:15px;font-weight:600;color:var(--muted);letter-spacing:0}

  .price-feats{list-style:none;margin:0;padding:22px 24px 8px;flex:1}
  .price-feats li{
    display:flex;align-items:flex-start;gap:11px;
    color:var(--muted);font-size:14px;line-height:1.5;margin-bottom:14px;
  }
  .tick{
    flex:none;width:21px;height:21px;border-radius:50%;
    display:inline-flex;align-items:center;justify-content:center;
    background:rgba(200,168,106,.14);border:1px solid rgba(200,168,106,.32);
    color:var(--gold);font-size:11px;font-weight:800;line-height:1;margin-top:1px;
  }

  .price-cta{
    margin:8px 24px 24px;padding:13px 18px;border-radius:11px;text-align:center;
    font-weight:800;font-size:14px;cursor:default;
    border:1px solid rgba(242,237,226,.14);color:var(--ink);
    background:rgba(242,237,226,.03);
    transition:background .3s ease,border-color .3s ease,color .3s ease;
  }
  .price-cta.is-primary{background:var(--gold);color:#161206;border-color:transparent}
  @media (hover:hover){
    .price-card:hover .price-cta{border-color:rgba(200,168,106,.45);background:rgba(200,168,106,.08)}
    .price-card:hover .price-cta.is-primary{background:#d4b578;border-color:transparent}
  }

  .price-card.pop{
    background:rgba(28,26,20,.62);
    border-color:rgba(200,168,106,.34);
  }
  .price-card.pop .badge{
    position:absolute;top:14px;right:16px;left:auto;
  }
  .price-card.pop .price-head{padding-top:26px}

  /* backdrop-filter is the whole effect; without it the cards would be flat
     translucent rectangles, so fall back to an opaque panel instead. */
  @supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
    .price-card{background:#141714}
    .price-card.pop{background:#1a1813}
    .price-ghost{color:rgba(242,237,226,.03)}
  }

  @media (max-width:900px){
    .price-ghost{font-size:clamp(70px,20vw,130px);top:-6px}
  }

  .price-note{color:var(--muted);font-size:13px;text-align:center;margin-top:26px}

  /* ---------- download ---------- */
  .dl{background:var(--bg2);border-top:1px solid var(--line);text-align:center}
  .dl h2{margin:0 auto}
  .dl p{color:var(--muted);margin:16px auto 32px;max-width:460px;font-size:17px}
  .store{
    display:inline-flex;align-items:center;justify-content:center;text-align:center;gap:12px;
    background:var(--ink);color:#0B0E0C;
    border-radius:12px;padding:13px 26px;font-weight:700;
    transition:transform .15s ease;
  }
  .store:active{transform:scale(.97)}
  .store svg{width:26px;height:26px;flex:none}
  .store .s1{display:block;font-size:10px;letter-spacing:.5px;opacity:.7;line-height:1.2}
  .store .s2{display:block;font-size:17px;font-weight:800;line-height:1.2}

  @media (max-width:900px){
    .g3,.g4{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:640px){
    section{padding:64px 0}
    .g2,.g3,.g4{grid-template-columns:1fr}
    .hero-band{min-height:auto;padding:52px 0 60px}
    .hero-mark{width:72px;height:72px;margin-bottom:22px}
    .cta-row .btn{flex:1;text-align:center}
  }
"""

CSS_LEGAL = """
  .wrap{max-width:1040px}

  /* ---------- page head ---------- */
  .legal-head{position:relative;overflow:hidden;border-bottom:1px solid var(--line);background:var(--bg2)}
  .legal-head::before{
    content:"";position:absolute;inset:0;z-index:0;
    background:
      radial-gradient(80% 70% at 12% 0%, var(--pitch) 0%, transparent 60%),
      radial-gradient(60% 60% at 96% 100%, rgba(200,168,106,0.12) 0%, transparent 62%);
  }
  .legal-head .wrap{position:relative;z-index:1;padding-top:56px;padding-bottom:48px}
  .legal-head h1{
    font-size:clamp(32px,6vw,52px);line-height:1.05;
    letter-spacing:-1.6px;font-weight:800;margin-top:20px;
  }
  .updated{color:var(--muted);font-size:14px;margin-top:14px}

  /* ---------- layout ---------- */
  /* NB: padding-block only - .legal-layout shares an element with .wrap, and a
     `padding` shorthand here would wipe out .wrap's horizontal gutter. */
  .legal-layout{display:grid;grid-template-columns:1fr;gap:36px;align-items:start;padding-top:44px;padding-bottom:72px}

  /* ---------- contents ---------- */
  .toc{
    background:var(--card);border:1px solid var(--line);
    border-radius:14px;padding:20px 22px;
  }
  .toc-title{
    font-size:11px;letter-spacing:2.4px;font-weight:800;
    color:var(--muted);text-transform:uppercase;margin-bottom:12px;
  }
  .toc ol{padding-left:22px;margin:0}
  .toc li{margin-bottom:2px;color:var(--muted);font-size:13px}
  .toc a{
    display:block;padding:6px 0;font-size:14px;
    color:var(--ink);line-height:1.35;transition:color .15s ease;
  }
  .toc a:hover{color:var(--gold);text-decoration:underline}

  /* ---------- prose ---------- */
  .prose{max-width:68ch;font-size:17px;line-height:1.75}
  .prose > p{color:rgba(242,237,226,0.86);margin-bottom:16px}
  .prose section{margin-bottom:44px;scroll-margin-top:88px}
  .prose h2{
    font-size:22px;font-weight:800;letter-spacing:-.4px;line-height:1.25;
    color:var(--ink);margin-bottom:18px;padding-bottom:12px;
    border-bottom:1px solid var(--line);
  }
  .prose h3{font-size:16px;font-weight:800;color:var(--gold);margin:26px 0 10px;letter-spacing:.1px}
  .prose p{color:rgba(242,237,226,0.86);margin-bottom:16px}
  .prose ul,.prose ol{padding-left:24px;margin-bottom:16px}
  .prose li{color:rgba(242,237,226,0.86);margin-bottom:8px;padding-left:2px}
  .prose li::marker{color:var(--gold)}
  .prose strong{color:var(--ink);font-weight:700}
  .prose a{color:var(--gold);text-decoration:underline;text-underline-offset:3px}
  .prose a:hover{text-decoration-thickness:2px}

  .notice{
    background:rgba(200,168,106,0.09);
    border:1px solid rgba(200,168,106,0.3);
    border-left-width:3px;
    border-radius:10px;
    padding:16px 18px;
    font-size:14px;line-height:1.6;
    color:var(--gold);
    margin-bottom:32px;
  }
  .renewal-box{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:10px;
    padding:18px 20px;
    margin:18px 0;
    font-size:15px;line-height:1.65;
    color:rgba(242,237,226,0.86);
  }

  /* ---------- tables ---------- */
  .prose table{
    width:100%;border-collapse:collapse;
    margin-bottom:22px;font-size:15px;
    border:1px solid var(--line);border-radius:12px;
  }
  .prose th{
    text-align:left;padding:11px 14px;
    background:rgba(242,237,226,0.05);
    color:var(--muted);font-size:11px;letter-spacing:1.2px;
    font-weight:800;text-transform:uppercase;
    border-bottom:1px solid var(--line);
  }
  .prose td{
    padding:12px 14px;color:rgba(242,237,226,0.86);
    border-bottom:1px solid rgba(242,237,226,0.06);
    vertical-align:top;line-height:1.6;
  }
  .prose tbody tr:last-child td{border-bottom:0}

  .totop{margin-top:8px;font-size:14px}
  .totop a{color:var(--muted);text-decoration:none}
  .totop a:hover{color:var(--gold)}

  @media (min-width:900px){
    .legal-layout{grid-template-columns:262px minmax(0,1fr);gap:56px;padding-top:56px;padding-bottom:88px}
    .toc{position:sticky;top:88px;max-height:calc(100vh - 116px);overflow-y:auto}
    .toc a{font-size:13.5px}
  }
  @media (max-width:640px){
    .legal-head .wrap{padding-top:40px;padding-bottom:36px}
    .legal-layout{gap:30px;padding-top:32px;padding-bottom:56px}
    .prose{font-size:16px}
    .prose h2{font-size:20px}
    .toc{padding:18px 18px}
  }
  /* stacked tables on small screens */
  @media (max-width:560px){
    .prose table{border:0}
    .prose thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
    .prose tbody tr{
      display:block;padding:14px 0;
      border-bottom:1px solid var(--line);
    }
    .prose tbody tr:last-child{border-bottom:0}
    .prose td{display:block;padding:0;border:0}
    .prose td:first-child{color:var(--ink);font-weight:700;margin-bottom:4px}
  }
  @media print{
    .site-nav,.site-foot,.toc,.skip,.totop,.legal-head::before{display:none !important}
    body{background:#fff;color:#111}
    .legal-head{background:#fff;border-bottom:1px solid #ccc}
    .prose,.prose p,.prose li,.prose td{color:#111;max-width:none}
    .prose h2,.prose strong,.legal-head h1{color:#000}
    .prose h3{color:#665028}
    .prose a{color:#111}
    .prose section{break-inside:auto;page-break-inside:auto}
    .prose h2{break-after:avoid;page-break-after:avoid}
  }
"""

CSS_404 = """
  .nf{
    position:relative;overflow:hidden;
    min-height:calc(100svh - 64px);
    display:flex;align-items:center;justify-content:center;
    text-align:center;padding:72px 0;
  }
  .nf::before{
    content:"";position:absolute;inset:0;z-index:0;
    background:
      radial-gradient(70% 60% at 50% 0%, var(--pitch) 0%, transparent 62%),
      radial-gradient(60% 60% at 50% 100%, rgba(200,168,106,0.12) 0%, transparent 60%);
  }
  .nf-in{position:relative;z-index:1;max-width:600px;margin:0 auto}
  .nf .brand-mark{width:92px;height:92px;margin:0 auto 26px}
  .nf-code{font-size:13px;letter-spacing:5px;font-weight:800;color:var(--gold)}
  .nf h1{font-size:clamp(30px,7vw,46px);line-height:1.08;letter-spacing:-1.4px;font-weight:800;margin-top:14px}
  .nf p{color:var(--muted);font-size:17px;margin-top:16px}
  .nf-links{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:34px}
  @media (max-width:640px){
    .nf{min-height:auto;padding:56px 0 64px}
    .nf .brand-mark{width:76px;height:76px}
  }
"""

# --------------------------------------------------------------------------
# shell
# --------------------------------------------------------------------------

NAV_ITEMS = [("index.html", "Home"), ("privacy.html", "Privacy"), ("terms.html", "Terms")]


def head(title, description, css, favicon, extra_head=""):
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0B0E0C">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CAPPED">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="logo-mark.png">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="{favicon}">
{extra_head}<style>
{css}
</style>
</head>"""


def nav(current):
    links = []
    for href, label in NAV_ITEMS:
        aria = ' aria-current="page"' if href == current else ""
        links.append(f'        <li><a href="{href}"{aria}>{label}</a></li>')
    links = "\n".join(links)
    cta_href = "#download" if current == "index.html" else "index.html#download"
    return f"""<a class="skip" href="#main">Skip to content</a>

<nav class="site-nav" aria-label="Primary">
  <div class="wrap nav-in">
    <a class="brand" href="index.html" aria-label="CAPPED home">
      <span class="brand-mark" aria-hidden="true"></span>
      <span class="brand-word">CAPPED</span>
    </a>
    <div class="nav-right">
      <ul class="nav-links">
{links}
      </ul>
      <a class="btn btn-gold nav-cta" href="{cta_href}">Coming soon</a>
    </div>
  </div>
</nav>"""


def footer():
    return f"""<footer class="site-foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      <span class="brand-mark" aria-hidden="true"></span>
      <div>
        <div class="foot-name">CAPPED</div>
        <div class="foot-note">&copy; {YEAR} CAPPED &middot; Queensland, Australia</div>
      </div>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="index.html">Home</a>
      <a href="privacy.html">Privacy Policy</a>
      <a href="terms.html">Terms of Use</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </nav>
  </div>
</footer>"""


def add_rel_noopener(html):
    """Markup hardening only - never touches wording."""
    return re.sub(r'target="_blank"(?!\s*rel=)', 'target="_blank" rel="noopener noreferrer"', html)


# --------------------------------------------------------------------------
# component css lifted from the source page
# --------------------------------------------------------------------------

MARKED_CSS = r"/\*\s*==\s*{0}:start\s*==.*?\*/(.*?)/\*\s*==\s*{0}:end\s*==\s*\*/"


def lift_css(src_html, marker):
    """Pull a fenced CSS block out of a source page's <style> so components
    that live in the source (markup + styles together) survive a rebuild
    without their CSS having to be duplicated into this script."""
    m = re.search(MARKED_CSS.format(marker), src_html, re.S)
    if not m:
        raise SystemExit(
            f"could not find the '/* == {marker}:start == */ ... /* == {marker}:end == */' "
            f"CSS block in the source page - it is required, and dropping it would ship "
            f"the {marker} markup unstyled"
        )
    return m.group(1)


def check_local_assets(html, out, label):
    """Warn loudly if the page points at a same-repo file that isn't there.
    Cheap guard against shipping a page full of broken images."""
    missing = []
    for ref in re.findall(r'(?:src|href)="((?!https?:|data:|mailto:|#)[^"]+\.(?:png|jpe?g|svg|webp|gif|css|js))"', html):
        if not os.path.exists(os.path.join(out, ref)):
            missing.append(ref)
    for ref in sorted(set(missing)):
        print(f"  WARNING {label}: missing asset {ref}")
    return missing


# --------------------------------------------------------------------------
# legal pages
# --------------------------------------------------------------------------


def parse_legal(src_html):
    """Pull the authored body content out of a source legal page, verbatim."""
    updated = re.search(r'class="updated">\s*(.*?)\s*</div>', src_html, re.S)
    notice = re.search(r'<div class="notice">\s*(.*?)\s*</div>', src_html, re.S)
    toc = re.search(r'<div class="toc">.*?(<ol>.*?</ol>)', src_html, re.S)
    if not (updated and notice and toc):
        raise SystemExit("could not parse source legal page - structure changed")

    after_notice = src_html[notice.end():]
    intro = after_notice[: after_notice.index('<div class="toc">')].strip()

    start = src_html.index("<section id=")
    end = src_html.rindex("</section>") + len("</section>")
    sections = src_html[start:end]

    return {
        "updated": updated.group(1),
        "notice": notice.group(1),
        "toc": toc.group(1),
        "intro": add_rel_noopener(intro),
        "sections": add_rel_noopener(sections),
    }


def build_legal(src_path, out_path, title, page_title, description, css, favicon):
    with open(src_path, encoding="utf-8") as fh:
        parts = parse_legal(fh.read())

    css_all = css + CSS_LEGAL
    doc = f"""{head(title, description, css_all, favicon)}
<body>

{nav(os.path.basename(out_path))}

<header class="legal-head">
  <div class="wrap">
    <div class="eyebrow"><span class="dot"></span>LEGAL</div>
    <h1>{page_title}</h1>
    <p class="updated">{parts["updated"]}</p>
  </div>
</header>

<main id="main">
  <div class="wrap legal-layout">

    <aside class="toc" aria-labelledby="toc-title">
      <div class="toc-title" id="toc-title">Contents</div>
      <nav aria-label="Section navigation">
        {parts["toc"]}
      </nav>
    </aside>

    <article class="prose">
      <div class="notice">
        {parts["notice"]}
      </div>

      {parts["intro"]}

      {parts["sections"]}

      <p class="totop"><a href="#top">&uarr; Back to top</a></p>
    </article>

  </div>
</main>

{footer()}

</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return doc


# --------------------------------------------------------------------------
# landing page
# --------------------------------------------------------------------------


def build_index(src_path, out_path, css, favicon):
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()

    hero = re.search(r'<div class="wrap hero">(.*?)</div>\s*</header>', src, re.S)
    if not hero:
        raise SystemExit("could not parse landing hero - structure changed")
    hero_inner = hero.group(1).strip()

    # Body copy is lifted as one run, from the proof bar down to the footer.
    # Both boundaries are matched at the start of a line so that a stray mention
    # of either tag inside the page - in an HTML comment, or in the inline
    # carousel script - cannot move the cut and silently drop everything after
    # it. (That failure mode is quiet: the build still succeeds, it just ships a
    # page missing its pricing and download sections.)
    start = re.search(r'^<div class="proof">', src, re.M)
    end = re.search(r"^<footer>", src, re.M)
    if not (start and end and start.start() < end.start()):
        raise SystemExit("could not locate the landing body between the proof bar and the footer")
    body_mid = src[start.start(): end.start()].strip()

    # Structural sanity check on the lifted run. Anything that truncates it
    # should fail the build loudly rather than quietly shorten the page.
    for required in ('id="how"', 'id="screens"', 'id="pricing"', 'id="download"'):
        if required not in body_mid:
            raise SystemExit(f"landing body is missing {required} - the lift was truncated")
    if not body_mid.endswith("</section>"):
        raise SystemExit("landing body does not end on a closing section - the lift was truncated")

    # markup fixes only, no copy changes
    body_mid = body_mid.replace(
        '<section style="background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)">',
        '<section class="band">',
    )
    body_mid = body_mid.replace(
        '<a href="#" class="store">',
        '<!-- TODO: swap "#download" for the real App Store listing URL once CAPPED is live -->\n    '
        '<a href="#download" class="store" aria-label="Download CAPPED on the App Store">',
    )
    body_mid = add_rel_noopener(body_mid)

    # The screenshot carousel keeps its markup, its inline script and its CSS in
    # the source page. The first two ride along inside body_mid; the CSS has to
    # be lifted out of the source <style> explicitly.
    css_all = css + CSS_LANDING + lift_css(src, "shots") + lift_css(src, "notify")
    doc = f"""{head(
        "CAPPED — Get seen. Get signed.",
        "CAPPED turns your match footage into a professional football highlight reel coaches actually want to watch. Built for Australian players.",
        css_all,
        favicon,
    )}
<body>

{nav("index.html")}

<header class="hero-band">
  <div class="wrap hero">
    <span class="brand-mark hero-mark" aria-hidden="true"></span>
    {hero_inner}
  </div>
</header>

<main id="main">

{body_mid}

</main>

{footer()}

</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return doc


# --------------------------------------------------------------------------
# 404 + redirect stub
# --------------------------------------------------------------------------


def build_404(out_path, css, favicon):
    # <base href="/capped-site/"> can be uncommented if you want deep-path 404s
    # (e.g. /capped-site/a/b/c) to resolve their nav links correctly on a project site.
    extra = (
        '<meta name="robots" content="noindex">\n'
        '<!-- If you deploy under a project path and want 404s on deep URLs to keep\n'
        '     working nav links, uncomment and match your repo name:\n'
        '     <base href="/capped-site/"> -->\n'
    )
    doc_head = head(
        "Page not found — CAPPED",
        "That page could not be found. Head back to the CAPPED home page, privacy policy or terms of use.",
        css + CSS_404,
        favicon,
        extra_head=extra,
    )
    doc = f"""{doc_head}
<body>

{nav("404.html")}

<main id="main" class="nf">
  <div class="wrap">
    <div class="nf-in">
      <span class="brand-mark" aria-hidden="true"></span>
      <div class="nf-code">404</div>
      <h1>This one went out for a throw-in.</h1>
      <p>The page you were after doesn&rsquo;t exist, or it has moved. Here&rsquo;s the way back.</p>
      <div class="nf-links">
        <a class="btn btn-gold btn-lg" href="index.html">Back to home</a>
        <a class="btn btn-ghost btn-lg" href="privacy.html">Privacy Policy</a>
        <a class="btn btn-ghost btn-lg" href="terms.html">Terms of Use</a>
      </div>
    </div>
  </div>
</main>

{footer()}

</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return doc


def build_redirect(out_path, target, label, favicon):
    doc = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label} — CAPPED</title>
<meta http-equiv="refresh" content="0; url={target}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<link rel="icon" type="image/png" href="{favicon}">
<style>
  body{{
    background:#0B0E0C;color:#F2EDE2;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    display:flex;align-items:center;justify-content:center;
    min-height:100vh;margin:0;padding:24px;text-align:center;line-height:1.6;
  }}
  a{{color:#C8A86A}}
</style>
</head>
<body>
<p>This page has moved. Redirecting to the <a href="{target}">CAPPED {label}</a>&hellip;</p>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)


# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description="Build the CAPPED static site.")
    ap.add_argument("--src", default=DEFAULT_SRC,
                    help="folder holding the authored source pages (default: ../marketing)")
    ap.add_argument("--out", default=HERE, help="output folder (default: this folder)")
    args = ap.parse_args()

    src, out = args.src, args.out
    for name in ("landing-page.html", "privacy-policy.html", "terms.html"):
        if not os.path.exists(os.path.join(src, name)):
            sys.exit(f"missing source file: {os.path.join(src, name)}")

    logo = data_uri(os.path.join(out, "assets", "logo-mark-256.png"))
    favicon = data_uri(os.path.join(out, "assets", "favicon-64.png"))
    css = CSS_CORE.replace("__LOGO__", logo)

    index_doc = build_index(
        os.path.join(src, "landing-page.html"), os.path.join(out, "index.html"), css, favicon
    )
    build_legal(
        os.path.join(src, "privacy-policy.html"), os.path.join(out, "privacy.html"),
        "Privacy Policy — CAPPED", "Privacy Policy",
        "How CAPPED collects, uses, stores and protects your personal information, "
        "in line with the Australian Privacy Principles.",
        css, favicon,
    )
    build_legal(
        os.path.join(src, "terms.html"), os.path.join(out, "terms.html"),
        "Terms of Use — CAPPED", "Terms of Use",
        "The terms that govern your use of the CAPPED app, covering accounts, your content, "
        "subscriptions and your Australian Consumer Law rights.",
        css, favicon,
    )
    build_404(os.path.join(out, "404.html"), css, favicon)
    build_redirect(os.path.join(out, "privacy-policy.html"), "privacy.html", "Privacy Policy", favicon)

    for name in ("index.html", "privacy.html", "terms.html", "404.html", "privacy-policy.html"):
        p = os.path.join(out, name)
        print(f"  built {name:22s} {os.path.getsize(p) / 1024:6.1f} KB")

    check_local_assets(index_doc, out, "index.html")

    # CNAME binds the custom domain; losing it takes cappedhq.com down.
    cname = os.path.join(out, "CNAME")
    if not os.path.exists(cname):
        print("  WARNING CNAME is missing - cappedhq.com will stop resolving")
    else:
        print(f"  CNAME  {open(cname).read().strip()}")


if __name__ == "__main__":
    main()
