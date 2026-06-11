import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests

        # Історія повідомлень:
        # ключ — user_id
        # значення — deque з часом відправлених повідомлень
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Видаляє старі повідомлення користувача,
        які вже вийшли за межі поточного часового вікна.
        """

        if user_id not in self.user_requests:
            return

        requests = self.user_requests[user_id]

        # Видаляємо всі повідомлення, які старші за window_size секунд
        while requests and current_time - requests[0] >= self.window_size:
            requests.popleft()

        # Якщо після очищення повідомлень не залишилось,
        # видаляємо користувача зі словника
        if not requests:
            del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може користувач відправити повідомлення зараз.
        """

        current_time = time.time()

        # Спочатку очищаємо старі записи
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає в історії — це його перше повідомлення
        if user_id not in self.user_requests:
            return True

        # Якщо кількість повідомлень менша за ліміт — можна відправляти
        return len(self.user_requests[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення користувача,
        якщо йому дозволено його відправити.
        """

        current_time = time.time()

        # Очищаємо старі повідомлення
        self._cleanup_window(user_id, current_time)

        # Перевіряємо, чи можна відправити повідомлення
        if not self.can_send_message(user_id):
            return False

        # Якщо користувача ще немає в словнику — створюємо deque
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        # Записуємо час нового повідомлення
        self.user_requests[user_id].append(current_time)

        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Повертає час очікування в секундах,
        поки користувач зможе відправити наступне повідомлення.
        """

        current_time = time.time()

        # Очищаємо старі повідомлення
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає — він може писати одразу
        if user_id not in self.user_requests:
            return 0.0

        requests = self.user_requests[user_id]

        # Якщо ліміт ще не досягнуто — чекати не потрібно
        if len(requests) < self.max_requests:
            return 0.0

        # Найстаріше повідомлення у вікні
        oldest_request_time = requests[0]

        # Коли воно вийде за межі вікна
        next_allowed_time = oldest_request_time + self.window_size

        # Скільки ще чекати
        wait_time = next_allowed_time - current_time

        return max(0.0, wait_time)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів
    print("\n=== Симуляція потоку повідомлень ===")

    for message_id in range(1, 11):
        # Симулюємо різних користувачів: ID від 1 до 5
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Випадкова затримка від 0.1 до 1.0 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки частина вікна очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")

    for message_id in range(11, 21):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()