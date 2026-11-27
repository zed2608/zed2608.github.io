# Bronze Orbit — V1.0 (V43 production build)

Personal portfolio for Ayzhiedy Jee D. Reyes. This is the publication-cleared launch package, prepared for GitHub Pages. The site has not yet been deployed. It preserves the V42 visual identity, image galleries, responsive layout and native animation system.

## Preview

Open `index.html` in Chrome or Edge with all folders kept together. No build, database or API key is required. For a normal local HTTP preview (Python 3 installed), run from this directory:

```powershell
py -m http.server 8000
```

Open `http://localhost:8000/`. Stop with Ctrl+C. Navigation uses URL fragments (`#work`, `#project-thesis`, etc.). Dark is the first-visit default; explicit visitor appearance settings are remembered. Audio is opt-in. The introduction can be skipped, and motion can be paused or reduced by the operating-system accessibility preference.

## Structure

- `index.html`: semantic page markup, case-study copy, gallery captions and social metadata.
- `css/portfolio.css`: styles, themes, layout and motion.
- `js/theme-init.js`: first-paint appearance initialization.
- `data/content.js`: Journey and credential content, separated from interaction logic.
- `js/portfolio.js`: navigation, rocket and profile transitions, galleries, canvas background, optional audio and settings.
- `assets/`: optimized WebP project views, portrait, certificate images and social preview.
- `documents/resume.pdf`: public review copy of the approved résumé, with the phone number removed from the PDF text and contact line recentered.
- `tests/`: static validation and optional Chromium smoke test.
- `.github/workflows/validate.yml`: checks markup references and JavaScript syntax on pushes and pull requests. It does **not** deploy the website.
- `.nojekyll`, `robots.txt`, `sitemap.xml`, `favicon.svg`: static-hosting support.

## Publication and privacy

The owner confirmed clearance for Optimizing Survival, Champion and LokalConnect on November 27, 2026. This build retains the reviewed V43 imagery. Public repository contents are accessible before Pages is enabled. Review the remaining privacy checks before pushing. Keep the nine project repositories separate; their visibility does not need to change.

## Deployment

Create an empty repository named `zed2608.github.io` under the intended GitHub account. For GitHub Free, this must be public to use Pages; verify the account's hosting eligibility. Use the extracted source package, not the standalone preview HTML. From this directory:

```powershell
git init
git branch -M main
git add .
git diff --cached --name-only
git commit -m "Release Bronze Orbit V1.0"
git remote add origin https://github.com/zed2608/zed2608.github.io.git
git push -u origin main
```

In the repository, open Settings > Pages > Build and deployment. Choose **Deploy from a branch**, `main`, `/(root)`, then Save. Confirm the Pages deployment and the HTTPS address in GitHub. Enable Enforce HTTPS if available. The proposed URL is `https://zed2608.github.io/`; it has not been verified as live. The canonical, sitemap and social metadata assume this address; change them if a different domain is selected. After launch, add the verified live URL to the résumé, LinkedIn and GitHub profile.

Official setup guide: https://docs.github.com/en/pages/quickstart

## Validation

```powershell
python tests/validate.py
node --check js/theme-init.js
node --check data/content.js
node --check js/portfolio.js
```

Optional browser checks: `python -m pip install playwright`, `python -m playwright install chromium`, then `python tests/browser_smoke.py`. The local test starts a loopback HTTP server; set `CHROMIUM_PATH` if a custom executable is needed. In the preparation environment direct local HTTP navigation was restricted; the executed browser checks therefore used a standalone document assembled from the same source and assets. See `TEST_RESULTS.md`. Test the real hosted files after deployment, including all external destinations and browser/device performance. Lighthouse scores are not yet measured.
