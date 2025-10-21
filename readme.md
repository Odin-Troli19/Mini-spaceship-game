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



To Run:
bashpip install pygame
python deep_space_dash.py