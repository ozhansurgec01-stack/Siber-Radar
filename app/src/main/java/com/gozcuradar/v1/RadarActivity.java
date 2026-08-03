package com.gozcuradar.v1;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import org.maplibre.android.MapLibre;
import org.maplibre.android.maps.MapView;
import org.maplibre.android.maps.Style;
import org.maplibre.android.camera.CameraUpdateFactory;
import org.maplibre.android.geometry.LatLng;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import org.json.JSONObject;
import org.json.JSONArray;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.Button;
import org.maplibre.geojson.Point;
import org.maplibre.geojson.FeatureCollection;
import org.maplibre.geojson.Feature;
import org.maplibre.android.style.sources.GeoJsonSource;
import org.maplibre.android.style.layers.CircleLayer;
import static org.maplibre.android.style.layers.PropertyFactory.*;

public class RadarActivity extends AppCompatActivity {

    private MapView mapView;
    private CircleLayer yanginLayer;
    private boolean yanginGoster = true;
    private CircleLayer kameraLayer;
    private boolean kameraGoster = true;
    private CircleLayer depremLayer;
    private boolean depremGoster = true;
    private boolean radarGoster = false;
    private org.maplibre.android.style.layers.RasterLayer radarLayer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        MapLibre.getInstance(this);

        mapView = new MapView(this);

        android.widget.FrameLayout ana = new android.widget.FrameLayout(this);
        ana.addView(mapView);

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.HORIZONTAL);
        panel.setGravity(Gravity.CENTER);

        String[] butonlar = {"🔥", "📷", "🌍", "🌧", "🌡", "⚡", "🔄"};

        for (String b : butonlar) {
            Button btn = new Button(this);
            btn.setText(b);
            btn.setTextSize(18);

            if (b.equals("🔥")) {
                btn.setOnClickListener(v -> {
                    if (yanginLayer != null) {
                        yanginGoster = !yanginGoster;

                        yanginLayer.setProperties(
                            visibility(
                                yanginGoster ? "visible" : "none"
                            )
                        );
                    }
                });
            }

            panel.addView(btn,
                new LinearLayout.LayoutParams(65,65)
            );
        }

        android.widget.FrameLayout.LayoutParams pp =
            new android.widget.FrameLayout.LayoutParams(
                -1, 80, Gravity.TOP
            );

        ana.addView(panel, pp);

        setContentView(ana);

        mapView.onCreate(savedInstanceState);

        mapView.getMapAsync(map -> {
            map.setStyle(
                new Style.Builder()
                    .fromUri("https://demotiles.maplibre.org/style.json"),
                style -> {
                    map.animateCamera(
                        CameraUpdateFactory.newLatLngZoom(
                            new LatLng(39.0, 35.0),
                            5.5
                        )
                    );
                    yanginGetir();
                            kameraGetir();
                            depremGetir();
                            radarGetir();
                }
            );
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        mapView.onStart();
    }

    @Override
    protected void onStop() {
        super.onStop();
        mapView.onStop();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mapView.onDestroy();
    }

    private void yanginGetir() {
        new Thread(() -> {
            try {
                URL url = new URL("https://siber-radar-1.onrender.com/api/yanginin");
                HttpURLConnection con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject json = new JSONObject(sb.toString());
                JSONArray arr = json.getJSONArray("uydu");

                runOnUiThread(() -> {
                    try {
    Feature[] features = new Feature[arr.length()];

    for (int i = 0; i < arr.length(); i++) {
        JSONObject y = arr.getJSONObject(i);

        double lat = y.getDouble("lat");
        double lng = y.getDouble("lng");

        Feature f = Feature.fromGeometry(
                    Point.fromLngLat(lng, lat)
                );

                f.addStringProperty("il", y.optString("il","Bilinmiyor"));
                f.addNumberProperty("frp", y.optDouble("frp",0));

                features[i] = f;
    }

    FeatureCollection fc = FeatureCollection.fromFeatures(features);

    if (mapView != null) {
        mapView.getMapAsync(map -> {
            map.getStyle(style -> {

                GeoJsonSource source = new GeoJsonSource(
                    "yangin-source",
                    fc
                );

                style.addSource(source);

                yanginLayer = new CircleLayer(
                    "yangin-layer",
                    "yangin-source"
                );

                CircleLayer layer = yanginLayer;

                layer.setProperties(
                    circleRadius(8f),
                    circleColor(Color.RED),
                    circleOpacity(0.8f)
                );

                style.addLayer(layer);

                map.addOnMapClickListener(point -> {
                    java.util.List<Feature> bulunan =
                        map.queryRenderedFeatures(
                            map.getProjection().toScreenLocation(point),
                            "yangin-layer"
                        );

                    if (!bulunan.isEmpty()) {
                        Feature f = bulunan.get(0);

                        String il = f.getStringProperty("il");
                        String frp = String.valueOf(
                            f.getNumberProperty("frp")
                        );

                        new android.app.AlertDialog.Builder(RadarActivity.this)
                            .setTitle("🔥 Yangın")
                            .setMessage(
                                "İl: " + il +
                                "\nFRP: " + frp +
                                "\nKaynak: NASA FIRMS"
                            )
                            .setPositiveButton("Tamam", null)
                            .show();
                    }

                    return true;
                });
            });
        });
    }


          } catch (Exception e) {
              e.printStackTrace();
          }
      }).start();

    private void kameraGetir() {
        new Thread(() -> {
            try {
                URL url = new URL("https://siber-radar-1.onrender.com/kameralar.json");
                HttpURLConnection con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONArray arr = new JSONArray(sb.toString());

                runOnUiThread(() -> {
                    try {
                        Feature[] features = new Feature[arr.length()];

                        for (int i = 0; i < arr.length(); i++) {
                            JSONArray k = arr.getJSONArray(i);

                            Feature f = Feature.fromGeometry(
                                Point.fromLngLat(
                                    k.getDouble(2),
                                    k.getDouble(1)
                                )
                            );

                            f.addStringProperty(
                                "ad",
                                k.getString(0)
                            );

                            f.addStringProperty(
                                "link",
                                k.getString(3)
                            );

                            features[i] = f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "kamera-source",
                                        fc
                                    );

                                style.addSource(source);

                                kameraLayer =
                                    new CircleLayer(
                                        "kamera-layer",
                                        "kamera-source"
                                    );

                                kameraLayer.setProperties(
                                    circleRadius(7f),
                                    circleColor(Color.BLUE),
                                    circleOpacity(0.9f)
                                );

                                style.addLayer(kameraLayer);
                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void depremGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());
                JSONArray arr = root.getJSONArray("result");

                runOnUiThread(() -> {
                    try {
                        Feature[] features =
                            new Feature[arr.length()];

                        for (int i=0; i<arr.length(); i++) {

                            JSONObject d =
                                arr.getJSONObject(i);

                            Feature f =
                                Feature.fromGeometry(
                                    Point.fromLngLat(
                                        d.getDouble("lng"),
                                        d.getDouble("lat")
                                    )
                                );

                            f.addStringProperty(
                                "yer",
                                d.optString("title","")
                            );

                            f.addNumberProperty(
                                "mag",
                                d.optDouble("mag",0)
                            );

                            features[i]=f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "deprem-source",
                                        fc
                                    );

                                style.addSource(source);

                                depremLayer =
                                    new CircleLayer(
                                        "deprem-layer",
                                        "deprem-source"
                                    );

                                depremLayer.setProperties(
                                    circleRadius(6f),
                                    circleColor(Color.YELLOW),
                                    circleOpacity(0.85f)
                                );

                                style.addLayer(depremLayer);

                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void radarGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.rainviewer.com/public/weather-maps.json"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());

                JSONArray radar =
                    root.getJSONObject("radar")
                    .getJSONArray("past");

                if (radar.length() == 0) return;

                JSONObject son =
                    radar.getJSONObject(radar.length()-1);

                String time =
                    son.getString("path");

                String tile =
                    "https://tilecache.rainviewer.com"
                    + time
                    + "/256/{z}/{x}/{y}/2/1_1.png";

                runOnUiThread(() -> {

                    mapView.getMapAsync(map -> {
                        map.getStyle(style -> {

                            org.maplibre.android.style.sources.RasterSource source =
                                new org.maplibre.android.style.sources.RasterSource(
                                    "radar-source",
                                    tile,
                                    256
                                );

                            style.addSource(source);

                            radarLayer =
                                new org.maplibre.android.style.layers.RasterLayer(
                                    "radar-layer",
                                    "radar-source"
                                );

                            radarLayer.setProperties(
                                org.maplibre.android.style.layers.PropertyFactory.rasterOpacity(0.55f)
                            );

                            style.addLayer(radarLayer);

                        });
                    });

                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

} catch(Exception e) {
    e.printStackTrace();

    private void kameraGetir() {
        new Thread(() -> {
            try {
                URL url = new URL("https://siber-radar-1.onrender.com/kameralar.json");
                HttpURLConnection con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONArray arr = new JSONArray(sb.toString());

                runOnUiThread(() -> {
                    try {
                        Feature[] features = new Feature[arr.length()];

                        for (int i = 0; i < arr.length(); i++) {
                            JSONArray k = arr.getJSONArray(i);

                            Feature f = Feature.fromGeometry(
                                Point.fromLngLat(
                                    k.getDouble(2),
                                    k.getDouble(1)
                                )
                            );

                            f.addStringProperty(
                                "ad",
                                k.getString(0)
                            );

                            f.addStringProperty(
                                "link",
                                k.getString(3)
                            );

                            features[i] = f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "kamera-source",
                                        fc
                                    );

                                style.addSource(source);

                                kameraLayer =
                                    new CircleLayer(
                                        "kamera-layer",
                                        "kamera-source"
                                    );

                                kameraLayer.setProperties(
                                    circleRadius(7f),
                                    circleColor(Color.BLUE),
                                    circleOpacity(0.9f)
                                );

                                style.addLayer(kameraLayer);
                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void depremGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());
                JSONArray arr = root.getJSONArray("result");

                runOnUiThread(() -> {
                    try {
                        Feature[] features =
                            new Feature[arr.length()];

                        for (int i=0; i<arr.length(); i++) {

                            JSONObject d =
                                arr.getJSONObject(i);

                            Feature f =
                                Feature.fromGeometry(
                                    Point.fromLngLat(
                                        d.getDouble("lng"),
                                        d.getDouble("lat")
                                    )
                                );

                            f.addStringProperty(
                                "yer",
                                d.optString("title","")
                            );

                            f.addNumberProperty(
                                "mag",
                                d.optDouble("mag",0)
                            );

                            features[i]=f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "deprem-source",
                                        fc
                                    );

                                style.addSource(source);

                                depremLayer =
                                    new CircleLayer(
                                        "deprem-layer",
                                        "deprem-source"
                                    );

                                depremLayer.setProperties(
                                    circleRadius(6f),
                                    circleColor(Color.YELLOW),
                                    circleOpacity(0.85f)
                                );

                                style.addLayer(depremLayer);

                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void radarGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.rainviewer.com/public/weather-maps.json"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());

                JSONArray radar =
                    root.getJSONObject("radar")
                    .getJSONArray("past");

                if (radar.length() == 0) return;

                JSONObject son =
                    radar.getJSONObject(radar.length()-1);

                String time =
                    son.getString("path");

                String tile =
                    "https://tilecache.rainviewer.com"
                    + time
                    + "/256/{z}/{x}/{y}/2/1_1.png";

                runOnUiThread(() -> {

                    mapView.getMapAsync(map -> {
                        map.getStyle(style -> {

                            org.maplibre.android.style.sources.RasterSource source =
                                new org.maplibre.android.style.sources.RasterSource(
                                    "radar-source",
                                    tile,
                                    256
                                );

                            style.addSource(source);

                            radarLayer =
                                new org.maplibre.android.style.layers.RasterLayer(
                                    "radar-layer",
                                    "radar-source"
                                );

                            radarLayer.setProperties(
                                org.maplibre.android.style.layers.PropertyFactory.rasterOpacity(0.55f)
                            );

                            style.addLayer(radarLayer);

                        });
                    });

                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

}
                });

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    private void kameraGetir() {
        new Thread(() -> {
            try {
                URL url = new URL("https://siber-radar-1.onrender.com/kameralar.json");
                HttpURLConnection con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("GET");

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONArray arr = new JSONArray(sb.toString());

                runOnUiThread(() -> {
                    try {
                        Feature[] features = new Feature[arr.length()];

                        for (int i = 0; i < arr.length(); i++) {
                            JSONArray k = arr.getJSONArray(i);

                            Feature f = Feature.fromGeometry(
                                Point.fromLngLat(
                                    k.getDouble(2),
                                    k.getDouble(1)
                                )
                            );

                            f.addStringProperty(
                                "ad",
                                k.getString(0)
                            );

                            f.addStringProperty(
                                "link",
                                k.getString(3)
                            );

                            features[i] = f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "kamera-source",
                                        fc
                                    );

                                style.addSource(source);

                                kameraLayer =
                                    new CircleLayer(
                                        "kamera-layer",
                                        "kamera-source"
                                    );

                                kameraLayer.setProperties(
                                    circleRadius(7f),
                                    circleColor(Color.BLUE),
                                    circleOpacity(0.9f)
                                );

                                style.addLayer(kameraLayer);
                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void depremGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());
                JSONArray arr = root.getJSONArray("result");

                runOnUiThread(() -> {
                    try {
                        Feature[] features =
                            new Feature[arr.length()];

                        for (int i=0; i<arr.length(); i++) {

                            JSONObject d =
                                arr.getJSONObject(i);

                            Feature f =
                                Feature.fromGeometry(
                                    Point.fromLngLat(
                                        d.getDouble("lng"),
                                        d.getDouble("lat")
                                    )
                                );

                            f.addStringProperty(
                                "yer",
                                d.optString("title","")
                            );

                            f.addNumberProperty(
                                "mag",
                                d.optDouble("mag",0)
                            );

                            features[i]=f;
                        }

                        FeatureCollection fc =
                            FeatureCollection.fromFeatures(features);

                        mapView.getMapAsync(map -> {
                            map.getStyle(style -> {

                                GeoJsonSource source =
                                    new GeoJsonSource(
                                        "deprem-source",
                                        fc
                                    );

                                style.addSource(source);

                                depremLayer =
                                    new CircleLayer(
                                        "deprem-layer",
                                        "deprem-source"
                                    );

                                depremLayer.setProperties(
                                    circleRadius(6f),
                                    circleColor(Color.YELLOW),
                                    circleOpacity(0.85f)
                                );

                                style.addLayer(depremLayer);

                            });
                        });

                    } catch(Exception e) {
                        e.printStackTrace();
                    }
                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }


    private void radarGetir() {
        new Thread(() -> {
            try {
                URL url = new URL(
                    "https://api.rainviewer.com/public/weather-maps.json"
                );

                HttpURLConnection con =
                    (HttpURLConnection) url.openConnection();

                BufferedReader br = new BufferedReader(
                    new InputStreamReader(con.getInputStream())
                );

                StringBuilder sb = new StringBuilder();
                String line;

                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }

                JSONObject root = new JSONObject(sb.toString());

                JSONArray radar =
                    root.getJSONObject("radar")
                    .getJSONArray("past");

                if (radar.length() == 0) return;

                JSONObject son =
                    radar.getJSONObject(radar.length()-1);

                String time =
                    son.getString("path");

                String tile =
                    "https://tilecache.rainviewer.com"
                    + time
                    + "/256/{z}/{x}/{y}/2/1_1.png";

                runOnUiThread(() -> {

                    mapView.getMapAsync(map -> {
                        map.getStyle(style -> {

                            org.maplibre.android.style.sources.RasterSource source =
                                new org.maplibre.android.style.sources.RasterSource(
                                    "radar-source",
                                    tile,
                                    256
                                );

                            style.addSource(source);

                            radarLayer =
                                new org.maplibre.android.style.layers.RasterLayer(
                                    "radar-layer",
                                    "radar-source"
                                );

                            radarLayer.setProperties(
                                org.maplibre.android.style.layers.PropertyFactory.rasterOpacity(0.55f)
                            );

                            style.addLayer(radarLayer);

                        });
                    });

                });

            } catch(Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

}
