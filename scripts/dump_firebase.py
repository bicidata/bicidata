import json
from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Dict, Any, Callable, Tuple

from tqdm import tqdm
from google.cloud import firestore

data_folder = Path("/media/data/git/bicidata/data/snapshots_firebase").resolve()
data_folder.mkdir(parents=True, exist_ok=True)


# Add a new document
db = firestore.Client(project="eternal-cycling-325717")


# Download the contents of a given collection by batches,
# this enables the download process, it you try to download directly
# you take a memory heap:
def get_docs_by_batches(
        collection_reference: firestore.CollectionReference,
        batch_size: int = 100,
) -> Iterable[firestore.DocumentSnapshot]:

    # Get the first batch:
    first_batch = collection_reference.limit(batch_size)

    # Get all the documents in the batch, this downloads the whole batch:
    for doc in first_batch.stream():
        yield doc

    while True:
        ii = 0
        second_batch = (
            collection_reference
            .start_after(doc)
            .limit(batch_size)
        )

        # Get all the documents in the batch, this downloads the whole batch:
        for ii, doc in enumerate(second_batch.stream()):
            yield doc

        # Check if this batch was the last one, aka it has fewer docs than the batch size:
        if ii < batch_size - 1:
            break


def save(
        d: Dict[str, Any],
        file: Path,
):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(d))


def get(
        doc: firestore.DocumentSnapshot,
) -> Dict[str, Any]:
    return doc.to_dict()


def delete(
        doc: firestore.DocumentSnapshot
) -> bool:
    doc.reference.delete()
    return True


def apply_all_collections(
        func: Callable[[firestore.DocumentSnapshot], Any],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        progress_bars: Optional[bool] = False
) -> Iterable[Tuple[str, Any]]:
    """
    Download all the documents from all Collection objects:
    """
    start_date = start_date or date.fromisoformat("2021-09-12")
    end_date = end_date or date.today()
    # Iterate over each collection:
    all_collections = tqdm(db.collections(), desc="Collections", disable=not progress_bars)
    collection: firestore.CollectionReference
    for collection in all_collections:
        _, day = str(collection.id).split("_")
        all_collections.set_postfix({"day": day})
        that_date = date.fromisoformat(day)

        if start_date <= that_date < end_date:
            # day_folder = data_folder / day
            # day_folder.mkdir(exist_ok=True)

            # Iterate over each document in the collection using a batch iterator:
            for doc in tqdm(get_docs_by_batches(collection), total=1440, desc="Documents", disable=not progress_bars):
                yield day, func(doc)


if __name__ == '__main__':
    all_collections = apply_all_collections(
        get,
        start_date=date.fromisoformat("2022-05-03"),
        end_date=date.today(),
        progress_bars=True,
    )
    for day, j in all_collections:
        save(j, data_folder / day / f"{j.get('last_updated')}.json")

