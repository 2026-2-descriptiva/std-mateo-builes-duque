from pathlib import Path

from s05_countries_frequency_report import make_frequency_report

SUBMISSION_DIRECTORY = Path(__file__).resolve().parent.parent / "submission"
FREQUENCY_REPORT_FILE = SUBMISSION_DIRECTORY / "keywords_frequency.csv"


def s16_keywords_frequency_report():
    make_frequency_report(
        column="keywords_clean",
        file_path=FREQUENCY_REPORT_FILE,
    )


if __name__ == "__main__":
    s16_keywords_frequency_report()
