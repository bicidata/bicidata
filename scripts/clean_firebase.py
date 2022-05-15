from datetime import date

from scripts.dump_firebase import delete, apply_all_collections


if __name__ == '__main__':
    all_collections = apply_all_collections(
        delete,
        start_date=date.fromisoformat("2021-09-12"),
        end_date=date.fromisoformat("2021-09-25"),
        progress_bars=True,
    )
    for day, _ in all_collections:
        pass
