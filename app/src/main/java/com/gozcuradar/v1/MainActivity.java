package com.gozcuradar.v1;

import android.os.Bundle;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.FrameLayout;
import android.widget.Button;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.WindowCompat;

public class MainActivity extends AppCompatActivity {

    WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        WindowCompat.setDecorFitsSystemWindows(getWindow(), true);

        FrameLayout ana = new FrameLayout(this);

        web = new WebView(this);
        ana.addView(web);

        Button yenile = new Button(this);
        yenile.setText("🔄");
        yenile.setTextSize(18);
        yenile.setTextColor(Color.WHITE);
        yenile.setBackgroundColor(Color.rgb(0, 120, 200));

        FrameLayout.LayoutParams buton =
                new FrameLayout.LayoutParams(
                        60,
                        60,
                        Gravity.TOP | Gravity.LEFT
                );

        buton.setMargins(20, 120, 0, 0);
        ana.addView(yenile, buton);

        setContentView(ana);

        WebSettings ayar = web.getSettings();
        ayar.setJavaScriptEnabled(true);
        ayar.setDomStorageEnabled(true);
        ayar.setMediaPlaybackRequiresUserGesture(false);

        web.setWebViewClient(new WebViewClient());
        web.setWebContentsDebuggingEnabled(true);
        web.getSettings().setJavaScriptCanOpenWindowsAutomatically(true);

        yenile.setOnClickListener(v -> {
            web.clearCache(false);
            web.reload();
        });

        web.clearCache(true);
        web.getSettings().setCacheMode(WebSettings.LOAD_NO_CACHE);
        web.loadUrl("https://siber-radar.onrender.com/");
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
