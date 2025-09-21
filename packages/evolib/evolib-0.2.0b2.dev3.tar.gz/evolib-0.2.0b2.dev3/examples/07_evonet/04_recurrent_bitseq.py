"""
Example: Recurrent Bit Sequence Prediction

This example demonstrates how an EvoNet with recurrent connections
can be evolved to predict the next bit in a fixed binary sequence.
A warm-up phase is used to let the network state settle before
fitness is measured. Visualization combines a raster plot of
input/target/prediction bits with a line plot of prediction quality.
"""

from evolib import Population, Individual, plot_bit_prediction
from evolib.representation.evonet import EvoNet

FRAME_FOLDER = "04_frames"
CONFIG_FILE = "configs/04_recurrent_bitseq.yaml"

#input_seq = [0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1] * 4
#target_seq = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0] * 4

def lfsr_sequence(length: int, seed: int = 0b10011, taps=(5, 2)) -> list[int]:
    """
    Generate a binary sequence using an n-bit LFSR.

    Parameters
    ----------
    length : int
        Number of output bits to generate.
    seed : int, optional
        Initial state (must be non-zero). Default: 0b10011.
    taps : tuple[int], optional
        Tap positions (1-based, e.g. (5, 2) for x^5 + x^2 + 1).

    Returns
    -------
    list[int]
        Generated bit sequence.
    """
    n = max(taps)
    if seed == 0:
        raise ValueError("Seed must be non-zero for LFSR.")
    state = seed & ((1 << n) - 1)

    seq = []
    for _ in range(length):
        bit = state & 1
        seq.append(bit)
        # compute feedback from taps
        fb = 0
        for t in taps:
            fb ^= (state >> (t - 1)) & 1
        state = (state >> 1) | (fb << (n - 1))
    return seq


input_seq = lfsr_sequence(44)
target_seq = input_seq[1:] + [input_seq[0]]  # nächstes Bit als Ziel
warmup_steps = 5


def fitness_bitseq(indiv: Individual) -> float:
    """
    Evaluate how well the EvoNet predicts the next bit in a fixed sequence.
    Errors from the first `warmup_steps` are ignored to allow network state to settle.
    """
    net: EvoNet = indiv.para["brain"].net
    net.reset(full=True)

    total_error = 0.0
    for t in range(len(input_seq)):
        output = net.calc([input_seq[t]])[0]
        if t >= warmup_steps:
            error = output - target_seq[t]
            total_error += error**2

    return total_error / (len(input_seq) - warmup_steps)


def save_plot(pop: Population) -> None:
    """
    Save visualization of the best individual's predictions
    at the current generation.
    """
    best = pop.best()
    y_preds = [best.para["brain"].net.calc([bit])[0] for bit in input_seq]

    plot_bit_prediction(
        true_bits=target_seq,
        pred_values=y_preds,
        input_bits=input_seq,
        title=f"Bit Prediction (gen={pop.generation_num}, MSE={best.fitness:.4f})",
        save_path=f"{FRAME_FOLDER}/gen_{pop.generation_num:03d}.png",
    )
    
    best.para["brain"].net.print_graph("test.png",fillcolors_on=True)


if __name__ == "__main__":
    pop = Population(CONFIG_FILE, fitness_function=fitness_bitseq)
    pop.run(verbosity=1, on_generation_end=save_plot)

    best = pop.best()
    best.para["brain"].net.print_graph("test.png",fillcolors_on=True)

