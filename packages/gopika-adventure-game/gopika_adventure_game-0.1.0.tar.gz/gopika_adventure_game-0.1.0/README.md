## Advanced Generator Methods - Interactive Adventure Game

### Overview for the task

This task demonstrates the use of advanced generator methods (send(), throw(), and close()) in a text-based adventure game. The player navigates through different stages by making decisions that influence the game's flow.

### Game Flow

- The player starts in a forest and chooses to go North or South.
- Going North leads to a mountain, where they can enter a cave or go back.
- Inside the cave, they find a treasure chest and can choose to open it (win) or leave.
- Going South leads to a river, where they can swim (lose) or go back.

### Modules

- ```game_engine.py```: Manages the main game loop and transitions between stages.
- ```stage_logic.py```: Contains generator functions for each stage (forest, mountain, river, cave).
- ```main.py```: Handles user interaction using questionary and rich for a styled CLI experience.
- ```constants.py```: Defines enums for Stage and Decision.

### How to Play

- Run the game and follow the prompts. Use the arrow keys to select your choices.
- You can quit anytime by selecting Quit or pressing Ctrl + C.

### To run the file

- Navigate to:

    ```bash
    cd src
    ```

- Then run using:

    ```bash
    python -m assignment_12.task_4.main
    ```
