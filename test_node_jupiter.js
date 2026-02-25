const axios = require('axios');
const https = require('https');

async function test() {
  const ip = '18.238.136.70';
  const url = `https://${ip}/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=5yaso9QHcqCmD7xegZvgRqa8J9RxjX2RtmK16frKpump&amount=100000000&slippageBps=50`;
  
  try {
    const response = await axios.get(url, {
      headers: { 'Host': 'api.jup.ag' },
      httpsAgent: new https.Agent({ rejectUnauthorized: false })
    });
    console.log(`Status: ${response.status}`);
    console.log(JSON.stringify(response.data));
  } catch (error) {
    console.error(`Error: ${error.message}`);
    if (error.response) {
      console.error(`Response data: ${JSON.stringify(error.response.data)}`);
    }
  }
}

test();
