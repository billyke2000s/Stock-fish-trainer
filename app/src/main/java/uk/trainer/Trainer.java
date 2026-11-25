package uk.trainer;

import android.app.Activity;
import android.os.Bundle;
import android.os.Build;
import android.content.res.Configuration;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.*;
import java.io.IOException;

public class Trainer extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        WebView view = new WebView(this);
        android.widget.FrameLayout frame = new android.widget.FrameLayout(this);
        frame.setBackgroundColor(0xff101a17);
        view.setBackgroundColor(0xff101a17);
        frame.addView(view);
        frame.setOnApplyWindowInsetsListener(new android.view.View.OnApplyWindowInsetsListener() {
            @Override public android.view.WindowInsets onApplyWindowInsets(android.view.View root, android.view.WindowInsets insets) {
            root.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                    insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
            }
        });
        getWindow().getDecorView().setSystemUiVisibility(0);
        getWindow().setStatusBarColor(0xff101a17);
        getWindow().setNavigationBarColor(0xff101a17);
        view.getSettings().setJavaScriptEnabled(true);
        view.getSettings().setDomStorageEnabled(true);
        view.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                String path = r.getUrl().getPath();
                if ("trainer.invalid".equals(r.getUrl().getHost()) && path != null && path.matches("/[a-z.]+")) {
                    try {
                        String mime = path.endsWith(".webp") ? "image/webp" : path.endsWith(".ogg") ? "audio/ogg" : path.endsWith(".js") ? "application/javascript" : path.endsWith(".css") ? "text/css" : "text/html";
                        return new WebResourceResponse(mime, path.endsWith(".webp") ? null : "UTF-8", getAssets().open(path.substring(1)));
                    } catch (IOException ignored) {}
                }
                return new WebResourceResponse("text/plain", "UTF-8", null);
            }
        });
        setContentView(frame);
        updateSystemBars();
        view.loadUrl("https://trainer.invalid/index.html");
    }

    // Reclaim the status/navigation bars for the board in landscape.
    // A swipe from the edge temporarily reveals the Android controls.
    private void updateSystemBars() {
        boolean landscape = getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                if (landscape) controller.hide(WindowInsets.Type.systemBars());
                else controller.show(WindowInsets.Type.systemBars());
            }
        } else {
            getWindow().getDecorView().setSystemUiVisibility(landscape
                    ? View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    : 0);
        }
    }

    @Override public void onConfigurationChanged(Configuration config) {
        super.onConfigurationChanged(config);
        updateSystemBars();
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) updateSystemBars();
    }
}
