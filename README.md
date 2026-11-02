# Free Time Vacation Planner

## 🏖️ Find the best vacation windows without missing live sports on SF Bay Area radio

This project tracks all live sports broadcasts receivable on AM/FM radio in San Francisco's Outer Sunset (ZIP 94122) and identifies the best windows for taking a vacation — periods of 1, 2, or 3+ consecutive weeks with no scheduled sports programming.

### Sports Tracked
- **⚾ MLB** — All 30 teams (SF Giants ⭐ and Athletics ⭐ high priority)
- **🏈 NFL** — All games + Westwood One national radio (SF 49ers ⭐ high priority)
- **🏈 NCAAF** — Stanford Cardinal ⭐ and Cal Golden Bears ⭐ (high priority)

### Coverage Years
- **2026**: Verified from official sources (MLB.com, NFL.com, GoStanford.com, CalBears.com)
- **2027-2029**: Estimated based on historical patterns (clearly flagged)

### Radio Stations
- KNBR 680 AM / 104.5 FM (The Sports Leader)
- KNBR 1050 AM (ESPN Radio / Athletics overflow)
- KSFN 1510 AM
- Westwood One Sports (national NFL broadcasts)

## 🌐 Live Site

**Setup GitHub Pages:**
1. Go to repo Settings → Pages
2. Under "Build and deployment" → Source → Select "GitHub Actions"
3. The included workflow will automatically deploy on push to main

**Site URL:** `https://karagemop466-tech.github.io/Korea4/`

## 📁 Project Structure

```
├── index.html              # Dashboard
├── daily.html              # Day-by-day schedule
├── calendar.html           # Monthly calendar view
├── vacation.html           # Vacation window finder
├── teams.html              # Team schedules & data
├── radio.html              # Radio station info
├── executive-summary.html  # Analysis & findings
├── flagged.html            # Unverified items for review
├── css/style.css           # Styles
├── js/app.js               # Application logic
├── data/schedules.js       # All schedule data with sources
├── docs/                   # Documentation
└── COORDINATION.md         # Task board
```

## 🔑 Key Findings

| Year | Best Vacation Window | Duration |
|------|---------------------|----------|
| 2026 | Oct 29 - Nov 7 | ~10 days |
| 2026-27 | Feb 15 - Mar 30 | ~6 weeks |
| 2027+ | Same pattern: post-Super Bowl to pre-MLB Opening Day | ~6 weeks |

## Sources

All data sourced from official verified sources with links provided in the application:
- [MLB.com](https://www.mlb.com/schedule) / [CBS Sports](https://www.cbssports.com/mlb/news/mlb-releases-2026-schedule/)
- [NFL.com](https://www.nfl.com/nfl-schedule-release/)
- [GoStanford.com](https://gostanford.com/sports/football/schedule)
- [CalBears.com](https://calbears.com/news/2026/1/26/california-football-announces-2026-schedule.aspx)
- [WestwoodOneSports.com](https://www.westwoodonesports.com/nfl-schedule/)
- [KNBR.com](https://www.knbr.com/shows/)
