const fs = require('fs');
const { Keypair } = require('@solana/web3.js');
const bs58 = require('bs58');

// Load keypair
const keypairData = JSON.parse(fs.readFileSync('moltwars-wallet.json'));
const keypair = Keypair.fromSecretKey(new Uint8Array(keypairData));

console.log('=== MOLT WARS WALLET EXPORT ===');
console.log('Public Key:', keypair.publicKey.toBase58());
console.log('Private Key (Base58):', bs58.encode(keypair.secretKey));
console.log('Private Key (Array):', JSON.stringify(Array.from(keypair.secretKey)));
console.log('\n=== FOR PHANTOM WALLET IMPORT ===');
console.log('Use this Base58 private key:', bs58.encode(keypair.secretKey));