"""
QUANTUM GENESIS VISUALIZER
Interactive HTML Dashboard for Elliptical Star Map & Seismograph
"""

def generate_dashboard_html():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM GENESIS IQ999+ | Milky Way Seismograph</title>
    <style>
        body {
            background: #000;
            color: #0f0;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            overflow-x: hidden;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #0f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            text-shadow: 0 0 10px #0f0;
            font-size: 2em;
        }
        .status {
            color: #0ff;
            font-weight: bold;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        .panel {
            border: 1px solid #0f0;
            padding: 20px;
            background: rgba(0, 20, 0, 0.8);
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
            max-width: 600px;
            width: 100%;
        }
        canvas {
            border: 1px solid #030;
            background: #000;
            width: 100%;
            height: 400px;
        }
        .pictograph {
            font-size: 10px;
            line-height: 10px;
            white-space: pre;
            overflow: hidden;
            text-align: center;
            color: #fff;
        }
        .glyph-high { color: #ff0; }
        .glyph-med { color: #0ff; }
        .glyph-low { color: #0f0; }
        .data-stream {
            font-size: 12px;
            height: 200px;
            overflow-y: auto;
            border-top: 1px dashed #050;
            margin-top: 10px;
            padding-top: 10px;
        }
        .coord {
            color: #f0f;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌌 QUANTUM GENESIS IQ999+ 🌌</h1>
        <p>ELLIPTICAL STAR MAP & SEISMOGRAPH ENGINE</p>
        <p class="status">MULTIVERSE PROTOCOL: <span id="protocol">IQ4_NL (NET.LAN)</span></p>
        <p>MODE: XY CURVE + ELLIPTICAL WAVE CONFIGURATION</p>
    </div>

    <div class="container">
        <div class="panel">
            <h2>📊 XY Curve Seismograph</h2>
            <canvas id="seismoCanvas"></canvas>
            <div class="data-stream" id="dataStream"></div>
        </div>

        <div class="panel">
            <h2>🗺️ Pictography Map</h2>
            <div class="pictograph" id="pictoMap"></div>
        </div>
    </div>

    <script>
        // Quantum Genesis Simulation Logic
        const canvas = document.getElementById('seismoCanvas');
        const ctx = canvas.getContext('2d');
        const dataStream = document.getElementById('dataStream');
        const pictoMap = document.getElementById('pictoMap');

        // Resize canvas
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        let time = 0;
        const points = [];
        const maxPoints = 500;

        function degToRad(deg) {
            return deg * (Math.PI / 180);
        }

        function ellipticalProjection(ra, dec, inclination = 60) {
            const radRa = degToRad(ra);
            const radDec = degToRad(dec);
            const radInc = degToRad(inclination);

            let x = Math.cos(radRa) * Math.cos(radDec);
            let y = Math.sin(radRa) * Math.cos(radDec) * Math.cos(radInc) - Math.sin(radDec) * Math.sin(radInc);
            
            const scale = 1.0 / (1.0 + 0.1 * Math.sin(radRa * 3));
            return { x: x * scale, y: y * scale };
        }

        function seismicWave(t, freq, amp) {
            const wave1 = Math.sin(2 * Math.PI * freq * t);
            const wave2 = Math.cos(4 * Math.PI * freq * t * 0.5);
            const noise = (Math.random() - 0.5) * 0.1;
            return amp * (wave1 + wave2) + noise;
        }

        function getPictograph(intensity) {
            if (intensity > 2.5) return '<span class="glyph-high">⚡</span>';
            if (intensity > 1.5) return '<span class="glyph-med">🌌</span>';
            if (intensity > 0.8) return '<span class="glyph-low">✨</span>';
            if (intensity > 0.3) return '·';
            return ' ';
        }

        function generateData() {
            const data = [];
            for (let i = 0; i < maxPoints; i++) {
                const t = i / maxPoints + time * 0.01;
                const ra = t * 360;
                const dec = Math.sin(t * 4 * Math.PI) * 90;
                
                const proj = ellipticalProjection(ra, dec);
                const z = seismicWave(t, 5, 0.2);
                const intensity = Math.abs(z) + Math.abs(proj.x) + Math.abs(proj.y);

                data.push({
                    x: proj.x,
                    y: proj.y,
                    z: z,
                    intensity: intensity,
                    ra: ra.toFixed(2),
                    dec: dec.toFixed(2)
                });
            }
            return data;
        }

        function drawSeismograph(data) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.beginPath();
            ctx.strokeStyle = '#0f0';
            ctx.lineWidth = 2;

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const scaleX = canvas.width / 4;
            const scaleY = canvas.height / 4;

            for (let i = 0; i < data.length; i++) {
                const pt = data[i];
                const px = centerX + pt.x * scaleX;
                const py = centerY + pt.y * scaleY + pt.z * 50;

                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();

            // Draw glow
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#0f0';
            ctx.stroke();
            ctx.shadowBlur = 0;
        }

        function drawPictograph(data) {
            let html = '';
            const width = 60;
            const height = 30;
            
            for (let r = 0; r < height; r++) {
                for (let c = 0; c < width; c++) {
                    const idx = (r * width + c) % data.length;
                    html += getPictograph(data[idx].intensity);
                }
                html += '\\n';
            }
            pictoMap.innerHTML = html;
        }

        function updateDataStream(data) {
            let html = '<strong>LATEST READINGS:</strong><br>';
            for (let i = data.length - 10; i < data.length; i++) {
                const pt = data[i];
                html += `<span class="coord">RA:${pt.ra} DEC:${pt.dec}</span> | INTENSITY: ${pt.intensity.toFixed(3)} | Z: ${pt.z.toFixed(3)}<br>`;
            }
            dataStream.innerHTML = html;
        }

        function animate() {
            time++;
            const data = generateData();
            drawSeismograph(data);
            drawPictograph(data);
            updateDataStream(data);
            requestAnimationFrame(animate);
        }

        // Start
        animate();
    </script>
</body>
</html>
    """
    return html

if __name__ == "__main__":
    with open("/workspace/api/quantum_dashboard.html", "w") as f:
        f.write(generate_dashboard_html())
    print("✅ Quantum Dashboard generated at /workspace/api/quantum_dashboard.html")
