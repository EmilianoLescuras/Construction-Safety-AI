# 30-Second Demo Video — Shot List

Goal: portfolio video showing the full pipeline in ~30 seconds. Recorded
manually because there's no headless way to capture a smooth screen+audio
demo of a UI in motion.

## Tools

| Tool | Mac built-in |
|---|---|
| Screen recording | QuickTime Player → File → New Screen Recording, or **⌘⇧5** |
| Trim | QuickTime → Edit → Trim |
| (Optional) gif conversion | `ffmpeg -i demo.mov -vf "fps=15,scale=960:-1" demo.gif` |

## Pre-roll setup

Before hitting record:

```bash
# Make sure the stack is up and seeded
docker compose up -d

# Run the worker once to load fresh events
docker compose --profile worker run --rm worker \
  --source /app/outputs/videos/cs_smoke_60_track.mp4 \
  --rules /app/config/rules.json

# Open these tabs in the SAME browser, in this order:
#   1. http://localhost:3000           (dashboard)
#   2. http://localhost:3000/events    (events list)
#   3. http://localhost:3000/events/3  (event detail)
#   4. http://localhost:3000/live      (live page)

# Resize the browser to 1440×900 for clean recording.
```

## Shots (30s total)

| t | Duration | Shot | Voice-over / overlay |
|---|---|---|---|
| 0–3s | 3s | Dashboard load (page fade in) | "Construction Safety AI — real-time PPE compliance monitoring." |
| 3–8s | 5s | Pan over KPI cards, hover bar chart | "Detects missing helmets, vests, masks across any video source." |
| 8–14s | 6s | Click `Events` tab → table appears → filter by `vest` | "Every violation persisted, deduped, and filterable." |
| 14–22s | 8s | Click into event #3 → side-by-side annotated frame + crop | "Each event ships with full-frame + crop evidence images." |
| 22–28s | 6s | Switch to `/live`, pause/resume toggle, show pulse | "Live monitor polls every 3s with pause/resume." |
| 28–30s | 2s | Static end card with `github.com/EmilianoLescuras/Construction-Safety-AI` | URL fade in |

## End card

Create a 2-second still frame with:

```
Construction Safety AI
github.com/EmilianoLescuras/Construction-Safety-AI
```

## After recording

1. Trim to exactly 30s in QuickTime.
2. Export at 1080p H.264.
3. (Optional) Make a 5MB animated gif for the README:
   ```bash
   ffmpeg -i demo.mov -vf "fps=15,scale=960:-1" -loop 0 docs/demo.gif
   ```
4. Upload the mp4 to GitHub Releases or YouTube.
5. Add to README under the "Live demo" section:
   ```markdown
   [![demo](docs/demo_thumb.png)](https://youtu.be/XXXX)
   ```
