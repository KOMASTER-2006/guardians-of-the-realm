"""Create a native offline Android wrapper for Guardians of the Realm.
Run with Python 3 from the directory containing Guardians-of-the-Realm.html.
GitHub Actions runs this automatically. No Python packages are required.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Guardians-of-the-Realm.html"
OUT = ROOT / "android"

FILES = {
    "settings.gradle": '''pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "GuardiansOfTheRealm"
include ':app'
''',
    "build.gradle": '''plugins {
    id 'com.android.application' version '8.7.3' apply false
}
''',
    "gradle.properties": '''org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
android.useAndroidX=false
''',
    "app/build.gradle": '''plugins { id 'com.android.application' }
android {
    namespace 'com.pruthvi.guardiansoftherealm'
    compileSdk 35
    defaultConfig {
        applicationId 'com.pruthvi.guardiansoftherealm'
        minSdk 23
        targetSdk 35
        versionCode 1
        versionName '1.0'
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    buildTypes {
        release { minifyEnabled false }
    }
}
''',
    "app/src/main/AndroidManifest.xml": '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Deliberately no Internet, storage, microphone or account permissions. -->
    <application android:allowBackup="false" android:label="Guardians of the Realm"
        android:icon="@drawable/ic_guardians" android:supportsRtl="true"
        android:theme="@style/AppTheme" android:usesCleartextTraffic="false">
        <activity android:name=".MainActivity" android:exported="true"
            android:screenOrientation="sensorLandscape"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:hardwareAccelerated="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
''',
    "app/src/main/res/values/styles.xml": '''<resources>
    <style name="AppTheme" parent="android:style/Theme.Material.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowActionModeOverlay">true</item>
        <item name="android:windowBackground">#101d23</item>
        <item name="android:colorAccent">#8ce6de</item>
        <item name="android:windowLayoutInDisplayCutoutMode">never</item>
    </style>
</resources>
''',
    "app/src/main/res/drawable/ic_guardians.xml": '''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#112A30" android:pathData="M0,0H108V108H0Z" />
    <path android:fillColor="#D2B275" android:pathData="M54,10L91,27V62Q88,85 54,99Q20,85 17,62V27ZM54,17L24,32V62Q27,80 54,91Q81,80 84,62V32Z" />
    <path android:fillColor="#79EAED" android:pathData="M54,23L73,46L54,82L35,46Z" />
    <path android:fillColor="#B7FBFF" android:pathData="M54,23V82L35,46Z" />
    <path android:fillColor="#738BEF" android:pathData="M35,46H73L54,82Z" />
    <path android:fillColor="#EBFCFF" android:pathData="M54,23L54,46L35,46Z" />
</vector>
''',
    "app/src/main/java/com/pruthvi/guardiansoftherealm/MainActivity.java": '''package com.pruthvi.guardiansoftherealm;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JsResult;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public final class MainActivity extends Activity {
    private WebView game;
    private static final String HOME = "file:///android_asset/index.html";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        game = new WebView(this);
        game.setBackgroundColor(0xff101d23);
        WebSettings settings = game.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setBlockNetworkLoads(true);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);
        game.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !request.getUrl().toString().equals(HOME);
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return !HOME.equals(url);
            }
        });
        game.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
                new AlertDialog.Builder(MainActivity.this).setMessage(message)
                    .setPositiveButton("OK", (d,w) -> result.confirm())
                    .setNegativeButton("Cancel", (d,w) -> result.cancel())
                    .setOnCancelListener(d -> result.cancel()).show();
                return true;
            }
        });
        setContentView(game);
        immersive();
        game.loadUrl(HOME);
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }
    @Override public void onWindowFocusChanged(boolean focus) {
        super.onWindowFocusChanged(focus);
        if (focus) immersive();
    }
    private void pauseMatch() {
        if (game != null) game.evaluateJavascript(
            "if(window.game && window.game.state==='playing'){window.game.paused=true;window.game.ui.update(true);}", null);
    }
    @Override protected void onPause() {
        pauseMatch();
        if (game != null) { game.onPause(); game.pauseTimers(); }
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        if (game != null) { game.onResume(); game.resumeTimers(); }
    }
    @Override public void onBackPressed() {
        pauseMatch();
        new AlertDialog.Builder(this).setTitle("Leave the realm?")
            .setMessage("Records and settings are saved. The current match will end.")
            .setPositiveButton("Exit", (d,w) -> finish())
            .setNegativeButton("Stay", (d,w) -> immersive()).show();
    }
    @Override protected void onDestroy() {
        if (game != null) { game.destroy(); game = null; }
        super.onDestroy();
    }
}
''',
}

def main():
    if not SOURCE.is_file():
        raise SystemExit("Missing Guardians-of-the-Realm.html. Upload that exact filename beside build_android.py in the repository root.")
    for name, content in FILES.items():
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    assets = OUT / "app/src/main/assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, assets / "index.html")
    print(f"Android project created: {OUT}")
    print("Game is bundled locally; no Internet permission is requested.")

if __name__ == "__main__":
    main()
