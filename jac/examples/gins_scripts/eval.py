import os
import random
import subprocess

num_samples = 1000
start_value = 99
end_avg = 105

# Initialize storage for sensor data
sensor_data = []

# Calculate the amount to increment each value to reach the desired average
increment = (end_avg - start_value) / num_samples

current_value = start_value
for _ in range(num_samples):
    # Add some noise to make the data more realistic
    noise = random.uniform(-0.7, 0.5)
    sensor_value = current_value + noise
    sensor_data.append(sensor_value)

    # Update current value towards the end_avg
    current_value += increment

current_directory = os.path.dirname(os.path.abspath(__file__))
program = os.path.join(current_directory, 'hot_path.jac')

for i, input in enumerate(sensor_data):
    try:
        # Use subprocess to pass input and capture output
        os.system(f'jac run {program} --gins --input {input}')

        temp_file = os.path.join(current_directory, 'preds/tmp_cfg.pkl')
        new_file = os.path.join(current_directory, f'preds/cfg{i}.pkl')

        if os.path.exists(temp_file):
            os.rename(temp_file, new_file)

        # Print or process the output from the jac program
        # output = process.stdout
        # print(f"Output: {output}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
    except KeyboardInterrupt:
        print("Process interrupted by user")
        break
