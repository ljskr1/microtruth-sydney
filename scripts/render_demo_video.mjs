import { chromium } from "playwright";
import path from "path";
import fs from "fs";
import { execSync } from "child_process";

const BASE_DIR = path.resolve();
const SLIDES_HTML = path.join(BASE_DIR, "presentation", "pitch_deck.html");
const IMAGES_DIR = path.join(BASE_DIR, "presentation", "frames");
const AUDIO_DIR = path.join(BASE_DIR, "presentation", "audio");
const OUT_DEMO_MP4 = path.join(BASE_DIR, "submission", "demo.mp4");

if (!fs.existsSync(IMAGES_DIR)) {
  fs.mkdirSync(IMAGES_DIR, { recursive: true });
}

async function renderDemoVideo() {
  console.log("Reading slide durations...");
  const durationsData = JSON.parse(fs.readFileSync(path.join(AUDIO_DIR, "durations_au.json"), "utf8"));
  const slides = durationsData.slides;

  console.log("Launching Playwright Chromium at 1920x1080...");
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-gpu"]
  });

  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  console.log(`Loading ${SLIDES_HTML}...`);
  await page.goto(`file://${SLIDES_HTML}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1000);

  // Apply clean full-bleed styling for video capture
  await page.evaluate(() => {
    document.querySelector('.top-bar').style.display = 'none';
    document.querySelector('.bottom-bar').style.display = 'none';
    const container = document.querySelector('.deck-container');
    container.style.padding = '0';
    container.style.height = '1080px';
    container.style.width = '1920px';
    
    document.querySelectorAll('.slide').forEach(s => {
      s.style.top = '0';
      s.style.left = '0';
      s.style.right = '0';
      s.style.bottom = '0';
      s.style.maxWidth = '1920px';
      s.style.maxHeight = '1080px';
      s.style.borderRadius = '0';
      s.style.border = 'none';
      s.style.padding = '80px 100px';
    });
  });

  // Capture each slide frame
  console.log("Capturing high-resolution 1080p slide frames:");
  const framePaths = [];
  for (let i = 1; i <= slides.length; i++) {
    await page.evaluate((idx) => {
      window.showSlide(idx);
    }, i);
    await page.waitForTimeout(400);

    const frameFile = path.join(IMAGES_DIR, `slide_${i}.png`);
    await page.screenshot({ path: frameFile });
    framePaths.push(frameFile);
    console.log(`  Captured Slide ${i} -> ${frameFile}`);
  }

  await browser.close();

  // Create individual video segments per slide matching audio duration + 0.8s pause
  console.log("\nGenerating slide video segments matching Australian voiceover timing:");
  const segmentFiles = [];
  const concatTextPath = path.join(IMAGES_DIR, "concat_segments.txt");
  let concatText = "";

  for (let i = 0; i < slides.length; i++) {
    const slideNum = i + 1;
    const dur = slides[i].duration + (slideNum < slides.length ? 0.8 : 1.2);
    const imgFile = framePaths[i];
    const segFile = path.join(IMAGES_DIR, `segment_${slideNum}.mp4`);

    console.log(`  Slide ${slideNum}: ${dur.toFixed(2)}s video segment...`);
    const cmdSeg = `ffmpeg -y -loop 1 -i "${imgFile}" -c:v libx264 -t ${dur} -pix_fmt yuv420p -r 30 -preset fast -crf 18 "${segFile}" -loglevel error`;
    execSync(cmdSeg);

    segmentFiles.push(segFile);
    concatText += `file '${segFile}'\n`;
  }

  fs.writeFileSync(concatTextPath, concatText);

  // Concat all video segments into master silent video
  console.log("\nConcatenating slide video segments...");
  const masterVideoRaw = path.join(IMAGES_DIR, "slides_master.mp4");
  execSync(`ffmpeg -y -f concat -safe 0 -i "${concatTextPath}" -c copy "${masterVideoRaw}" -loglevel error`);

  // Mux with Australian Master Audio
  const masterAudio = path.join(AUDIO_DIR, "pitch_voiceover_au_mastered.mp3");
  console.log("Muxing video with Australian Neural audio track...");
  
  // Backup existing demo.mp4
  const backupDemo = path.join(BASE_DIR, "submission", "demo_silent_original.mp4");
  if (fs.existsSync(OUT_DEMO_MP4) && !fs.existsSync(backupDemo)) {
    fs.copyFileSync(OUT_DEMO_MP4, backupDemo);
  }

  const finalMuxCmd = `ffmpeg -y -i "${masterVideoRaw}" -i "${masterAudio}" -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest "${OUT_DEMO_MP4}" -loglevel error`;
  execSync(finalMuxCmd);

  console.log(`\n🎉 Successfully rendered Australian Narrated Demo Video to: ${OUT_DEMO_MP4}`);

  // Print output stats
  const probeOutput = execSync(`ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 "${OUT_DEMO_MP4}"`).toString();
  console.log("\nVideo Properties:\n" + probeOutput);
}

renderDemoVideo().catch(err => {
  console.error("Rendering failed:", err);
  process.exit(1);
});
