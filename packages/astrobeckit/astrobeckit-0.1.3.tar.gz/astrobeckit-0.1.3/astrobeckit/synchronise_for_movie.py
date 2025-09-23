## Python script that syncs filenames for splash movies using the log files

import argparse
import os

# Main function
def main():
    parser = argparse.ArgumentParser(description="Process three inputs.")
    parser.add_argument('--folders_file', required=True, help="Filename for list of folders")
    parser.add_argument('--prefix', default='disc', help="Prefix for simulation files (default: 'disc')")
    parser.add_argument('--end', default='minimum', help="When to stop the movie (default: 'minimum')")

    args = parser.parse_args()

    # Set the folders and prefix
    folders = read_array_from_file(args.folders_file)
    prefix = args.prefix
    minimum_only = True if args.end == 'minimum' else False

    # Make necessary arrays
    ll = len(folders)

    dt_max = 0.
    num_logs = []
    for k, folder in enumerate(folders):
        # How many log files are in this folder?
        num_logs.append(count_files(folder,prefix,'.log'))

        # For each file, read it in and look for the line "dtmax = " which has been reprinted from the .in file
        for i in range(num_logs[k]):
            j = i + 1
            filename = '/' + prefix + f'{j:02}.log'
            # Read in the file, return the dt line
            dt_read = extract_value_between_equals_and_bang(folder + filename,'               dtmax =')

            # Now, always pick the biggest until we have finished
            if (dt_read > dt_max): dt_max = dt_read

    collated_filenames = []

    for k, folder in enumerate(folders):
        # With the largest dt_max, now look for which files correspond to this based on their time
        filenames = []
        for i in range(num_logs[k]):
            j = i + 1
            filename = '/' + prefix + f'{j:02}.log'
            matches = extract_all_times_and_discs(folder + filename,prefix)
            # Now check if the number corresponds to dt_max
            # If so, add it to the filenames
            for time_value, disc_value in matches:
                if (time_value % dt_max == 0.):
                    filenames.append(folder + '/' + prefix + '_' + str(disc_value).zfill(5))

        # Now, check if there was a moddump or not - if moddump, we need to add the zeroth file in
        no_moddump = line_exists_in_file(folder + '/' + prefix + '01.log', ' ---> DELETING temporary dump file ' + prefix + '_00000.tmp <---')
        if (no_moddump == False): filenames.insert(0,folder + '/' + prefix + '_00000')

        collated_filenames.append(filenames)

    # Now print to a file
    filename = 'splash.filenames'

    # If you only want the minimum number of files for completeness
    if (minimum_only):
        min_lengths = min([len(sublist) for sublist in collated_filenames])
        for k, folder in enumerate(folders):
            collated_filenames[k] = collated_filenames[k][0:min_lengths]
        write_column_major(collated_filenames, filename)
    # else, we want to repeat the last value to pad the lists
    else:
        max_lengths = max([len(sublist) for sublist in collated_filenames])
        for k, folder in enumerate(folders):
            last_item = collated_filenames[k][-1]
            last_index = len(collated_filenames[k]) - 1
            for i in range(last_index,max_lengths):
                collated_filenames[k].append(last_item)
        write_column_major(collated_filenames, filename)

# Function to read the list of filenames
def read_array_from_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Function to count how many files are in the directory
def count_files(folder_path, prefix, suffix):
    count = 0
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path) and filename.startswith(prefix) and filename.endswith(suffix):
            count += 1
    return count

# Function to read a particular line in the log file
def get_line_starting_with(file_path, start_text):
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith(start_text):
                return line.strip()  # Remove trailing newline and spaces
    return None  # Return None if no matching line is found

# Function to extract a number between the = and ! sign in the dt file
def extract_value_between_equals_and_bang(file_path, line_start):
    with open(file_path, 'r') as f:
        for line in f:
            if line.lstrip().startswith(line_start.strip()):
                # Split between '=' and '!' and strip spaces
                try:
                    between = line.split('=')[1].split('!')[0].strip()
                    return float(between)  # or return as string if preferred
                except IndexError:
                    pass  # line didn't have expected format
    return None

# Function to get the time and the file number
def extract_all_times_and_discs(file_path,prefix):
    results = []
    with open(file_path, 'r') as file:
        for line in file:
            if "TIME =" in line and prefix + "_" in line:
                try:
                    # Extract string after "TIME ="
                    time_part = line.split("TIME =")[1].split()[0].rstrip(':')
                    time_val = float(time_part)  # works for both normal and scientific notation

                    # Extract disc number string and convert to int
                    disc_part = line.split(prefix + "_")[1].split()[0]
                    disc_val = int(disc_part.lstrip('0') or '0')  # handles '00000' correctly

                    results.append((time_val, disc_val))
                except (IndexError, ValueError):
                    # Skip lines that don't match expected pattern
                    continue
    return results

# Function to check if a line exists or not
def line_exists_in_file(file_path, target_line):
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip() == target_line.strip():
                return True
    return False

# And a function to write to the output file
def write_column_major(array, file_path):
    # Transpose using zip
    with open(file_path, 'w') as f:
        for col in zip(*array):
            for item in col:
                f.write(f"{item}\n")

if __name__ == "__main__":
    main()
    print('Filenames printed to splash.filenames')
