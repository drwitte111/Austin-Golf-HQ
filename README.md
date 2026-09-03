# Austin Golf HQ

Live golf scoring for the group. Type your name, pick a course, enter what you
shot hole by hole, and everyone watches the leaderboard move in real time.

Built the same way as [LaManna-Big-Year](https://github.com/drwitte111/LaManna-Big-Year):
a single `index.html`, Firebase straight from the CDN, no build step, no npm,
installable to a phone home screen, hosted on GitHub Pages.

- **Firebase project:** `golf-hq`
- **Services:** Cloud Firestore only (no Auth, no Firebase Hosting)
- **Hosting:** GitHub Pages

## Screens

```
Login (name only)
  └── Menu
        ├── Overview          - placeholder
        ├── Stats             - placeholder
        ├── World Tour Golf   - built
        ├── New Kings North   - placeholder
        └── Admin             - placeholder, only shown to an admin
```

## World Tour Golf

A working copy of the printed scorecard: two nines, the "holes inspired by"
column headers, all three tee yardages, par and handicap rows, and a score row
you type into. Yardage subtotals match the card exactly (BLACK 3235/3290, GOLD
3026/3188, SILVER 2859/2967, par 36/36).

Pick your tee and that row is ringed. Out / In / Total / To-par update as you
type. Everyone's scores stream in live underneath.

### Adding New Kings North

The scorecard is data-driven — `COURSES` near the top of the script block is the
only thing that describes a course. Adding New Kings North means adding one more
entry there (name, tee names, and the two nines with `inspiredBy`, yardage per
tee, `par`, `hcp`) and pointing the menu button at its id. **No renderer changes.**

## Signing in, and admin

There is no Firebase Auth. "Signing in" is typing your name, exactly like
LaManna-Big-Year. What keeps two players apart is a random device id minted once
into `localStorage`; that id is the document id of your score row, so your phone
only ever writes your own scores.

`ADMIN_NAMES` in the script controls who sees admin screens — currently
`['david']`, matched case-insensitively against the typed name. `Dave` and
`Davidson` do not match.

**What that gate is worth:** it hides UI, nothing more. The page source is
public, so anyone can read the list and type `David`, and Firestore will still
accept their writes because the rules cannot tell players apart. Fine for a
group of friends; if admin ever needs to be real, that means Firebase Anonymous
Auth plus a uid check in the rules.

### Data model

```
courses/{courseId}/players/{deviceId}   name, tee, scores { "1": 4, ... "18": 5 }, updatedAt
```

Course reference data ships in `index.html`, not Firestore — no reads to pay
for, and the card still draws with no signal. Only holes actually entered are
stored, so "thru 5" and to-par stay honest mid-round.

## Mobile

Set up to be added to a phone home screen and used on the course:

- **Installable PWA** — `manifest.json`, `display: standalone`, plus 192/512
  icons and maskable variants for Android.
- **iOS home screen** — `apple-touch-icon`, `apple-mobile-web-app-capable`, and
  a black-translucent status bar.
- **Safe areas** — `viewport-fit=cover` with `env(safe-area-inset-*)` padding on
  every outer edge, so nothing hides under a notch or home indicator.
- **`100dvh`** so the layout tracks Safari's collapsing toolbars.
- **16px score inputs** — anything smaller makes iOS zoom the page on focus,
  which is maddening when you are tapping in 18 numbers.
- **44px touch targets** on every button.
- **Sticky row labels** — the scorecard scrolls sideways inside its own box
  (the page itself never scrolls horizontally) and the BLACK/GOLD/PAR labels
  stay pinned so you always know which row you are typing in.
- **`overscroll-behavior`** so swiping past hole 9 doesn't trigger back-navigation
  or rubber-band the whole page.

## Security, honestly

Because there is no auth, the Firestore rules cannot tell one player from
another — `request.auth` is always null. The rules enforce *shape* (a write must
look like a scorecard, sizes capped, course docs not client-writable), but anyone
with the page can read and write any score row. Same trade LaManna-Big-Year
makes.

## Remaining setup

Already done: CLI installed, logged in, web app registered, config inlined.

### 1. Create the Firestore database

[Firestore console](https://console.firebase.google.com/project/golf-hq/firestore)
→ **Create database** → **us-central1** → **production mode**. This also enables
the Cloud Firestore API, which cannot be turned on from the CLI. Until this is
done the app runs but no scores save.

### 2. Push the security rules

```bash
firebase deploy --only firestore:rules
```

### 3. Turn on GitHub Pages

**Settings → Pages → deploy from branch → `main` / root**. Lands at
`https://drwitte111.github.io/Austin-Golf-HQ/`. `.nojekyll` is committed so Pages
serves the files as-is.

## Notes

- **Auto-update:** on load the page sends a `HEAD` request against itself and
  compares the ETag to the last one seen. GitHub Pages derives the ETag from
  file content, so it changes on every deploy and a home-screen icon can't get
  stuck on a stale copy. No version number to bump.
- **Offline:** score writes are deliberately not awaited — Firestore applies
  them locally at once and syncs when signal returns, so totals keep moving in a
  dead spot on the back nine.
- **Icons** were generated by `tools/make_icons.py` (Pillow); rerun it to
  change the artwork.
