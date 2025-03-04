# Multi-Currency-Seed-Finder
This Python script is an educational experiment designed to generate mnemonic seed phrases using the bitcoinlib library and check for associated wallet balances across Bitcoin, Litecoin, and Dogecoin networks. It uses multi-threading with ThreadPoolExecutor for concurrent processing and logs progress to local files (searched_seeds.json and live.txt).

# Features
Generates random mnemonic seed phrases.
Checks wallet balances for Bitcoin, Litecoin, and Dogecoin.
Processes seeds in batches with configurable concurrency settings.
Logs searched seeds and wallets with non-zero balances.
Designed to run on Google Colab with local file output.
# Purpose
This project was created for learning purposes to explore cryptocurrency wallet generation, multi-threading, and file I/O in Python. It serves as a portfolio piece to demonstrate coding skills and understanding of blockchain-related concepts.

# Usage
Requires bitcoinlib library (pip install bitcoinlib).
Adjust BATCH_SIZE and MAX_WORKERS for performance tuning.
Outputs results to live.txt and tracks progress in searched_seeds.json.
# Disclaimer
This is an educational tool and should not be used for malicious purposes, such as attempting to access or exploit existing wallets. It is intended purely for demonstration and learning. Use responsibly and ethically.

# Note
Originally designed for Google Colab; download output files manually after execution.
