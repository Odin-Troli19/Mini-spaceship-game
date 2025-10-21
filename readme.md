What I Built
Your complete "Deep Space Dash" game with all the requested features:
Core Gameplay:

Fixed horizontal spaceship with smooth up/down movement (W/S or arrows)
Endless right-scrolling with obstacles spawning from the right
Gradual difficulty increase (speed caps at 10, spawn rate increases)
Collision detection ends the run

HUD & Display:

Left: Distance traveled in miles with "From Earth" indicator
Right: Score (increases per second + bonus per obstacle passed)
Clean white text with shadows for contrast

Planet Milestones:

All 7 milestones implemented (Moon through Pluto)
Toast notifications appear when passing each planet
Shows distance to next planet
Tracks last planet passed for game-over screen

Technical Features:

800×600 window, 60 FPS
Distance scales at 10,000 miles per pixel (reaches Mars in ~2-3 minutes)
Three game states: Menu → Running → Game Over
Pause function (P key)
Simple geometric shapes (no external assets needed)
Animated star field background

✨ New Features Added!
Your enhanced "Deep Space Dash" game now includes:
🚀 Speed Boost System

Hold RIGHT ARROW to accelerate your spaceship!
Base speed increases naturally over time (up to 10 km/s)
Boost adds +8 km/s to current speed (max 15 km/s total)
Visual "BOOST!" indicator appears on screen
Stars scroll faster when boosting for visual feedback

📏 Kilometers Instead of Miles

All distances now displayed in kilometers (km)
Speed shown in km/s (kilometers per second)
Real-time speed updates in the HUD
Converted planet distances to km:

Moon: 384,400 km
Mars: 225,300,000 km
Jupiter: 778,500,000 km
Saturn: 1,433,000,000 km
Uranus: 2,871,000,000 km
Neptune: 4,495,000,000 km



🌌 Beyond Neptune - Procedural Universe

Special message when passing Neptune: "You are leaving our solar system!"
After Neptune, the game generates random planet names:

Examples: "Zeta-Prime", "Nova-Centauri", "Quantum-Rex"


Also generates random galaxy names:

Examples: "Andromeda Expanse", "Whirlpool Sector", "Phoenix Domain"


70% chance for planets, 30% chance for galaxies
New milestones appear every 300-800 million km
Infinite gameplay with unique names each run!

🎨 Spaceship Color Selection

New color selection screen before starting
Choose from 4 colors:

Press 1 - Red
Press 2 - Green
Press 3 - Blue
Press 4 - Yellow


Visual preview of each ship color
Your choice is remembered for the current run

🎮 Gameplay Flow

Main Menu → Press SPACE
Color Selection → Press 1-4 to choose ship color
Game starts immediately after selection
Game Over → Press R to play again (returns to color selection)

🎮 All New Features Implemented!
🌍 Earth Launch Animation

Beautiful 3-second animation when starting the game
Watch Earth shrink as you leave orbit
Shows continents, oceans, and clouds
Progressive text: "Launching..." → "Leaving Earth Orbit" → "Entering Deep Space!"
Smooth transition to gameplay

🪐 Visual Planet Representations
Each planet appears on screen as you approach it (at 90% of the distance):

Moon - Gray sphere with dark craters
Mars - Red planet with darker surface spots
Jupiter - Beige/tan with brown and white horizontal stripes + Great Red Spot
Saturn - Orange/tan planet with beautiful rings (behind and in front)
Uranus - Cyan/light blue ice giant
Neptune - Deep blue ice giant

Planets scroll across the screen at game speed and you actually fly past them!
📈 Distance-Based Difficulty Scaling

Game gets harder the further you travel from Earth
Every 500 million km increases obstacle spawn rate by 15%
Difficulty multiplier caps at 3x (very challenging!)
More obstacles = higher score potential
Creates a natural progression: easy near Earth → intense in deep space

🎯 Complete Feature List
✅ Earth departure animation
✅ Visual planets with unique designs
✅ Saturn's iconic rings
✅ Jupiter's stripes and Great Red Spot
✅ Distance-based difficulty
✅ Speed boost (RIGHT arrow)
✅ Kilometers display
✅ Color selection (4 ship colors)
✅ Procedural planets/galaxies after Neptune
✅ Real-time speed display
✅ Milestone notifications

View your complete game
🎮 All New Features Implemented!
🏆 Leaderboard System

Top 10 high scores saved locally
Saved to deep_space_dash_scores.json in the game directory
Displays: Rank, Score, Distance (km + light years), Ship color, Date/Time
Access from main menu (Press L)
Shows your rank after game over
Persists between game sessions

🌌 Dual Distance Display

Kilometers always shown
Light Years displayed when distance > 0.001 LY
Format: "Distance: 225,300,000 km (0.023810 LY)"
Both units shown in leaderboard and game over screen

❤️ Lives System

Start with 0 extra lives
Earn 1 extra life every 100,000 km traveled
Maximum of 3 extra lives
Lives counter shown in HUD (top-left)
2 seconds of invulnerability after losing a life (ship flashes)
Notification when earning/losing lives
Game over only when all lives are lost

🕳️ Black Holes

Dangerous spinning vortex obstacles
Purple/black appearance with swirling accretion disk
Instant death on collision (same as regular obstacles)
Worth +5 points for passing safely
Rarer than asteroids

🌀 Teleportation Portals

Cyan pulsing portal appearance
Teleports you forward by a random distance:

100 km, 1,000 km, 10,000 km, 100,000 km
1 million km, 10 million km, 100 million km
1 BILLION km (max jump!)


Shows notification with distance jumped
Worth +10 points
Can help you skip to distant milestones instantly!

🎯 Complete Feature Summary
✅ Local leaderboard (top 10, persistent save)
✅ Distance in both km AND light years
✅ Lives system (0 start, max 3, earn every 100k km)
✅ Black holes (deadly spinning vortex)
✅ Portals (random teleportation 100 km - 1 billion km)
✅ Visual planets with realistic designs
✅ Earth launch animation
✅ Distance-based difficulty scaling
✅ Speed boost mechanic
✅ Color selection
✅ Procedural universe after Neptune
Controls:

W/S or UP/DOWN: Move
RIGHT ARROW: Boost speed
P: Pause
L: Leaderboard (from menu or game over)
R: Restart (from game over)


To Run:
bashpip install pygame
python deep_space_dash.py