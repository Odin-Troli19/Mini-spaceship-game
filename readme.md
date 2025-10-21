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

To Run:
bashpip install pygame
python deep_space_dash.py