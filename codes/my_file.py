def tinh_tong(list_so):
  """Tính tổng các phần tử trong list."""

  if not list_so:
    raise ValueError("List is empty")

  tong = 0
  for i in list_so:
    tong += i

  return tong


def main():
  """Hàm main."""

  list_so = [1, 2, 3, 4, 5]
  print(tinh_tong(list_so))


if __name__ == "__main__":
  main()
