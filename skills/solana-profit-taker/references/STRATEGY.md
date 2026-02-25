# The Vulture Strategy

The Vulture Engine follows a specific mathematical framework for surviving high-volatility meme-coin environments.

## 1. The Initial Strike (1.3x)
The engine targets a quick 30% gain (1.3x) for the bulk of the position. This recovers the initial investment plus a small buffer for gas and slippage.

## 2. The 80/20 Split
By selling 80% and keeping 20% (the "Moonbag"), the trade becomes effectively "risk-free." 
- If the token goes to zero, the trade is still profitable.
- If the token goes to 100x, the remaining 20% captures life-changing upside.

## 3. Trailing Profit (The "Claw")
Instead of selling at a fixed target, the engine allows the token to "run." 
- It tracks the `peak_roi`.
- If the token hits 2.0x and then drops to 1.8x (10% drop), it triggers the exit.
- This captures the "meat" of a pump without being shaken out by minor candles.

## 4. Volume Decay (The "Ghost" Filter)
Meme-coins die when attention moves elsewhere. 
- If 1-hour volume drops below $1,000, the engine assumes the project is "dead."
- It clears the position immediately to free up SOL for the next runner.
