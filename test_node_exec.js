const https = require('https');

const inputMint = "So11111111111111111111111111111111111111112";
const outputMint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
const amount = 100000000;
const ip = "172.64.32.59";

const options = {
  hostname: ip,
  port: 443,
  path: `/v6/quote?inputMint=${inputMint}&outputMint=${outputMint}&amount=${amount}&slippageBps=50`,
  method: 'GET',
  headers: {
    'Host': 'quote-api.jup.ag',
    'User-Agent': 'Mozilla/5.0'
  },
  rejectUnauthorized: false
};

const req = https.request(options, (res) => {
  console.log(`STATUS: ${res.statusCode}`);
  let data = '';
  res.on('data', (d) => {
    data += d;
  });
  res.on('end', () => {
    console.log(data);
  });
});

req.on('error', (e) => {
  console.error(`ERROR: ${e.message}`);
});

req.end();
