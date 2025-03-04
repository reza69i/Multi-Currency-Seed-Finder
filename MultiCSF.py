import time
import uuid
import json
import os
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
import logging
from concurrent.futures import ThreadPoolExecutor, wait
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
SEARCH_LOG_FILE = "searched_seeds.json"  # Local to Colab
OUTPUT_FILE = "live.txt"  # Local to Colab
BATCH_SIZE = 50  # Number of seeds to process in each batch
MAX_WORKERS = 5  # Number of concurrent workers

searched_seeds = set()
seed_count = 0
balance_count = 0
balance_lock = threading.Lock()  # Lock for thread-safe operations

def load_searched_seeds():
    global searched_seeds
    try:
        if os.path.exists(SEARCH_LOG_FILE):
            with open(SEARCH_LOG_FILE, "r") as f:
                data = json.load(f)
                searched_seeds.update(data if isinstance(data, list) else [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load searched seeds: {e}")
        searched_seeds = set()

def save_progress():
    try:
        with open(SEARCH_LOG_FILE, "w") as f:
            json.dump(list(searched_seeds), f)
        logger.info(f"Saved progress: {len(searched_seeds)} seeds")
    except Exception as e:
        logger.error(f"Failed to save progress: {e}")

def remove_db_file(db_file, max_attempts=3, delay=0.5):
    for attempt in range(max_attempts):
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
            return True
        except PermissionError as e:
            logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed to remove {db_file}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    logger.error(f"Failed to remove {db_file} after {max_attempts} attempts")
    return False

def check_balance(passphrase, network):
    wallet_name = str(uuid.uuid4())
    db_file = f'wallet_{wallet_name}.db'
    db_uri = f'sqlite:///{db_file}?check_same_thread=False'
    w = None
    try:
        witness_type = 'legacy' if network == 'dogecoin' else 'segwit'
        w = Wallet.create(
            wallet_name,
            keys=passphrase,
            network=network,
            witness_type=witness_type,
            db_uri=db_uri
        )
        w.get_key()
        balance = w.balance()
        return balance
    except Exception as e:
        logger.error(f"Error checking {network} wallet: {e}")
        return 0
    finally:
        if w is not None:
            try:
                w.close()
            except:
                pass
            del w
            import gc
            gc.collect()
        remove_db_file(db_file)

def check_seed(passphrase, current_seed_count):
    currencies = ['bitcoin', 'litecoin', 'dogecoin']
    for network in currencies:
        balance = check_balance(passphrase, network)
        logger.info(f"Checked {network} wallet for seed #{current_seed_count}: {passphrase} BALANCE: {balance}")
        if balance > 0:
            with balance_lock:
                global balance_count
                balance_count += 1
                with open(OUTPUT_FILE, 'a', encoding="utf8") as f:
                    f.write(f"Found {network} wallet for seed #{current_seed_count}: {passphrase} BALANCE: {balance}\n")
            logger.info(f"Found {network} wallet with balance for seed #{current_seed_count}: {passphrase} BALANCE: {balance}")

def seed_finder():
    global seed_count

    mnemonic = Mnemonic()
    load_searched_seeds()

    print("Starting multi-currency seed finder on Google Colab... (Press Ctrl+C to stop or interrupt the cell)")
    print("Checking: Bitcoin, Litecoin, Dogecoin")
    print("Note: Files will be saved locally. Download 'searched_seeds.json' and 'live.txt' manually when needed.")
    logger.info("Seed finder started")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        try:
            while True:
                futures = []
                for _ in range(BATCH_SIZE):
                    passphrase = mnemonic.generate()
                    if passphrase not in searched_seeds:
                        searched_seeds.add(passphrase)
                        seed_count += 1
                        future = executor.submit(check_seed, passphrase, seed_count)
                        futures.append(future)
                wait(futures)
                print(f"Seeds Checked: {seed_count} | Wallets with Balance: {balance_count}")
                save_progress()
        except KeyboardInterrupt:
            print("\nStopping seed finder...")
            print(f"Final Stats - Seeds Checked: {seed_count} | Wallets with Balance: {balance_count}")
            print("Download 'searched_seeds.json' and 'live.txt' now if needed!")
            logger.info("Seed finder stopped")

if __name__ == "__main__":
    seed_finder()
