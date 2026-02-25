const https = require('https');

const options = {
  hostname: '3.160.107.9', // IP for quote-api.jup.ag
  port: 443,
  path: '/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000',
  method: 'GET',
  headers: {
    'Host': 'quote-api.jup.ag',
    'User-Agent': 'Mozilla/5.0'
  },
  rejectUnauthorized: false // Skip cert check for IP
};

const req = https.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  res.on('data', (d) => {
    process.stdout.write(d);
  });
});

req.on('error', (e) => {
  console.error(`Error: ${e.message}`);
});

req.end();
