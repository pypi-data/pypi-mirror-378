"""
Example: Recurrent Bit Sequence Prediction

This example demonstrates how an EvoNet with recurrent connections
can be evolved to predict the next bit in a fixed binary sequence.

Key details:
- The bit sequence is repeated twice.
- The first pass is used as a warm-up so the recurrent state can settle.
- Fitness and accuracy are evaluated only on the second pass.
- Visualization shows input, target, and predictions for the evaluated phase.
"""

from evolib import Population, Individual, plot_bit_prediction
from evolib.representation.evonet import EvoNet

FRAME_FOLDER = "04_frames"
CONFIG_FILE = "configs/04_recurrent_bitseq.yaml"

SEQ_LENGTH = 31
warmup_steps = SEQ_LENGTH

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
        fb = 1
        for t in taps:
            fb ^= (state >> (t - 1)) & 1
        state = (state >> 1) | (fb << (n - 1))
    return seq


def fitness_bitseq(indiv: Individual) -> float:
    """
    Evaluate how well the EvoNet predicts the next bit in a fixed sequence.
    Returns mean squared error (to minimize).
    Additionally logs classification accuracy in indiv.extra_metrics.
    """
    net: EvoNet = indiv.para["brain"].net
    net.reset(full=True)

    total_error = 0.0
    correct = 0
    count = 0


    for t in range(len(input_seq)):
        output = net.calc([input_seq[t]])[0]
        if t >= warmup_steps:
            target = target_seq[t]
            # --- MSE ---
            error = output - target
            total_error += error**2

            # --- Accuracy ---
            pred_bit = 1 if output > 0.5 else 0
            if pred_bit == target:
                correct += 1
            count += 1

    mse = total_error / count
    acc = correct / count if count > 0 else 0.0

    # Log extra metrics
    indiv.extra_metrics = {"accuracy": acc, "mse": mse}

    return mse + (1-acc) / 4


def save_plot(pop: Population) -> None:
    best = pop.best()
    net = best.para["brain"].net
    net.reset(full=True)

    print(
            f"id: {best.id[:6]} "
          f"ms: {best.para["brain"].evo_params.mutation_strength} "
          f"mse: {best.extra_metrics.get("mse", best.fitness):.5} "
          f"acc: {best.extra_metrics.get("accuracy", 0.0):.3%}")

    # Warmup
    for bit in input_seq[:SEQ_LENGTH]:
        net.calc([bit])

    # Prediction
    y_preds = [net.calc([bit])[0] for bit in input_seq[SEQ_LENGTH:]]

    true_bits = target_seq[SEQ_LENGTH:]
    input_bits = input_seq[SEQ_LENGTH:]

    acc = best.extra_metrics.get("accuracy", 0.0)
    mse = best.extra_metrics.get("mse", best.fitness)

    plot_bit_prediction(
        true_bits=true_bits,
        pred_values=y_preds,
        input_bits=input_bits,
        title=(
            f"Bit Prediction (gen={pop.generation_num}, "
            f"MSE={mse:.5f}, Acc={acc:.3%})"
        ),
        save_path=f"{FRAME_FOLDER}/gen_{pop.generation_num:03d}.png",
    )

    best = pop.best()
    best.para["brain"].net.print_graph("test.png",fillcolors_on=True)


input_seq = lfsr_sequence(SEQ_LENGTH) * 2
target_seq = input_seq[1:] + [input_seq[0]]


if __name__ == "__main__":
    pop = Population(CONFIG_FILE, fitness_function=fitness_bitseq)
    pop.run(verbosity=1, on_generation_end=save_plot)

    best = pop.best()
    best.para["brain"].net.print_graph("test.png",fillcolors_on=True)

