def strip_none(arr):
    start = 0
    end = len(arr)

    # сдвигаем начало, пока элементы None
    while start < end and arr[start] is None:
        start += 1

    # сдвигаем конец, пока элементы None
    while end > start and arr[end - 1] is None:
        end -= 1

    return arr[start:end]