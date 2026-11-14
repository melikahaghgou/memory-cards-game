# Neon Memory Cards

Neon Memory Cards is a memory matching puzzle game built using Python and Pygame. It has a bright neon look with a style. The game includes a countdown timer, game-style icon buttons automatically generated card icons or the option to use your pictures. It supports grid sizes and has a separate leaderboard for each grid size.

---

## Features

- **Neon Visuals:** The game uses a color palette with a custom synthwave-style background. This includes a sky, stars, a perspective grid floor and floating cards. You can replace the background with your image.

- **Countdown Timer:** Each game starts with a timer set to 1:00. The timer counts down. The timer bar and clock turn red in the last 10 seconds. If the time runs out the "TIME'S UP" screen. No record is saved.

- **Unique Card Icons:** There are 14 neon shapes in 8 colors creating 112 unique icons. No two pairs in the game look the same. The icons. Do not contain any numbers or text.

- **Custom Card Images:** You can use your pictures for the cards. Just place your images in the cards folder and the game resizes them automatically. The images are picked at random for each game. You need least as many images as the number of pairs on the map.

- **Game-Style Icon Buttons:** The buttons are round, glossy. Have a glow effect. They show a lift effect when you hover and a press effect when you click. The buttons are icon-. The leaderboard Play Again/Try Again Menu and Back buttons show tooltips when you hover over them. The map buttons show a preview of the grid size.

- **Multiple Grid Sizes:**

4 X 4 (16 cards 8 pairs)

6 X 6 (36 cards 18 pairs)

8 X 8 (64 cards 32 pairs)

10 X 10 (100 cards 50 pairs)

- **Tabbed Leaderboard:** Each grid size has its tab in the leaderboard. Clicking a tab shows the scores for that map size.

- **Ranking and Score:** Players are ranked by the time they took with the times first. Then by the number of moves. The saved time is 60 seconds. The time left. The score is higher when you finish faster and use moves.

- **Persistent Storage:** High scores are saved in a file called `leaderboard.json`. The file is written safely through a file.

---

## Installation & Running

### Prerequisites

You need Python 3.8 or newer installed on your computer.

### Steps

1. Clone the repository:

```bash

git clone https://github.com/your-username/neon-memory-cards.git

cd neon-memory-cards

```

2. Install Pygame:

```bash

pip install pygame

```

3. Run the game:

```bash

python main.py

```

(Use the name of your game file if it is different.)

---

## How to Play

1. Type your name in the menu. This step is optional. Then choose a map size.

2. Click two cards to flip them. If they match they stay open. If they don't match they flip back.

3. Find all the pairs before the 1:00 countdown reaches zero.

4. If you win your time moves and score are saved to the leaderboard automatically.

5. Use the icon buttons: trophy for the leaderboard house for the menu circular arrow to play again and arrow to go back. Press `Esc` at any time to return to the menu.

---






<div align="center">
  <img src="assets/1.png" alt="Screenshot 1" width="70%"><br><br>
  <img src="assets/2.png" alt="Screenshot 2" width="70%"><br><br>
  <img src="assets/3.png" alt="Screenshot 3" width="70%"><br><br>
  <img src="assets/4.png" alt="Screenshot 4" width="70%">
</div>
