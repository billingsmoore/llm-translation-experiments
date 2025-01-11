import os
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd


def normalize_term(term):
    """Normalize terms accounting for variations"""
    # Convert to lowercase
    term = str(term).lower().strip()
    # Remove possessives
    term = re.sub(r"'s$", "", term)
    # Remove plural s
    term = re.sub(r"s$", "", term)
    # Remove common derived forms
    term = re.sub(r"(ic|ing|ed|ly)$", "", term)
    return term


def analyze_translations(df):
    """Analyze translation consistency for a dataframe"""
    # Group by source word
    groups = df.groupby("Word")
    metrics = {}

    for word, group in groups:
        # Get all translations for this word
        translations = group["Translation"].tolist()
        normalized_translations = [normalize_term(t) for t in translations]

        # Count occurrences of each normalized translation
        translation_counts = pd.Series(normalized_translations).value_counts()
        most_common_count = translation_counts.iloc[0]

        # Calculate consistency score for this word
        consistency_score = (most_common_count / len(translations)) * 100

        # Store metrics
        metrics[word] = {
            "total_occurrences": len(translations),
            "unique_translations": len(translation_counts),
            "consistency_score": consistency_score,
            "translations": dict(translation_counts),
        }

    # Calculate overall metrics
    total_terms = len(df)
    total_consistent = sum(
        m["total_occurrences"] * (m["consistency_score"] / 100)
        for m in metrics.values()
    )
    overall_consistency = (total_consistent / total_terms) * 100

    return {
        "per_term_metrics": metrics,
        "overall_consistency": overall_consistency,
        "total_terms": total_terms,
        "avg_unique_translations": sum(
            m["unique_translations"] for m in metrics.values()
        )
        / len(metrics),
    }


def plot_comparison(metrics_dict, output_file="translation_comparison.png"):
    """Create comparison plots for multiple translation methods"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Prepare data for plotting
    methods = list(metrics_dict.keys())
    consistency_scores = [
        metrics["overall_consistency"] for metrics in metrics_dict.values()
    ]
    avg_translations = [
        metrics["avg_unique_translations"] for metrics in metrics_dict.values()
    ]

    # Color palette for bars
    colors = plt.cm.Set3(np.linspace(0, 1, len(methods)))

    # Plot consistency scores
    bars1 = ax1.bar(methods, consistency_scores, color=colors)
    ax1.set_title("Overall Consistency Score")
    ax1.set_ylabel("Consistency Score (%)")
    ax1.tick_params(axis="x", rotation=45)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
        )

    # Plot average unique translations
    bars2 = ax2.bar(methods, avg_translations, color=colors)
    ax2.set_title("Average Unique Translations per Term")
    ax2.set_ylabel("Average Count")
    ax2.tick_params(axis="x", rotation=45)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.2f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    plt.close()


def print_detailed_metrics(metrics_dict):
    """Print detailed metrics for all translation methods"""
    print("\nDetailed Analysis")
    print("=" * 50)

    for method, metrics in metrics_dict.items():
        print(f"\n{method}")
        print("-" * len(method))
        print(f"Overall Consistency Score: {metrics['overall_consistency']:.1f}%")
        print(f"Total Terms Analyzed: {metrics['total_terms']}")
        print(f"Average Unique Translations: {metrics['avg_unique_translations']:.2f}")

        # Print top 5 most inconsistent terms
        print("\nTop 5 Most Inconsistent Terms:")
        inconsistent_terms = sorted(
            metrics["per_term_metrics"].items(), key=lambda x: x[1]["consistency_score"]
        )[:5]

        for term, term_metrics in inconsistent_terms:
            print(f"\n{term}:")
            print(f"  Consistency Score: {term_metrics['consistency_score']:.1f}%")
            print(f"  Unique Translations: {term_metrics['unique_translations']}")
            print("  Translation Distribution:")
            for trans, count in term_metrics["translations"].items():
                print(f"    - {trans}: {count}")


def main(folder_path):
    try:
        # Read ground truth file
        gt_path = os.path.join(folder_path, "target_gt.csv")
        if not os.path.exists(gt_path):
            raise FileNotFoundError("Ground truth file 'target_gt.csv' not found")

        metrics_dict = {}

        # Get all CSV files in the folder
        csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

        # Process each file
        for file in csv_files:
            if file == "target_gt.csv":
                continue

            file_path = os.path.join(folder_path, file)
            method_name = file.replace(".csv", "").replace("_", " ").title()

            print(f"\nProcessing {method_name}...")
            df = pd.read_csv(file_path)
            metrics_dict[method_name] = analyze_translations(df)

        # Also analyze ground truth
        gt_df = pd.read_csv(gt_path)
        metrics_dict["Ground Truth"] = analyze_translations(gt_df)

        # Create visualization
        output_file = os.path.join(folder_path, "translation_comparison.png")
        plot_comparison(metrics_dict, output_file)

        # Print detailed metrics
        print_detailed_metrics(metrics_dict)

        print(f"\nVisualization saved as '{output_file}'")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    import sys

    import numpy as np

    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    main(folder_path)
