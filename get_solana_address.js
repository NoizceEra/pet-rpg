const { Keypair } = require('@solana/web3.js');
const bs58 = require('bs58');
const fs = require('fs');

const secretKey = JSON.parse(fs.readFileSync('moltwars-wallet.json', 'utf8'));
const wallet = Keypair.fromSecretKey(new Uint8Array(secretKey));
console.log(wallet.publicKey.toBase58());
