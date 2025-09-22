"""Make plots comparing single sample performance."""

import functools
from pathlib import Path

import pandas as pd

from cryovit.types import Sample
from cryovit.visualization.utils import (
    compute_stats,
    merge_experiments,
    significance_test,
)


def _plot_df(
    df: pd.DataFrame,
    pvalues: pd.Series,
    key: str,
    title: str,
    file_name: str,
):
    # import here to avoid unnecessary dependencies if function not used
    import matplotlib
    import matplotlib.pyplot as plt
    import seaborn as sns
    from statannotations.Annotator import Annotator

    matplotlib.use("Agg")
    colors = sns.color_palette("deep")[:3]
    sns.set_theme(style="darkgrid", font="Open Sans")

    hue_palette = {
        "3D U-Net": colors[0],
        "CryoViT": colors[1],
        "CryoViT with Sparse Labels": colors[1],
        "CryoViT with Dense Labels": colors[2],
    }

    sample_counts = df["sample"].value_counts()
    num_models = df[key].nunique()
    n_samples = df["sample"].nunique()
    sorted_samples = sample_counts.sort_values(ascending=True).index.tolist()
    fig = plt.figure(figsize=(12 if n_samples > 6 else 6, 6))
    ax = plt.gca()

    params = {
        "x": "sample",
        "y": "dice_metric",
        "hue": key,
        "data": df,
        "order": sorted_samples,
    }

    sns.boxplot(
        showfliers=False,
        palette=hue_palette,
        linewidth=1,
        medianprops={"linewidth": 2, "color": "firebrick"},
        ax=ax,
        **params,
    )
    sns.stripplot(
        dodge=True,
        marker=".",
        alpha=0.5,
        palette="dark:black",
        ax=ax,
        **params,
    )

    k1, k2 = df[key].unique()
    pairs = [[(s, k1), (s, k2)] for s in pvalues.index]

    annotator = Annotator(ax, pairs, **params)
    annotator.configure(color="blue", line_width=1, verbose=False)
    annotator.set_pvalues_and_annotate(pvalues.values)

    current_labels = ax.get_xticklabels()
    new_labels = [
        f"{Sample[label.get_text()].value}\n(n={sample_counts[label.get_text()] // num_models})"
        for label in current_labels
    ]

    ax.set_xticks(range(len(new_labels)))
    ax.set_xticklabels(new_labels, ha="center")
    ax.set_ylim(-0.05, 1.15)
    ax.set_xlabel("")
    ax.set_ylabel("")

    fig.suptitle(title)
    fig.supxlabel("Sample Name (Count)")
    fig.supylabel("Dice Score")

    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles[:2], labels[:2], loc="lower center", shadow=True)

    plt.tight_layout()
    plt.savefig(f"{file_name}.svg")
    plt.savefig(f"{file_name}.png", dpi=300)


def process_single_experiment(
    exp_type: str,
    exp_group: str,
    exp_names: dict[str, list[str]],
    exp_dir: Path,
    result_dir: Path,
):
    """Plot single sample experiment results with box and strip plots including annotations for statistical tests.

    Args:
        exp_type (str): Type of experiment, e.g. "single", "sparse"
        exp_group (str): Group of experiments, e.g. "hd", "ad"
        exp_names (dict[str, list[str]]): Dictionary mapping experiment names to model used
        exp_dir (Path): Directory containing experiment results
        result_dir (Path): Directory to save results
    """

    result_dir.mkdir(parents=True, exist_ok=True)
    df = merge_experiments(exp_dir, exp_names, keys=["model"])
    test_fn = functools.partial(
        significance_test,
        model_A=(
            "CryoViT" if exp_type != "sparse" else "CryoViT with Sparse Labels"
        ),
        model_B=(
            "3D U-Net" if exp_type != "sparse" else "CryoViT with Dense Labels"
        ),
        key="model",
        test_fn="wilcoxon",
    )
    p_values = compute_stats(
        df,
        group_keys=["sample", "model"],
        file_name=str(result_dir / f"{exp_group}_{exp_type}_stats.csv"),
        test_fn=test_fn,
    )

    if exp_type != "sparse":
        _plot_df(
            df,
            p_values,
            "model",
            f"Model Comparison on Individual {exp_group.upper()} Samples for Mitochondria",
            str(result_dir / f"{exp_group}_{exp_type}_comparison"),
        )
    else:
        _plot_df(
            df,
            p_values,
            "model",
            "CryoViT: Sparse vs Dense Labels Comparison on Individual Samples",
            str(result_dir / "sparse_vs_dense_comparison"),
        )
