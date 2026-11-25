package uk.trainer;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.*;
import java.io.IOException;

public class Trainer extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        WebView view = new WebView(this);
        view.setFitsSystemWindows(true);
        view.getSettings().setJavaScriptEnabled(true);
        view.getSettings().setDomStorageEnabled(true);
        view.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                String path = r.getUrl().getPath();
                if ("trainer.invalid".equals(r.getUrl().getHost()) && path != null && path.matches("/[a-z.]+")) {
                    try {
                        String mime = path.endsWith(".js") ? "application/javascript" : path.endsWith(".css") ? "text/css" : "text/html";
                        return new WebResourceResponse(mime, "UTF-8", getAssets().open(path.substring(1)));
                    } catch (IOException ignored) {}
                }
                return new WebResourceResponse("text/plain", "UTF-8", null);
            }
        });
        setContentView(view);
        view.loadUrl("https://trainer.invalid/index.html");
    }
}
