# Asha Berkeley website

Static site for Asha Berkeley (UC Berkeley chapter of Asha for Education),
deployed on Vercel at https://asha-ochre.vercel.app.

## Branch workflow — IMPORTANT

- **All changes go to the `dev` branch.** Never commit or push directly to `main`.
- `main` is production: any push to it auto-deploys to the live site via
  Vercel's Git integration (root directory: `asha-site`).
- Pushes to `dev` create Vercel preview deployments only.
- To ship: merge `dev` into `main` (PR or local merge), then push `main`.
- `dev` is the repo's default branch.

## How the site is built

- `asha-site/` holds the generated site. **Do not hand-edit the HTML files** —
  they are overwritten by the build.
- Edit `build_asha_site.py`, then run `python3 build_asha_site.py` from the repo
  root to regenerate all pages.
- The build sources its header/footer chrome from its own previous output
  (`asha-site/join.html`), so any injected script/markup that gets removed from
  the build must also be actively stripped in the chrome-processing section, or
  it will persist forever.
- Manual deploy (if ever needed): `vercel deploy --prod --yes` from the repo
  root, not from `asha-site/`.

## Design rules

- Flat colors only: no gradients, no glows, no background animations.
- Jaini Purva font for headings; template typekit font for body.
- No emoji as icons. No em dashes in copy. Copy must sound like a student
  wrote it, not AI (no punchline endings, no "genuinely/honestly" filler,
  no perfect triads).
- No page-load text entrance animations. The join page has no scroll
  animations at all. Projects-page animations stay as they are.
- Real chapter photos only (`asha-site/assets/photo-*.jpg`, `proj-*.jpg`);
  never reintroduce Phoenix Consulting content — that site was a design
  template only.

## Key integrations

- Coffee chat Airtable (gallery share) is embedded on the members page.
- Application Google Form is linked from the join page Apply button.
- Contact email: berkeley@ashanet.org. Venmo: @ashaberkeley.
