const functions = require("firebase-functions");

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
exports.helloWorld = functions.region('europe-west1').https.onRequest((request, response) => {
  functions.logger.info("Hello logs!", {structuredData: true});
  response.send("Hello from Firebase!");
});

exports.scheduledFunction = functions.region('europe-west1').pubsub.schedule('every minute').onRun((context) => {
  functions.logger.info('This will be run every minute!', {structuredData: true});
  return null;
});
