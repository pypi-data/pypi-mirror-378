import subprocess
import re
import os
import glob
import argparse

# Main function
def main():
   parser = argparse.ArgumentParser(description="Process three inputs.")
   parser.add_argument('--search_string', default=None, help="String pattern for folders")
   parser.add_argument('--dry_run', default=False, help="List folders and whether to submit instead of submitting")
   parser.add_argument('--n_sub', default=5, help="Number of jobs to resubmit")

   args = parser.parse_args()

   # Set the folders and prefix
   folder_string = args.search_string
   dry_run = args.dry_run
   n_sub = args.n_sub
   script_path = os.path.expanduser("~/runs/multi_run.sh")

   ### check the storage first
   result = subprocess.run(
          ['mmlsquota', '--block-size', 'auto'],
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          text=True,
          check=True
          )


   # prefill this for safety
   enough_space = False

   # Process each line of the output
   for line in result.stdout.splitlines():
      if line.startswith("gpfs01"):
         # Extract the first number using regex
         match = re.search(r'\b(\d+(?:\.\d+)?)([KMGTP]?)\b', line)
         if match:
            number = float(match.group(1))
            unit = match.group(2)

            if (unit == 'G' and number <= 999.9):
               enough_space = True
            if (unit == 'T' and number <= 1.8):
               enough_space = True

   # now find out where the files are (this script is designed to be run in the folder above the simulation folders)
   current_dir = os.getcwd()
   if (folder_string):
      folders = [name for name in os.listdir(current_dir)
              if os.path.isdir(os.path.join(current_dir, name)) and folder_string in name]
   else:
      folders = [name for name in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, name))]

   for current_folder in folders:
      # change to the folder in question
      os.chdir(current_folder)

      # establish the final time in the simulation
      for filename in glob.glob("*.in"):
         with open(filename, "r") as f:
            for line in f:
               if "tmax" in line:
                  match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
                  if match:
                     tmax = float(match.group())
                  break
      file_prefix = filename.split(".in")[0]

      # find the last log file
      ready_to_rerun = False
      logfiles = glob.glob(file_prefix + "??.log")
      if logfiles:
         last_log = sorted(logfiles)[-1]

         # now, find the last time that has been output in the log file (this is slightly faster than reading the evs)
         time_pattern = re.compile(r"TIME\s*=\s*([-+]?\d*\.\d+(?:[eE][-+]?\d+)?)")
         last_time = None

         with open(last_log,"r") as file:
            for line in file:
               match = time_pattern.search(line)
               if (match):
                  last_time = float(match.group(1)) # converts it to a float
         if (last_time and last_time < tmax): ready_to_rerun = True
      else:
         #print(current_folder,': No log files found')
         ready_to_rerun = True

      # now, check if something is running already
      jobs_already_queued = False
      job_name_pattern = re.compile(r"#SBATCH\s+--job-name=(\S+)")
      with open('run.sbatch',"r") as file:
         for line in file:
            match = job_name_pattern.search(line)
            if match: job_name = match.group(1)

      # identify which jobs are running with that name
      result = subprocess.run(
               ["squeue", "--name", job_name, "--format", "%T", "-h"],  # The `-h` option hides the header
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               text=True,
               check=True
           )

      if (result.stdout.strip()):
         jobs_already_queued = True

      if (enough_space and ready_to_rerun and not jobs_already_queued):
         print('Resubmitting job: ',current_folder)
         if (not dry_run):
            subprocess.run(["bash", script_path, n_sub], check=True)
      else:
         if (dry_run):
            print('Not resubmitting: ',current_folder)

      # and change back up
      os.chdir('..')

if __name__ == "__main__":
    main()
