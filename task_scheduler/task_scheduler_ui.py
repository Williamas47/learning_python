import tkinter as tk
from tkinter import ttk
import time
import json
import os
import datetime

tasks_file_path = 'tasks.json'
task_time_delay_types = ['Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years']
task_time_option_types = ['Delay', 'Date and time']
task_month_options = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

screen = 0
root = tk.Tk()
root.title("Task Scheduler")
time_label = tk.Label(root, font=("Courier", 14))

def read_file_data(path):
  if(not os.path.exists(path)):
      with open(path, "w") as file:
        json.dump({}, file, indent=4)
      return

  with open(path, "r") as file:
    loaded_tasks = json.load(file)
    parsed_tasks = []
    for loaded_task in loaded_tasks:
      if (loaded_task['date'] and loaded_task['name']):
        parsed_tasks.append(loaded_task)
    return parsed_tasks

def save_data_on_file(data, path):
  existent_data = read_file_data(path)
  parsed_new_data = {
    **data,
    'date': data['date'].strftime('%Y-%m-%d %H:%M:%S')
  }
  updated_content = [*existent_data, parsed_new_data]
  with open(path, "w") as file:
    json.dump(updated_content, file, indent=4)

def get_days_amount(answer_type, answer_multiplier, delay_type):
  days_in_year = 365
  days_in_month = 30
  days_in_week = 7
  # If answer_type is in timedelta_non_supported_options
  if(answer_type.lower() != delay_type):
    answer_multiplier = int(answer_multiplier) * {
      'weeks': days_in_week,
      'months': days_in_month,
      'years': days_in_year
    }.get(answer_type.lower())
  return int(answer_multiplier)

def get_date_after_delay(delay_answers):
  today = datetime.datetime.now()
  timedelta_non_supported_options = ['weeks', 'months', 'years']
  delay_type =  'days' if delay_answers['delay_type'].lower() in timedelta_non_supported_options else delay_answers['delay_type'].lower()
  days_amount = get_days_amount(delay_answers['delay_type'], delay_answers['delay_multiplier'], delay_type)
  time_delta_qtd_arg = days_amount if delay_type == 'days' else int(delay_answers['delay_multiplier'])
  timedelta_args={delay_type: int(time_delta_qtd_arg)}
  timedelta = datetime.timedelta(**timedelta_args)
  date = today + timedelta
  parsed_date = datetime.datetime(int(date.year), int(date.month), int(date.day), int(date.hour), int(date.minute), int(date.second))
  return parsed_date

def get_tasks_remaining_time(file_data):
  now = datetime.datetime.now()
  data = ''
  biggest_name = None
  for task in file_data:
    task_parsed_date = datetime.datetime.strptime(task['date'], '%Y-%m-%d %H:%M:%S')
    task_remaining_time = task_parsed_date - now
    overdue = task_remaining_time < datetime.timedelta(0)
    task['remaining_time_to_alert'] = datetime.timedelta(0) if overdue else task_remaining_time
    if not biggest_name or len(task['name']) > len(biggest_name):
      biggest_name = task['name']
  ordered_tasks = sorted(file_data, key=lambda task: task['remaining_time_to_alert'])
  data += "\nTask Name" + " " * (len(biggest_name) - len("Task Name")) + ' ---------- ' + "Remaining Time" +'\n'
  for task in ordered_tasks:
    remaining_days = task['remaining_time_to_alert'].days
    remaining_hours, remainder = divmod(task['remaining_time_to_alert'].seconds, 3600)
    remaining_minutes, _ = divmod(remainder, 60)
    remaining_seconds =task['remaining_time_to_alert'].seconds % 60
    time_expired = remaining_days <= 0 and remaining_hours <= 0 and remaining_minutes <= 0 and remaining_seconds <= 0
    remaining_time = "Time Expired" if time_expired else f"{remaining_days}d {remaining_hours}h {remaining_minutes}m {remaining_seconds}s"
    name_spaces = len(biggest_name) - len(task['name'])
    print(task['name'], (str(name_spaces)))
    data += task['name']+" " * name_spaces + ' ---------- ' + remaining_time +'\n'
  return data

def handle_delay_answer():
    name = task_name.get()
    delay_type_value = delay_type.get()
    delay_quantity_value = delay_quantity.get()

    delay_answers = {
      'delay_type': delay_type_value,
      'delay_multiplier': delay_quantity_value
    }
    to_remind_date = get_date_after_delay(delay_answers)
    new_task = {
      'name': name,
      'date': to_remind_date
    }
    save_data_on_file(new_task, tasks_file_path)
    print("We will remind you about task: '"+name+"' in " +
      delay_answers['delay_multiplier'] + " " + delay_type_value + " ("+str(to_remind_date)+")"
    )
    handle_back()
    clear_delay_task_input_values()

def handle_date_time_answer():
    name = task_name.get()
    year = date_time_year.get()
    month = date_time_month.get()
    day = date_time_day.get()
    hour = date_time_minutes.get()
    minute = date_time_minutes.get()
    second = date_time_seconds.get()
    print(name, year, month, day, hour, minute, second)
    date_answers = {
      'year': year,
      'month': month,
      'day': day,

    }
    time_answers = {
      'hour': hour,
      'minute': minute,
      'second': second
    }

    full_date = datetime.datetime(int(date_answers['year']), task_month_options.index(date_answers['month']) + 1, int(date_answers['day']), int(time_answers['hour']), int(time_answers['minute']), int(time_answers['second']))
    to_remind_date = full_date
    new_task = {
      'name': name,
      'date': to_remind_date
    }

    save_data_on_file(new_task, tasks_file_path)
    print("We will remind you about task: '"+name+"' in " +
       str(to_remind_date)
    )
    handle_back()
    clear_date_time_task_input_values()

def validate_date_time_answer():
    name = task_name.get()
    year = date_time_year.get()
    month = date_time_month.get()
    day = date_time_day.get()
    hour = date_time_minutes.get()
    minute = date_time_minutes.get()
    second = date_time_seconds.get()
    if not name or not year or not month or not day or not hour or not minute or not second:
      error_message.config(text="Please fill all fields")
      error_message.grid(row=11, column=0, columnspan=2)
      return False
    return True

def validate_delay_answer():
    name = task_name.get()
    delay_type_value = delay_type.get()
    delay_quantity_value = delay_quantity.get()
    if not name or not delay_type_value or not delay_quantity_value:
      error_message.config(text="Please fill all fields")
      error_message.grid(row=8, column=0, columnspan=2)
      return False
    return True

def submit():
    schedule_type_value = schedule_type.get()
    error_message.config(text="")
    print('SUBMIT', schedule_type_value)
    if(schedule_type_value == 'Delay'):
      is_answer_valid = validate_delay_answer()
      print(is_answer_valid)
      if is_answer_valid:
        handle_delay_answer()
        # TODO show message, wait 5 secs, remove elements and go back to first screen

    elif(schedule_type_value == 'Date and time'):
      is_answer_valid = validate_date_time_answer()
      if is_answer_valid:
        handle_date_time_answer()
        # TODO show message, wait 5 secs, remove elements and go back to first screen


# Schedule task Delay type
delay_label = tk.Label(root, text="Delay type task: ")
delay_type_label = tk.Label(root, text="Select a delay type: ")
delay_type = ttk.Combobox(root, values=task_time_delay_types)
delay_quantity_label = tk.Label(root, text="Insert a delay quantity: ")
delay_quantity = tk.Entry(root)
delay_submit_button = tk.Button(root, text="Submit", command=lambda: submit())


def clear_delay_task_input_values():
  task_name.delete(0, tk.END)
  schedule_type.delete(0, tk.END)
  delay_type.delete(0, tk.END)
  delay_quantity.delete(0, tk.END)

def clear_delay_task_elements():
  delay_label.grid_remove()
  delay_type_label.grid_remove()
  delay_type.grid_remove()
  delay_quantity_label.grid_remove()
  delay_quantity.grid_remove()
  delay_submit_button.grid_remove()

def schedule_delay_task():
  clear_date_time_task_elements()
  delay_label.grid(row=4, column=0, columnspan=2)
  delay_type_label.grid(row=5, column=0)
  delay_type.grid(row=5, column=1)
  delay_quantity_label.grid(row=6, column=0)
  delay_quantity.grid(row=6, column=1)
  back_button.grid(row=7, column=0)
  delay_submit_button.grid(row=7, column=1)

# Schedule task Date and time type
date_time_label = tk.Label(root, text="Date and time task:")
date_time_year_label = tk.Label(root, text="Year: ")
date_time_year = tk.Entry(root)
date_time_month_label = tk.Label(root, text="Month: ")
date_time_month = ttk.Combobox(root, values=task_month_options)
date_time_day_label = tk.Label(root, text="Day: ")
date_time_day = tk.Entry(root)
date_time_minutes_label = tk.Label(root, text="Minutes: ")
date_time_minutes = tk.Entry(root)
date_time_seconds_label = tk.Label(root, text="Seconds: ")
date_time_seconds = tk.Entry(root)
date_time_submit_button = tk.Button(root, text="Submit", command=lambda: submit())


def clear_date_time_task_input_values():
  task_name.delete(0, tk.END)
  schedule_type.delete(0, tk.END)
  date_time_year.delete(0, tk.END)
  date_time_month.delete(0, tk.END)
  date_time_day.delete(0, tk.END)
  date_time_minutes.delete(0, tk.END)
  date_time_seconds.delete(0, tk.END)

def clear_date_time_task_elements():
  date_time_label.grid_remove()
  date_time_year_label.grid_remove()
  date_time_year.grid_remove()
  date_time_month_label.grid_remove()
  date_time_month.grid_remove()
  date_time_day_label.grid_remove()
  date_time_day.grid_remove()
  date_time_minutes_label.grid_remove()
  date_time_minutes.grid_remove()
  date_time_seconds_label.grid_remove()
  date_time_seconds.grid_remove()
  date_time_submit_button.grid_remove()

def schedule_date_time_task():
  clear_delay_task_elements()

  date_time_label.grid(row=4, column=0, columnspan=2)
  date_time_year_label.grid(row=5, column=0)
  date_time_year.grid(row=5, column=1)
  date_time_month_label.grid(row=6, column=0)
  date_time_month.grid(row=6, column=1)
  date_time_day_label.grid(row=7, column=0)
  date_time_day.grid(row=7, column=1)
  date_time_minutes_label.grid(row=8, column=0)
  date_time_minutes.grid(row=8, column=1)
  date_time_seconds_label.grid(row=9, column=0)
  date_time_seconds.grid(row=9, column=1)
  back_button.grid(row=10, column=0)
  date_time_submit_button.grid(row=10, column=1)

def handle_schedule_selection():
  error_message.config(text="")
  value = schedule_type.get()
  if(value == 'Delay'):
    schedule_delay_task()
  elif(value == 'Date and time'):
    schedule_date_time_task()

# Task schedule initial elements
task_label = tk.Label(root, text="Schedule a New Task:")
task_name_label = tk.Label(root, text="Task name: ")
task_name = tk.Entry(root)
task_schedule_type_label = tk.Label(root, text="Select a option of schedule: ")
schedule_type = ttk.Combobox(root, values=task_time_option_types)
schedule_type.bind("<<ComboboxSelected>>", lambda e: handle_schedule_selection())

def schedule_task():
  #  ????
  follow_up_frame = tk.Frame(root)
  follow_up_frame.grid(row=1, column=0, columnspan=2)

  task_label.grid(row=0, column=0)
  task_name_label.grid(row=1, column=0)
  task_name.grid(row=1, column=1)
  task_schedule_type_label.grid(row=2, column=0)
  schedule_type.grid(row=2, column=1)

def update_remaining_time():
    file_data = read_file_data(tasks_file_path)
    current_time = time.strftime("%H:%M:%S")
    tasks_data = get_tasks_remaining_time(file_data)
    time_label.config(text=f"Current Time: {current_time}\n{tasks_data}", justify=tk.LEFT)
    root.after(1000, update_remaining_time)

def remove_show_tasks_elements():
  time_label.grid_remove()

def remove_schedule_task_elements():
  task_label.grid_remove()
  task_name_label.grid_remove()
  task_name.grid_remove()
  task_schedule_type_label.grid_remove()
  schedule_type.grid_remove()
  delay_type_label.grid_remove()
  delay_type.grid_remove()

def handle_back():
  error_message.config(text="")
  remove_show_tasks_elements()
  remove_schedule_task_elements()
  clear_date_time_task_elements()
  clear_delay_task_elements()
  back_button.grid_remove()

  main_label.grid(row=0, column=0, columnspan=2)
  show_tasks_button.grid(row=1, column=0)
  schedule_task_button.grid(row=1, column=1)
  exit_button.grid(row=2, column=0)
  # TODO
  #  remove root loop
  # root.mainloop().grid_remove()

def handle_show_tasks():
  handle_action_selection('show_tasks')
  update_remaining_time()
  time_label.grid(row=0, column=0, columnspan=2)

def handle_schedule_task():
  print('schedule task')
  handle_action_selection('schedule_task')
  schedule_task()


# Initial elements
main_label = tk.Label(root, text="Task Time Tracker", font=("Helvetica", 16), padx=10, pady=5)
show_tasks_button = tk.Button(root, text="Show tasks", command=handle_show_tasks)
schedule_task_button = tk.Button(root, text="Schedule task", command=handle_schedule_task)
back_button = tk.Button(root, text="Back", command=handle_back)
exit_button = tk.Button(root, text="Exit", command=root.quit)
error_message = tk.Label(root, text="", fg="red")

main_label.grid(row=0, column=0, columnspan=2)
show_tasks_button.grid(row=1, column=0)
schedule_task_button.grid(row=1, column=1 )
exit_button.grid(row=2, column=0, columnspan=2)


def mount_back_button(action):

   if back_button.winfo_ismapped() != 0:
     return
   if (action == 'show_tasks'):
     back_button.grid(row=2, column=0, columnspan=2)
   elif (action == 'schedule_task'):
      # if not schedule selected
      back_button.grid(row=4, column=0, columnspan=2)
    # if schedule = delay

def handle_action_selection(action):
   main_label.grid_remove()
   show_tasks_button.grid_remove()
   schedule_task_button.grid_remove()
   exit_button.grid_remove()
   mount_back_button(action)


root.mainloop()












