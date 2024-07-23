import asyncio
import aiohttp
import time
import logging
from config_data import CFG

API_URL = F'https://api.telegram.org/bot{CFG.TOKEN}/sendMessage'
CHAT_ID = '1038468423'

# Настройка логирования
logging.basicConfig(filename='stress_test.log', level=logging.INFO, format='%(asctime)s - %(message)s')

async def send_message(session, message, index):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    start_time = time.time()
    try:
        async with session.post(API_URL, data=payload) as response:
            end_time = time.time()
            elapsed_time = end_time - start_time
            response_text = await response.text()
            logging.info(f"Request {index}: Status {response.status}, Time {elapsed_time:.2f}s, Response {response_text}")
            return response.status, elapsed_time, response_text
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.error(f"Request {index}: Error {str(e)}, Time {elapsed_time:.2f}s")
        return None, elapsed_time, str(e)

async def stress_test(number_of_requests, delay):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(number_of_requests):
            task = asyncio.create_task(send_message(session, f"Test message {i}", i))
            tasks.append(task)
            await asyncio.sleep(delay)  # Добавляем задержку между запросами

        results = await asyncio.gather(*tasks)
        return results

if __name__ == '__main__':
    start_time = time.time()
    number_of_requests = 1000  # Количество запросов
    delay = 0.01  # Задержка между запросами в секундах

    results = asyncio.run(stress_test(number_of_requests, delay))
    end_time = time.time()

    # Выводим результаты
    total_time = end_time - start_time
    successful_requests = sum(1 for status, _, _ in results if status == 200)
    failed_requests = sum(1 for status, _, _ in results if status is None)
    avg_response_time = sum(elapsed for _, elapsed, _ in results) / len(results)

    print(f"Stress test completed in {total_time:.2f} seconds")
    print(f"Total requests: {number_of_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Average response time: {avg_response_time:.2f} seconds")

    # Записываем итоговую информацию в лог
    logging.info(f"Stress test completed in {total_time:.2f} seconds")
    logging.info(f"Total requests: {number_of_requests}")
    logging.info(f"Successful requests: {successful_requests}")
    logging.info(f"Failed requests: {failed_requests}")
    logging.info(f"Average response time: {avg_response_time:.2f} seconds")
