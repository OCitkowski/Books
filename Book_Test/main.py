"""
main.py — точка входу Book Pipeline

Використання:
  python main.py --step all
  python main.py --step summarize
  python main.py --step bible
  python main.py --step skeleton
  python main.py --step bible skeleton
"""

import argparse
import logging
import sys

from config import PATHS

# ── Логування ────────────────────────────────────────────────
def setup_logging():
    log_file = PATHS["log"]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

# ── Кроки ────────────────────────────────────────────────────
def step_summarize():
    from flows.chunker import load_text, split_into_chunks
    from flows.summarizer import analyze_chunks
    logger = logging.getLogger("summarize")
    logger.info("=== КРОК: summarize ===")
    text = load_text()
    chunks = split_into_chunks(text)
    logger.info(f"Чанків: {len(chunks)}")
    analyze_chunks(chunks)
    logger.info("=== summarize завершено ===")


def step_bible():
    from flows.build_bible import build_bible
    logger = logging.getLogger("bible")
    logger.info("=== КРОК: bible ===")
    if not PATHS["summaries"].exists():
        logger.error("summaries.json не знайдено. Спочатку: --step summarize")
        sys.exit(1)
    build_bible()
    logger.info("=== bible завершено ===")


def step_skeleton():
    from flows.build_skeleton import build_skeleton
    logger = logging.getLogger("skeleton")
    logger.info("=== КРОК: skeleton ===")
    if not PATHS["summaries"].exists():
        logger.error("summaries.json не знайдено. Спочатку: --step summarize")
        sys.exit(1)
    build_skeleton()
    logger.info("=== skeleton завершено ===")


# ── CLI ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Book Pipeline")
    parser.add_argument(
        "--step",
        nargs="+",
        choices=["summarize", "bible", "skeleton", "all"],
        default=["all"],
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("main")
    logger.info(f"=== Book Pipeline START | steps: {args.step} ===")

    steps = ["summarize", "bible", "skeleton"] if "all" in args.step else args.step
    for step in steps:
        {"summarize": step_summarize, "bible": step_bible, "skeleton": step_skeleton}[step]()

    logger.info("=== Book Pipeline DONE ===")


if __name__ == "__main__":
    main()
