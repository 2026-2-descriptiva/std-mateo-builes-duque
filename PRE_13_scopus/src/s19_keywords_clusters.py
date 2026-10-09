from pathlib import Path

from s10_countries_clusters import make_communities_report

SUBMISSION_DIRECTORY = Path(__file__).resolve().parent.parent / "submission"
MATRIX_FILE = SUBMISSION_DIRECTORY / "keywords_cooc_matrix.csv"
CLUSTERS_FILE = SUBMISSION_DIRECTORY / "keywords_clusters.txt"


def s19_keywords_clusters():
    make_communities_report(input_file=MATRIX_FILE, output_file=CLUSTERS_FILE)


if __name__ == "__main__":
    s19_keywords_clusters()
