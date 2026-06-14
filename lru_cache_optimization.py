import random
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        # Переносимо ключ у кінець, бо він щойно був використаний
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Якщо ключ вже є, оновлюємо його і переносимо в кінець
            self.cache.move_to_end(key)

        self.cache[key] = value

        # Якщо кеш переповнений, видаляємо найстаріший елемент
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# Глобальний кеш ємністю 1000
cache = LRUCache(1000)


def range_sum_no_cache(array, left, right):
    """
    Обчислення суми без кешування.
    Кожного разу рахуємо суму заново.
    """
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    """
    Оновлення елемента без кешування.
    """
    array[index] = value


def range_sum_with_cache(array, left, right):
    """
    Обчислення суми з використанням LRU-кешу.

    Ключем кешу є пара (left, right).
    Якщо така сума вже була порахована раніше,
    беремо її з кешу.
    """
    key = (left, right)

    cached_result = cache.get(key)

    if cached_result != -1:
        return cached_result

    result = sum(array[left:right + 1])
    cache.put(key, result)

    return result


def update_with_cache(array, index, value):
    """
    Оновлення елемента масиву.

    Після оновлення треба видалити з кешу всі діапазони,
    які містять змінений індекс.
    """
    array[index] = value

    keys_to_delete = []

    # Лінійно проходимо по всіх ключах кешу
    for left, right in cache.cache.keys():
        if left <= index <= right:
            keys_to_delete.append((left, right))

    # Видаляємо неактуальні діапазони
    for key in keys_to_delete:
        del cache.cache[key]


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]

    queries = []

    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)

            queries.append(("Range", left, right))

    return queries


def execute_queries_no_cache(array, queries):
    """
    Виконує всі запити без кешу.
    """
    results = []

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            result = range_sum_no_cache(array, left, right)
            results.append(result)

        elif query[0] == "Update":
            _, index, value = query
            update_no_cache(array, index, value)

    return results


def execute_queries_with_cache(array, queries):
    """
    Виконує всі запити з LRU-кешем.
    """
    results = []

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            result = range_sum_with_cache(array, left, right)
            results.append(result)

        elif query[0] == "Update":
            _, index, value = query
            update_with_cache(array, index, value)

    return results


def main():
    random.seed(42)

    n = 100_000
    q = 50_000

    original_array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    # Для чесного порівняння обидва варіанти мають працювати
    # з однаковим початковим масивом
    array_no_cache = original_array.copy()
    array_with_cache = original_array.copy()

    start = time.perf_counter()
    results_no_cache = execute_queries_no_cache(array_no_cache, queries)
    time_no_cache = time.perf_counter() - start

    # Очищаємо кеш перед тестом
    global cache
    cache = LRUCache(1000)

    start = time.perf_counter()
    results_with_cache = execute_queries_with_cache(array_with_cache, queries)
    time_with_cache = time.perf_counter() - start

    # Перевірка правильності
    if results_no_cache == results_with_cache:
        print("Результати однакові: кеш працює правильно.")
    else:
        print("Помилка: результати з кешем і без кешу відрізняються.")

    speedup = time_no_cache / time_with_cache

    print()
    print(f"Без кешу : {time_no_cache:6.2f} c")
    print(f"LRU-кеш  : {time_with_cache:6.2f} c  (прискорення ×{speedup:.1f})")


if __name__ == "__main__":
    main()