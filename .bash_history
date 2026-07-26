<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<title>Siber Afet Radarı v18.8</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
:root{
--bg-main:#030712;
--bg-panel:#0b0f19;
--neon-color:#00ecff;
--text-color:#00ecff;
}

html,body{
margin:0;
padding:0;
width:100%;
height:100%;
overflow:hidden;
background:#030712;
color:#00ecff;
font-family:monospace;
}

.top-nav{
height:auto;
padding:8px;
background:#0b0f19;
border-bottom:2px solid #00ecff;
display:flex;
justify-content:space-between;
align-items:center;
}

.brand-title{
font-weight:bold;
}

button{
background:#030712;
color:#00ecff;
border:1px solid #00ecff;
padding:6px;
border-radius:5px;
}

.map-container{
height:38vh;
position:relative;
}

#map{
height:100%;
width:100%;
}

#rainAlertBtn{
display:none;
position:absolute;
top:10px;
right:10px;
z-index:9999;
background:#0284c7;
color:white;
padding:8px 12px;
border-radius:8px;
font-weight:bold;
box-shadow:0 0 10px #0284c7;
}

#rainPopup{
display:none;
position:absolute;
top:55px;
right:10px;
z-index:9999;
background:#080d18;
border:2px solid #00ecff;
color:#00ecff;
padding:10px;
width:230px;
border-radius:8px;
}

.weather-panel{
display:flex;
overflow-x:auto;
background:#0b0f19;
padding:8px;
}

.bottom-area{
height:55vh;
overflow:auto;
}

.eq-item{
border:1px solid #00ecff;
padding:10px;
margin:5px;
}

</style>
</head>
<body>
<div class="top-nav">
    <div class="brand-title">📡 SİBER RADAR v18.8</div>
    <div>
        <button onclick="toggleRain()">🌧️ YAĞIŞ</button>
        <button onclick="riskGoster()">📊 RİSK</button>
    </div>
</div>

<div class="map-container">

    <div id="rainAlertBtn" onclick="toggleRain()">
        🌧️ YAĞIŞ ALARMI
    </div>

    <div id="rainPopup">
        <b>🌧️ Aktif Yağış Bölgeleri</b>
        <hr>
        <div id="rainList">
            Kontrol ediliyor...
        </div>
    </div>

    <div id="map"></div>

</div>


<div class="weather-panel">
    <div>🌤️ İSTANBUL <b id="w-ist">--</b></div>
    <div>🏛️ EDİRNE <b id="w-ank">--</b></div>
    <div>🌊 İZMİR <b id="w-izm">--</b></div>
    <div>☀️ ADANA <b id="w-adn">--</b></div>
    <div>🌴 MERSİN <b id="w-mer">--</b></div>
    <div>🔥 ANTALYA <b id="w-ant">--</b></div>
</div>


<div class="bottom-area">

<div id="list">
    Radar verileri işleniyor...
</div>

</div>


<div id="miniRisk" style="
display:none;
position:fixed;
top:80px;
right:10px;
background:#080d18;
border:1px solid #00ecff;
padding:10px;
z-index:9999;
color:white;">
    
🔵 Düşük:
<span id="riskLow">0%</span>
<br>

🟢 Orta:
<span id="riskMid">0%</span>
<br>

🔴 Yüksek:
<span id="riskHigh">0%</span>

</div>


<script>

let map = L.map('map').setView([38.9,35.5],6);


L.tileLayer(
'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
).addTo(map);



function toggleRain(){

let p=document.getElementById("rainPopup");

p.style.display =
p.style.display==="block"
?"none"
:"block";

}



function yagisKontrol(){

fetch(
"https://api.rainviewer.com/public/weather-maps.json"
)
// Flask'tan gelen kamera verisi
let kameralarVerisi = {{ kameralar | tojson }};


function riskGoster(){

let r=document.getElementById("miniRisk");

r.style.display =
r.style.display==="block"
?"none"
:"block";


if(r.style.display==="block"){
miniRiskGuncelle();
}

}



function miniRiskGuncelle(){

fetch('/api/risk')

.then(r=>r.json())

.then(d=>{

document.getElementById("riskLow").innerHTML =
d.dusuk+"%";

document.getElementById("riskMid").innerHTML =
d.orta+"%";

document.getElementById("riskHigh").innerHTML =
d.yuksek+"%";

});

}




function depremleriYenile(){

fetch('/api')

.then(r=>r.json())

.then(data=>{


let liste=document.getElementById("list");

liste.innerHTML="";


data.forEach(d=>{


if(d.mag>=3){

liste.innerHTML +=

`
<div class="eq-item">

🕒 ${d.zaman}

<br>

📍 <b>${d.yer}</b>

<br>

💥 Şiddet:
<b>${d.mag}</b>

</div>
`;



L.circleMarker(
[d.lat,d.lng],
{
radius:d.mag*2,
color:"#ff4500",
fillColor:"#ff4500",
fillOpacity:.8
}

).addTo(map);



}


});


});


}



depremleriYenile();

setInterval(
depremleriYenile,
60000
);



miniRiskGuncelle();

setInterval(
miniRiskGuncelle,
60000
);



</script>

</body>
</html>
PY

ls -lh templates/index.html
python app.py
cat templates/index.html
unzip -l siber_radar_yedek_20260723_120431.zip
unzip -p siber_radar_yedek_20260723_120431.zip templates/index.html > templates/index.html
ls -lh templates/index.html
pkill -f app.py
python app.py
cat templates/index.html > /sdcard/index_mevcut.txt
split -b 8000 /sdcard/index_mevcut.txt /sdcard/index_parca_
ls /sdcard/index_parca_*
cat /sdcard/index_parca_aa
cat /sdcard/index_parca_ab
wc -l templates/index.html
tail -80 templates/index.html
cp templates/index.html templates/index_yagmur_yedek.html
python - <<'PY'
from pathlib import Path

p=Path("templates/index.html")
s=p.read_text(encoding="utf-8")

s=s.replace(
'<div class="map-container">',
'''<div class="map-container">

<button id="rainAlertBtn" onclick="toggleRain()" style="
display:none;
position:absolute;
top:10px;
right:10px;
z-index:9999;
background:#0284c7;
color:white;
border:2px solid #00ecff;
padding:8px;
border-radius:8px;
font-weight:bold;">
🌧️ YAĞIŞ ALARMI
</button>

<div id="rainPopup" style="
display:none;
position:absolute;
top:55px;
right:10px;
z-index:9999;
background:#080d18;
color:#00ecff;
border:2px solid #00ecff;
padding:10px;
border-radius:8px;
width:230px;">
<b>🌧️ Aktif Yağış Bölgeleri</b>
<hr>
<div id="rainList">Kontrol ediliyor...</div>
</div>'''
)

s=s.replace(
'</script>',
'''
function toggleRain(){
 let p=document.getElementById("rainPopup");
 p.style.display =
 p.style.display==="block" ? "none":"block";
}

function yagisKontrol(){

fetch('/api/weather')
.then(r=>r.json())
.then(data=>{

let yagis=[];

data.forEach(s=>{

if(s.nem>=70){
yagis.push("🌧️ "+s.isim+" Nem: "+s.nem+"%");
}

});


if(yagis.length){

document.getElementById("rainAlertBtn").style.display="block";

document.getElementById("rainList").innerHTML =
yagis.join("<br>");

}else{

document.getElementById("rainAlertBtn").style.display="none";

}

});

}

yagisKontrol();
setInterval(yagisKontrol,60000);

</script>'''
)

p.write_text(s,encoding="utf-8")

print("YAĞIŞ SİSTEMİ EKLENDİ")
PY

pkill -f app.py
python app.py
wc -l templates/index.html
python -m py_compile app.py
pkill -f app.py
python app.py
/api/rain
grep -n "rain" app.py
grep -n "@app.route" app.py
cat app.py
cd /data/data/com.termux/files/home
cp app.py app_eski.py
cp templates/index.html templates/index_eski.html
cat > app.py <<'PY'
ls -lh app.py app_yedek_son.py
pwd
wc -l app.py templates/index.html
cat app.py
cat app.py > /sdcard/app_mevcut.txt
cat templates/index.html > /sdcard/index_mevcut.txt
wc -l /sdcard/app_mevcut.txt /sdcard/index_mevcut.txt
ls -la
ls -la *.tar.gz *.zip 2>/dev/null
unzip -o siber_radar_yedek_20260723_120431.zip
python app.py
rm app.py
nano app.py
truncate -s 0 ./templates/index.html
nano templates/index.html
pkill -9 -f app.py ; python app.py
rm app.py
nano app.py
truncate -s 0 ./templates/index.html
nano templates/index.html
<html lang="tr">
<head>
</head>
<body>
</body>
</html>
nano templates/index.html
truncate -s 0 ./templates/index.html
nano templates/index.htmlnano templates/index.html
pkill -9 -f app.py ; python app.py
