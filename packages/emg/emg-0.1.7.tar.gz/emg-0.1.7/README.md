# Eulerian Melody Generator

**emg** is a Python library for generating algorithmic melodies using Eulerian paths with de Bruijn graphs. It can compose a melody from stochastically generated musical motifs by building a Eulerian path, visualize the related de Bruijn graph, and export the melody as an MP3 using a SoundFont file. MuseScore has a number of SoundFont files (e.g., *TimGM6mb.sf2*) that can be downloaded [here](https://musescore.org/en/handbook/3/soundfonts-and-sfz-files).

---

## ✨ Features

- Stochastically generate musical motifs (or k-mers) over a chosen musical scale
- Build and visualize a de Bruijn graph from the musical motifs
- Find Eulerian paths in the graph to create coherent melodic sequences
- Export melodies in MP3 format and de Bruijn graphs in PNG format
- Several configurable parameters: scale, tempo, k‑mer length, repeats, etc.

---

## 📦 Installation

```bash
pip install emg
```

Built for Python 3.12 or above.

**System Prerequisites:**

- [FFmpeg](https://ffmpeg.org/)
- [FluidSynth](https://www.fluidsynth.org/)

These tools can be installed using Homebrew on Mac OS:

```bash
brew install ffmpeg
brew install fluid-synth
```

---

## 🚀 Quick Start

```Python
from emg.generator import EulerianMelodyGenerator

# Path to your SoundFont file
sf2_path = "TimGM6mb.sf2"

# Create a generator instance
generator = EulerianMelodyGenerator(
    soundfont_path=sf2_path,
    scale="C-Major-Pentatonic",
    bpm=200,
    kmer_length=4,
    num_kmers=8,
    num_repeats=8,
    random_seed=2
)

# Run the full pipeline
generator.run_generation_pipeline(
    graph_png_path="graph.png",
    mp3_output_path="melody.mp3"
)
```

Use FFmpeg to convert the MP3 file to an MP4 file (taking the PNG export of the de Bruijn graph - or some other image - as cover art), for uploading to platforms such as YouTube:
```Bash
ffmpeg -loop 1 -i graph.png -i melody.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest melody.mp4
```

---

## 📚 API Reference

See [here](https://github.com/ckstash/emg/blob/main/API.md)
