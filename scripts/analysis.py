import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def add_protein_abbreviations(df, filename):
    protein_dict = {
        "Alcohol_dehydrogenase": "ADH",
        "Beta_2_microglobulin": "B2M",
        "Catalase": "CAT",
        "Cytochrome_c": "CYTC",
        "Ferritin": "FT",
        "FtsZ": "FtsZ",
        "Green_fluorescent_protein": "GFP",
        "Hemoglobin": "HB",
        "Insulin": "INS",
        "Lactase": "LAC",
        "Myosin": "MYO",
        "p53": "p53",
        "Peripherin": "PRPH",
        "Ubiquitin": "UB",
        "UGGT": "UGGT"
    }

    # Add abbreviations column and check the first 5 entries
    df["Abbreviation"] = df["Topic"].map(protein_dict)
    # print(df.head())

    # Reorder columns: place "Abbreviation" as the second column
    cols = ["Topic", "Abbreviation"] + [col for col in df.columns if col not in ["Topic", "Abbreviation"]]
    df = df[cols]

    # Save the updated CSV
    df.to_csv(filename, index=False)
    print("Abbreviation column added to 'evaluation.csv'")


def plot_boxplots(df, save=False, k_chunks_filter="all"):
    """Generate boxplots for the dataset with an optional k_chunks filter.

    Args:
        df (pd.DataFrame): The dataframe containing the data.
        save (bool): Whether to save the plot or just display it.
        k_chunks_filter (str): Filter by k_chunks value (e.g., "50", "100", or "all").
    """
    plt.figure(figsize=(5, 5))

    # First boxplot (GEval 4o score)
    plt.subplot(1, 1, 1)
    sns.boxplot(x=df["Model"], y=df["GEval 4o score"], hue=df["k_chunks"], fill=False)
    plt.title(f"GEval GPT-4o score")
    plt.ylabel("GEval score")

    # Adjust layout
    plt.tight_layout()

    if save:
        filename = f"boxplots_k{str(k_chunks_filter)}.png"
        plt.savefig(filename)
        print(f"Boxplots saved as '{filename}'")
    else:
        plt.show()  # Show the plot


def main():
    parser = argparse.ArgumentParser(description="Data analysis script.")

    # Make --boxplots accept an optional value: save
    parser.add_argument("--boxplots", nargs="?", const="show", choices=["show", "save"],
                        help="Generate boxplots (optionally save them)")
    parser.add_argument("--abbreviation", action="store_true", help="Generate protein abbreviations")
    parser.add_argument("--df_filename", help="The name (with suffix) of the .csv file to analyze")

    args = parser.parse_args()

    df = pd.read_csv(args.df_filename)

    if args.boxplots:
        save = args.boxplots == "save"  # If "save" is given, save the plot
        plot_boxplots(df, save)

    if args.abbreviation:
        add_protein_abbreviations(df, args.df_filename)


if __name__ == "__main__":
    main()
