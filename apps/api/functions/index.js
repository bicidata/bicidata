// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require("firebase-functions");

// A requester module to consume API
const fetch = require('node-fetch');

// // The Firebase Admin SDK to access Firestore.
// const admin = require('firebase-admin');
// admin.initializeApp();

// A function to serve the modified GBFS API:
exports.gbfs = functions
    // .region('europe-west1')  // TODO changing region brakes the firebase "rewrite" rule.
    .https
    .onRequest(async (request, response) => {
        let settings = { method: "Get" };
        let url = "https://barcelona.publicbikesystem.net/ube/gbfs/v1/gbfs.json";
        let response_gbfs = await fetch(url, settings);
        let json_gbfs = await response_gbfs.json();

        // json_gbfs["data"]["en"]["feeds"].push({
        //     name: "snapshots_information",
        //     url: "http://35.241.203.225/snapshots.json"
        // })

        functions.logger.info(json_gbfs, {structuredData: true});

        response.json(json_gbfs);
      }
    );

// A function to serve the GBFS snapshots:
// TODO


// A function to capture the GBFS snapshots:
exports.scheduledFunction = functions
    // .region('europe-west1')
    .pubsub.schedule('every minute')
    .onRun((context) => {
  functions.logger.info('This will be run every minute!', {structuredData: true});
  return null;
});
