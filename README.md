# ♞ Stockfish Trainer

**An offline chess coach for Android.** Play a fresh game against Stockfish, try a different move when you slip, and see the reply if you decide to play it anyway.

[**Download the Android APK**](../../releases/download/v1.0.3/Stockfish-Trainer.apk) · [All releases](../../releases) · [APK in this repository](downloads/Stockfish-Trainer.apk)

### Your first game

1. Open the app. The trainer picks one of eight opening positions and assigns you White or Black.
2. Tap a piece to highlight its legal destinations, then tap the square you want.
3. If the coach spots a mistake, try a different move. **Hint** reveals a suggested move. **Play my move** lets you see Stockfish’s reply.
4. Tap **New game** for a fresh opening. The move list below the board tracks the current game.

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
gradle assembleDebug
```

Find the APK under `app/build/outputs/apk/debug/`. The preparation script verifies the downloaded engine and chess rules packages against pinned SHA-256 hashes.

### Credits

[Stockfish.js](https://github.com/niklasf/stockfish.js) powers the opponent and move analysis. [chess.js](https://github.com/jhlywa/chess.js) handles legal moves and game outcomes. See [COPYING](COPYING) and [CHESS-LICENSE](CHESS-LICENSE).
