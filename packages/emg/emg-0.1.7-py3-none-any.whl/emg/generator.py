import os
import contextlib
import random
import subprocess
from collections import defaultdict
from midiutil import MIDIFile
from midi2audio import FluidSynth
import networkx as nx
import matplotlib.pyplot as plt


class EulerianMelodyGenerator:
    """Generates melodies using Eulerian paths in De Bruijn graphs."""

    NOTE_TO_OFFSET = {
        "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4,
        "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9,
        "A#": 10, "B": 11
    }

    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    NAT_MINOR = [0, 2, 3, 5, 7, 8, 10]
    MAJOR_PENTA = [0, 2, 4, 7, 9]
    MINOR_PENTA = [0, 3, 5, 7, 10]
    MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
    DORIAN = [0, 2, 3, 5, 7, 9, 10]

    def __init__(self, soundfont_path, scale="C-Major-Pentatonic", bpm=200,
                 kmer_length=4, num_kmers=8, num_repeats=8, random_seed=2):
        """
        Initialize the melody generator.

        Args:
            soundfont_path (str): Path to the .sf2 SoundFont file.
            scale (str): Musical scale in the format "Key-ScaleName", where key is in the set {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"}, and ScaleName is in the set {"Major", "Natural-Minor", "Major-Pentatonic", "Minor-Pentatonic", "Mixolydian", "Dorian"}.
            bpm (int): Beats per minute.
            kmer_length (int): Length of each k-mer.
            num_kmers (int): Number of k-mers to generate.
            num_repeats (int): Number of times to repeat the final note sequence.
            random_seed (int): Seed for reproducibility.
        """
        self.soundfont_path = soundfont_path
        self.scale_name = scale
        self.bpm = bpm
        self.kmer_length = kmer_length
        self.num_kmers = num_kmers
        self.num_repeats = num_repeats
        self.random_seed = random_seed
        self.scale_dict = self._generate_scale_dict()

    def _generate_scales_all_keys(self, scale_name, intervals):
        """Build a given scale in all 12 keys."""
        scales = {}
        chromatic = list(self.NOTE_TO_OFFSET.keys())
        for i, root in enumerate(chromatic):
            notes = [chromatic[(i + step) % 12] for step in intervals]
            key_name = f"{root}-{scale_name}"
            scales[key_name] = notes
        return scales

    def _generate_scale_dict(self):
        """Build the master dictionary of all keys."""
        scale_dict = {}
        scale_dict.update(self._generate_scales_all_keys("Major", self.MAJOR))
        scale_dict.update(self._generate_scales_all_keys("Natural-Minor", self.NAT_MINOR))
        scale_dict.update(self._generate_scales_all_keys("Major-Pentatonic", self.MAJOR_PENTA))
        scale_dict.update(self._generate_scales_all_keys("Minor-Pentatonic", self.MINOR_PENTA))
        scale_dict.update(self._generate_scales_all_keys("Mixolydian", self.MIXOLYDIAN))
        scale_dict.update(self._generate_scales_all_keys("Dorian", self.DORIAN))
        return scale_dict

    def generate_eulerian_kmers(self, k, count, scale_notes, seed=42):
        """Generate k-mers over the given scale that form a connected De Bruijn graph."""
        random.seed(seed)
        if count < 1:
            return []

        start_node = tuple(random.choice(scale_notes) for _ in range(k - 1))
        nodes = {start_node}
        edges = []
        out_deg = defaultdict(int)
        in_deg = defaultdict(int)

        current = start_node
        for _ in range(count):
            next_note = random.choice(scale_notes)
            next_node = tuple(list(current[1:]) + [next_note])
            edges.append(current + (next_note,))
            nodes.add(next_node)
            out_deg[current] += 1
            in_deg[next_node] += 1
            current = next_node

        start_candidates = [n for n in nodes if out_deg[n] - in_deg[n] > 0]
        end_candidates = [n for n in nodes if in_deg[n] - out_deg[n] > 0]

        if len(start_candidates) > 1 or len(end_candidates) > 1:
            return self.generate_eulerian_kmers(k, count, scale_notes, seed + 1)

        return edges

    def build_debruijn_graph(self, kmers):
        """Build De Bruijn-style graph."""
        adj = defaultdict(list)
        in_deg = defaultdict(int)
        out_deg = defaultdict(int)
        for kmer in kmers:
            prefix = tuple(kmer[:-1])
            suffix = tuple(kmer[1:])
            adj[prefix].append(suffix)
            out_deg[prefix] += 1
            in_deg[suffix] += 1
        return adj, in_deg, out_deg

    def generate_and_save_graph(self, graph_dict, output_file=None, seed=100, k=1):
        """
        Visualize a De Bruijn graph and save it as a PNG.

        Args:
            graph_dict (dict): Adjacency list of the graph.
            output_file (str, optional): Path to save the PNG file. Defaults to None (current dir).
            seed (int): Layout seed.
            k (float): Node spacing parameter.
        """
        if output_file is None:
            output_file = os.path.join(os.getcwd(), "graph.png")

        G = nx.DiGraph()
        for prefix, suffixes in graph_dict.items():
            for suffix in suffixes:
                G.add_edge(prefix, suffix)

        pos = nx.spring_layout(G, seed=seed, k=k)
        plt.figure(figsize=(10, 8))
        nx.draw_networkx_nodes(G, pos, node_size=1600, node_color="skyblue", edgecolors="black")
        nx.draw_networkx_edges(G, pos, arrowstyle="-|>", arrowsize=20, edge_color="black",
                               connectionstyle="arc3,rad=0.1", min_source_margin=20, min_target_margin=20)
        nx.draw_networkx_labels(G, pos, labels={node: " ".join(node) for node in G.nodes()}, font_size=10)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_file, format="PNG", dpi=300)
        plt.close()

    def find_eulerian_path(self, adj, in_deg, out_deg):
        """Find an Eulerian path in the De Bruijn-style graph."""
        start = None
        for node in set(list(adj) + list(in_deg)):
            if out_deg[node] - in_deg[node] == 1:
                start = node
                break
        if start is None:
            start = next(n for n in adj if adj[n])
        stack = [start]
        path = []
        local_adj = {u: vs[:] for u, vs in adj.items()}
        while stack:
            v = stack[-1]
            if local_adj.get(v):
                u = local_adj[v].pop()
                stack.append(u)
            else:
                path.append(stack.pop())
        return path[::-1]

    def flatten_path(self, path_nodes):
        """Flatten a list of note tuples into a single list."""
        flattened = []
        for kmer in path_nodes:
            flattened.extend(kmer)
        return flattened

    def _note_with_octave_to_midi(self, note, octave):
        """Convert a note with octave to MIDI number."""
        return 12 * (octave + 1) + self.NOTE_TO_OFFSET[note]

    @contextlib.contextmanager
    def _suppress_fd_output(self):
        """Suppress stdout and stderr at the OS file descriptor level."""
        with open(os.devnull, 'w') as devnull:
            old_stdout_fd = os.dup(1)
            old_stderr_fd = os.dup(2)
            try:
                os.dup2(devnull.fileno(), 1)
                os.dup2(devnull.fileno(), 2)
                yield
            finally:
                os.dup2(old_stdout_fd, 1)
                os.dup2(old_stderr_fd, 2)
                os.close(old_stdout_fd)
                os.close(old_stderr_fd)

    def compose_and_export(self, final_notes, mp3_file=None, midi_file=None, wav_file=None):
        """
        Compose a melody from notes and export as MP3.

        Args:
            final_notes (list): List of note names (without octaves).
            mp3_file (str, optional): Path to save the MP3 file. Defaults to None (current dir).
            midi_file (str, optional): Path to save the intermediate MIDI file. Defaults to None.
            wav_file (str, optional): Path to save the intermediate WAV file. Defaults to None.
        """
        # Default file paths if None
        if mp3_file is None:
            mp3_file = os.path.join(os.getcwd(), "output.mp3")
        if midi_file is None:
            midi_file = os.path.join(os.getcwd(), "output.mid")
        if wav_file is None:
            wav_file = os.path.join(os.getcwd(), "temp.wav")

        # Create MIDI file
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTrackName(track, time, "Eulerian Melody")
        midi.addTempo(track, time, self.bpm)

        # Assign octaves and write notes
        octave = 5
        duration = 1
        volume = 100
        for note in final_notes:
            midi_note = self._note_with_octave_to_midi(note, octave)
            midi.addNote(track, channel=0, pitch=midi_note,
                         time=time, duration=duration, volume=volume)
            time += 1

        with open(midi_file, "wb") as output_file:
            midi.writeFile(output_file)

        # Convert MIDI to WAV using FluidSynth
        fs = FluidSynth(self.soundfont_path)
        with self._suppress_fd_output():
            fs.midi_to_audio(midi_file, wav_file)

        # Convert WAV to MP3 using ffmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_file, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Clean up intermediate files
        for f in [midi_file, wav_file]:
            if os.path.exists(f):
                os.remove(f)

    def run_generation_pipeline(self, graph_png_path, mp3_output_path):
        """
        Run the full melody generation pipeline:
        1. Generate k-mers
        2. Build De Bruijn graph
        3. Save graph visualization
        4. Find Eulerian path
        5. Flatten to note sequence
        6. Repeat sequence and export as MP3

        Args:
            graph_png_path (str): Path to save the graph PNG.
            mp3_output_path (str): Path to save the MP3 file.
        """
        # Step 1: Generate k-mers
        scale_notes = self.scale_dict[self.scale_name]
        kmers = self.generate_eulerian_kmers(
            self.kmer_length, self.num_kmers, scale_notes, seed=self.random_seed
        )

        # Step 2: Build graph
        adj, in_deg, out_deg = self.build_debruijn_graph(kmers)

        # Step 3: Save graph visualization
        self.generate_and_save_graph(adj, graph_png_path)

        # Step 4: Find Eulerian path
        path_nodes = self.find_eulerian_path(adj, in_deg, out_deg)

        # Step 5: Flatten to note sequence
        flattened_notes = self.flatten_path(path_nodes)

        # Step 6: Repeat and export
        final_notes = flattened_notes * self.num_repeats
        self.compose_and_export(final_notes, mp3_output_path)

