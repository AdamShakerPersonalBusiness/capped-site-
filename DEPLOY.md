# Deploying to GitHub Pages

Goal: get this folder online so the CAPPED Privacy Policy has a public URL you can paste
into App Store Connect. Total time is about ten minutes, most of it waiting for GitHub.

Hosting is free. GitHub Pages requires the repository to be **public** on the free plan —
that is fine here, since every file in this folder is meant to be public anyway.

---

## Step 0 — One-time GitHub setup

You need two things before the push will work.

**A GitHub account.** Sign up at <https://github.com/signup> if you do not have one. Write
down the username you choose — it becomes part of your live URL.

**A Personal Access Token (PAT).** GitHub stopped accepting account passwords for pushes,
and this machine has no SSH key and no `gh` CLI installed, so you will be asked for a
token instead of a password.

1. Go to <https://github.com/settings/tokens>
2. **Generate new token** → **Generate new token (classic)**
3. Note: `capped-site deploy`. Expiration: 90 days (or longer).
4. Tick the **`repo`** scope. Nothing else is needed.
5. **Generate token**, then copy it. GitHub shows it once only.

Optionally, save yourself retyping it on every push:

```bash
git config --global credential.helper osxkeychain
```

macOS will then store the token in the Keychain the first time you enter it.

---

## Step 1 — Create the repository

1. Go to <https://github.com/new>
2. **Repository name:** `capped-site`
3. **Visibility:** Public
4. Leave **Add a README file**, **.gitignore** and **licence** all **unticked** — an empty
   repo is required, otherwise the first push is rejected as a non-fast-forward.
5. Click **Create repository**.

Leave that page open. The URL it shows you is the one used in Step 2.

---

## Step 2 — Push this folder

Run these commands exactly, replacing `YOUR_USERNAME` on the `git remote` line with your
GitHub username:

```bash
cd ~/Desktop/CAPPED/site

git init -b main
git config user.name "Adam Shaker"
git config user.email "cappedhq@gmail.com"

git add .
git commit -m "CAPPED public site: landing page, privacy policy, terms"

git remote add origin https://github.com/YOUR_USERNAME/capped-site.git
git push -u origin main
```

When the push prompts you:

- **Username:** your GitHub username
- **Password:** paste the Personal Access Token from Step 0 (not your account password)

Notes:

- The `git config` lines set the identity for this repository only, so nothing else on
  this machine changes. There is currently no global git identity set, and without these
  two lines `git commit` will refuse to run.
- This creates a repository containing only the site. `~/Desktop/CAPPED` is not a git
  repository, so nothing else in the project gets swept in.
- `git add .` picks up `.nojekyll`, which matters — see Step 5.

---

## Step 3 — Turn on GitHub Pages

1. In the repo on GitHub, click **Settings**
2. In the left sidebar, click **Pages**
3. Under **Build and deployment**:
   - **Source:** `Deploy from a branch`
   - **Branch:** `main`
   - **Folder:** `/ (root)`
4. Click **Save**

The first build takes roughly 30–60 seconds. Refresh the Pages settings screen until it
shows "Your site is live at …".

---

## Step 4 — Your live URLs

With a repo named `capped-site` under username `YOUR_USERNAME`:

| Page | URL |
|---|---|
| Landing page | `https://cappedhq.com/` |
| **Privacy Policy** | `https://cappedhq.com/privacy.html` |
| Terms of Use | `https://cappedhq.com/terms.html` |

The old filename still resolves — `cappedhq.com/privacy-policy.html` redirects to
`privacy.html` — so any link already shared keeps working.

Open the Privacy Policy URL in a browser and confirm it loads with the gold cap logo in
the nav before moving on. If you get a 404, wait another minute and refresh; the first
deploy is the slow one.

---

## Step 5 — Paste the URL into App Store Connect

**This is the URL App Store Connect needs:**

```
https://cappedhq.com/privacy.html
```

Where it goes:

1. <https://appstoreconnect.apple.com> → **My Apps** → **CAPPED**
2. **App Information** in the left sidebar
3. Scroll to **General Information**
4. Paste into the **Privacy Policy URL** field
5. **Save** (top right)

Two related fields worth filling in at the same time, since CAPPED sells auto-renewable
subscriptions and Apple checks for these:

- **App Privacy → Privacy Policy URL.** Same URL again. App Store Connect keeps a separate
  copy of this field in the App Privacy section.
- **Terms of Use (EULA).** Under **App Information → License Agreement**, either keep
  Apple's standard EULA or link
  `https://cappedhq.com/terms.html`. Apple also expects a working
  link to the Terms of Use from inside the app on the subscription screen.

---

## Updating the site later

The repository is just this folder. Change a file, then:

```bash
cd ~/Desktop/CAPPED/site
git add .
git commit -m "Update privacy policy"
git push
```

GitHub Pages redeploys automatically within about a minute. The URLs never change, so you
do not need to touch App Store Connect again.

If you changed the wording in `../marketing/privacy-policy.html` or
`../marketing/terms.html`, run `python3 build.py` **before** committing — see
[README.md](README.md#editing-the-legal-wording).

---

## Custom domain — cappedhq.com

The `CNAME` file in this folder already contains `cappedhq.com`, so GitHub Pages will claim
the domain as soon as you push. You still have to point DNS at GitHub.

**At your registrar, for the apex `cappedhq.com`, add four `A` records:**

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

**And four `AAAA` records** (IPv6 — skipping these makes the site unreachable for some
mobile networks, which matters when your audience is on phones):

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

**For `www`, add one `CNAME` record** pointing at `YOUR_USERNAME.github.io` (with the
trailing dot if your registrar requires it).

Then in **Settings → Pages**, enter `cappedhq.com` in the Custom domain field and save.
Wait for the DNS check to go green, then tick **Enforce HTTPS**. Certificate issuance
usually takes a few minutes but can take up to an hour — the box stays greyed out until
it's ready, which is normal, not an error.

Verify before pasting anything into App Store Connect:

```bash
dig +short cappedhq.com
curl -sI https://cappedhq.com/privacy.html | head -1
```

The first should list the four GitHub IPs; the second should return `HTTP/2 200`. Apple
rejects submissions where the privacy policy URL doesn't resolve, so confirm this rather
than assuming DNS has propagated.

---

## Troubleshooting

**`git commit` says "Please tell me who you are".** The two `git config` lines in Step 2
were skipped. Run them and commit again.

**Push is rejected as "non-fast-forward" or "fetch first".** The repository was created
with a README. Either delete the repo and recreate it empty, or run
`git push -u origin main --force` — safe here, because the remote has nothing you want.

**Push asks for a password and rejects the right one.** GitHub does not accept account
passwords. Paste the Personal Access Token from Step 0.

**Site shows a 404 after enabling Pages.** Give it a full minute. Then check that the repo
is Public, that the branch is `main` and the folder is `/ (root)`, and that `index.html`
is at the top level of the repo rather than inside a subfolder.

**A page loads but has no styling, or the logo is missing.** Confirm `.nojekyll` was
committed (`git ls-files | grep nojekyll`). Without it, GitHub runs the files through
Jekyll, which can drop files and choke on unexpected syntax.

**Links work locally but 404 on GitHub Pages.** The server is case-sensitive where macOS
is not. The filenames are all lowercase: `index.html`, `privacy.html`, `terms.html`,
`404.html`.

---

## Alternative: a root-level site

If you would rather have `https://YOUR_USERNAME.github.io/privacy.html` with no
`/capped-site/` path, name the repository `YOUR_USERNAME.github.io` instead at Step 1 and
change the `git remote` URL to match. Everything else is identical. You only get one such
repo per account, so use it only if this is the only site you plan to host.
