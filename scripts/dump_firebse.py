import json
from datetime import date
from pathlib import Path
from typing import Iterable, Generator

from tqdm import tqdm
from google.cloud import firestore

data_folder = Path("../data/snapshots_firebase").resolve()
data_folder.mkdir(parents=True, exist_ok=True)


# Add a new document
db = firestore.Client(project="eternal-cycling-325717")

start_date = date.fromisoformat("2021-09-28")
current_date = date.today()


# Download the contents of a given collection by batches,
# this enables the download process, it you try to download directly
# you take a memory heap:
def get_docs_by_batches(
        collection_reference: firestore.CollectionReference,
        batch_size: int = 100,
) -> Iterable[firestore.CollectionReference]:

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

        # Check if this batch was the last one, aka it has less docs than the batch size:
        if ii < batch_size - 1:
            break


"""
Download all the documents from all Collection objects:
"""
# Iterate over each collection:
all_collections = tqdm(db.collections(), desc="Collections")
collection: firestore.CollectionReference
for collection in all_collections:
    _, day = str(collection.id).split("_")
    all_collections.set_postfix({"day": day})
    that_date = date.fromisoformat(day)

    if start_date <= that_date < current_date:
        day_folder = data_folder / day
        day_folder.mkdir(exist_ok=True)

        # Iterate over each document in the collection using a batch iterator:
        for doc in tqdm(get_docs_by_batches(collection), total=1440, desc="Documents"):

            file = day_folder / f"{doc.id}.json"
            file.write_text(json.dumps(doc.to_dict()))




