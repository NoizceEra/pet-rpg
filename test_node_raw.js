const https = require('https');

const ip = '18.238.136.70';
const options = {
  hostname: ip,
  port: 443,
  path: '/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=5yaso9QHcqCmD7xegZvgRqa8J9RxjX2RtmK16frKpump&amount=100000000&slippageBps=50',
  method: 'GET',
  headers: {
    'Host': 'api.jup.ag',
    'User-Agent': 'Mozilla/5.0'
  },
  rejectUnauthorized: false
};

const req = https.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => { console.log(data); });
});

req.on('error', (e) => {
  console.error(`Error: ${e.message}`);
});

req.end();
