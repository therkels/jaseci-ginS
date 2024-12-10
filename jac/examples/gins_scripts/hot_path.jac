import:py os;
import:py random;
import:py sys;

with entry {
    a: int = 0;
    b: int = 0;
    c: int = 0;
    input_val: float = 0.0;
    test_val: float = 0.0;
    count: int = 100;
    accum_sum: float = 0.0;
    changing_average: float = 0;
    change_reduction_arr: list = [];
    input_val: float = float(sys.argv[-1]);
    print("Input value: ", input_val);

    # count = count + 1;
    accum_sum = accum_sum + input_val;
    changing_average = accum_sum / count;
    print("Changing average: ", changing_average / 100);
    if (changing_average) / 100 < 0.0001 {
        test_val: int = test_val + 100.0;
        print('here');
    } else {
        counter = 0;
        for i in range(count) {

            counter = counter + 1;
            test_val = test_val + 10.0;
        }
        print("for Count: ", count);    
    }
    count = 0;
    print("Test value: ", test_val);
    while test_val >= 0 {
        count = count + 1;
        reduce: float = random.uniform(5.0, 10.0);
        test_val -= reduce;

        # change_reduction_arr.append(test_val);
    }
    print("while Count: ", count);
}
