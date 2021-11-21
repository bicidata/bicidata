// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require("firebase-functions");

// A requester module to consume API
const fetch = require('node-fetch');

// The Firebase Admin SDK to access Firestore.
const admin = require('firebase-admin');
admin.initializeApp();

let API_URL = "http://35.241.203.225";

// A function to serve the modified GBFS API:
exports.gbfs = functions
    // .region('europe-west1')  // TODO changing region brakes the firebase "rewrite" rule.
    .https
    .onRequest(async (request, response) => {
        let settings = { method: "Get" };
        let url = "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json";
        let response_gbfs = await fetch(url, settings);
        let json_gbfs = await response_gbfs.json();

        json_gbfs["ttl"] = -1;

        json_gbfs["data"]["en"]["feeds"].push({
            name: "station_status_snapshots",
            url: `${API_URL}/station_status/{timestamp}.json`
        })

        json_gbfs["data"]["en"]["feeds"].push({
            name: "snapshots_information",
            url: `${API_URL}/snapshots.json`
        })

        // functions.logger.info(json_gbfs, {structuredData: true});

        response.json(json_gbfs);
      }
    );

// A function to serve the GBFS snapshots:
exports.gbfsSnapshotInformation = functions
    .https
    .onRequest(async (request, response) => {
        functions.logger.info("Hello.", {structuredData: true});
        let date = "2021-09-13";
        let snapshot_id = `snapshots_${date}`;

        let list_snapshots = (await admin
            .firestore()
            .collection(snapshot_id)
            .listDocuments()).map(function (doc) {
                return doc.path;
        })


        let obj = {
            last_updated: Math.ceil(new Date().getTime()/1000),
            ttl: -1,
            data: {timestamps: list_snapshots}
        };
        response.json(obj);
      }
    );


// A function to capture the GBFS snapshots:
exports.gbfsSnapshot = functions
    // .region('europe-west1')
    .pubsub.schedule('every minute')
    .onRun(async (context) => {
         let settings = { method: "Get" };
         let url = "https://barcelona-sp.publicbikesystem.net/customer/ube/gbfs/v1/en/station_status";
         let response_gbfs = await fetch(url, settings);
         let json_gbfs = await response_gbfs.json();

         let timestamp = json_gbfs["last_updated"];
         let date = new Date(timestamp * 1000);
         let year = date.getFullYear().toString();
         let month = (date.getMonth() + 1).toString().padStart(2, "0");
         let day = date.getDate().toString().padStart(2, "0");

         json_gbfs["ttl"] = -1;

         // Push the new snapshot into Firestore using the Firebase Admin SDK.
         const writeResult = await admin.firestore()
             .collection(`snapshots_${year}-${month}-${day}`)
             .doc(timestamp.toString())
             .set(json_gbfs);

         functions.logger.info("Success writing snapshoot.", {structuredData: true});

         return null;
        }
    );
