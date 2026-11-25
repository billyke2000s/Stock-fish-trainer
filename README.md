# ♞ Stockfish Trainer

**An offline chess coach for Android.** Play a fresh game against Stockfish, try a different move when you slip, and see the reply if you decide to play it anyway.

[**Download the Android APK**](../../releases/latest/download/Stockfish-Trainer.apk) · [All releases](../../releases)

The redesigned main menu has its own original piano theme, *Quiet Opening*. Choose **Player vs CPU** for a standard game as White, or **Player vs Player** to pass the phone after each move. **Menu → Resume game** returns to the current board.

### Your first game

1. Choose **Train** from the main menu. The trainer picks one of eight opening positions and assigns you White or Black.
2. Tap a piece to highlight its legal destinations, then tap the square you want.
3. If the coach spots a mistake, try a different move. **Hint** reveals a suggested move. **Play my move** lets you see Stockfish’s reply.
4. Tap **New game** for a fresh opening. The move list below the board tracks the current game.

Tap **♫ Music** for the three-song original soundtrack. Choose Between Moves, Window Seat, or Amber After Dark. The next song plays when the current one ends. Your music preference is saved on this device.

### On your phone

| | |
|---|---|
| Android | 7.0 or later with a modern Android System WebView |
| Internet during play | None required |
| Engine | Stockfish.js 10.0.2, running locally |
| First release | Debug-signed APK for device testing |

### Build from source

With Android SDK 35, JDK 17 and Gradle 8.9 installed, run:

```sh
bash prepare-assets.sh
# Install python3-numpy, libfluidsynth3, timgm6mb-soundfont and ffmpeg first.
python3 music/opening.py
gradle assembleDebug
```

Find the APK under `app/build/outputs/apk/debug/`. The preparation script verifies the downloaded engine and chess rules packages against pinned SHA-256 hashes.

### Credits

[Stockfish.js](https://github.com/niklasf/stockfish.js) powers the opponent and move analysis. [chess.js](https://github.com/jhlywa/chess.js) handles legal moves and game outcomes. See [COPYING](COPYING) and [CHESS-LICENSE](CHESS-LICENSE).
