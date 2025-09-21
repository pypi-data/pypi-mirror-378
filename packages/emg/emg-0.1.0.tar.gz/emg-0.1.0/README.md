# Eulerian Melody Generator

**emg** is a Python library for generating algorithmic melodies using **Eulerian paths** in **De Bruijn graphs**.  
It can visualize the generated graph, compose a melody in MIDI, and export it as an MP3 using a SoundFont.

## Features

- Generate **k‑mers** over a chosen musical scale
- Build and visualize **De Bruijn graphs**
- Find **Eulerian paths** to create coherent melodic sequences
- Export melodies as **MIDI** and **MP3**
- Fully configurable parameters: scale, tempo, k‑mer length, repeats, and more
- Designed for reproducibility with a random seed

## Installation

```bash
pip install emg
```

## API Documentation

See [here](https://github.com/ckstash/emg/blob/main/API.md)

## Example Usage

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