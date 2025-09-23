import starbound.cli as cli


def test_csv_flip_vertical():
    # 2x3 grid with values row-major from bottom-left origin arr (0..5)
    # arr layout by y from bottom (y=0..2):
    # y=0: 0 1
    # y=1: 2 3
    # y=2: 4 5
    arr = [0,1, 2,3, 4,5]
    csv = cli._csv_from_array(arr, 2, 3)
    lines = csv.split('\n')
    # Expect top row first: 4,5 then 2,3 then 0,1
    assert lines == ['4,5', '2,3', '0,1']
