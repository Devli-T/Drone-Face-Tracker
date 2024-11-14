# Drone tracker project

This project uses a drone to track faces in real-time using computer vision and AI.

## Setup

1. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the following scripts in order:

    1. `main-state.py`: This script receives and processes the drone's state information, such as yaw, and writes it to a file.
        ```sh
        python3 main-state.py
        ```

    2. `main-command.py`: This script sends commands to the drone based on user input and adjusts the drone's yaw.
        ```sh
        python3 main-command.py
        ```

    3. `main_stream_default.py`: This script handles the video stream from the drone, detects faces, and sends movement commands to the drone to track the detected faces.
        ```sh
        python3 main_stream_default.py
        ```

## Useful documentation for self:
https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf