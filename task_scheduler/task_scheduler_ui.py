import tkinter as tk
from tkinter import ttk
import time
import json
import os
import datetime

tasks_file_path = 'tasks.json'
task_time_delay_types = ['Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years']
task_time_option_types = ['By Delay', 'By Date and time']
task_month_options = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

screen = 0
root = tk.Tk()
root.title("Task Scheduler")
time_label = tk.Label(root, font=("Helvetica", 16))
# time_label.pack(padx=20, pady=20)

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
  for task in file_data:
    task_parsed_date = datetime.datetime.strptime(task['date'], '%Y-%m-%d %H:%M:%S')
    task_remaining_time = task_parsed_date - now
    overdue = task_remaining_time < datetime.timedelta(0)
    task['remaining_time_to_alert'] = datetime.timedelta(0) if overdue else task_remaining_time

  ordered_tasks = sorted(file_data, key=lambda task: task['remaining_time_to_alert'])

  for task in ordered_tasks:
    remaining_days = task['remaining_time_to_alert'].days
    remaining_hours, remainder = divmod(task['remaining_time_to_alert'].seconds, 3600)
    remaining_minutes, _ = divmod(remainder, 60)
    remaining_seconds =task['remaining_time_to_alert'].seconds % 60
    time_expired = remaining_days <= 0 and remaining_hours <= 0 and remaining_minutes <= 0 and remaining_seconds <= 0
    remaining_time = "Time Expired" if time_expired else f"{remaining_days} day(s), {remaining_hours} hour(s) and {remaining_minutes} minute(s) and {remaining_seconds} seconds"

    name_spacing = 20 - len(task['name'])
    time_spacing = 20 - len(remaining_time)

    data += task['name']+" " + '-' * name_spacing + '-' * time_spacing + remaining_time +'\n'
  return data

def handle_delay_answer():
    name = task_name.get()
    delay_type_value = delay_type.get()
    delay_quantity_value = delay_quantity.get()
    print(name, delay_type_value, delay_quantity_value)
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
    return new_task

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
    return new_task

def submit(schedule_type):
    print('SUBMIT')
    # TODO validate inputs
    # TODO show message, wait 5 secs, remove elements and go back to first screen
    if(schedule_type == 'delay'):
      handle_delay_answer()
    elif(schedule_type == 'date_time'):
      handle_date_time_answer()


# Schedule task Delay type
delay_label = tk.Label(root, text="Delay type task:")
delay_type_label = tk.Label(root, text="Select a delay type")
delay_type = ttk.Combobox(root, values=task_time_delay_types)
delay_quantity_label = tk.Label(root, text="Insert a delay quantity")
delay_quantity = tk.Entry(root)
delay_submit_button = tk.Button(root, text="Submit", command=lambda: submit('delay'))

def clear_delay_task_elements():
  delay_label.pack_forget()
  delay_type_label.pack_forget()
  delay_type.pack_forget()
  delay_quantity_label.pack_forget()
  delay_quantity.pack_forget()
  delay_submit_button.pack_forget()

def schedule_delay_task():
  clear_date_time_task_elements()
  delay_label.pack()
  delay_type_label.pack()
  delay_type.pack()
  delay_quantity_label.pack()
  delay_quantity.pack()
  delay_submit_button.pack()

# Schedule task Date and time type
date_time_label = tk.Label(root, text="Date and time task:")
date_time_year_label = tk.Label(root, text="Year")
date_time_year = tk.Entry(root)
date_time_month_label = tk.Label(root, text="Select a month")
date_time_month = ttk.Combobox(root, values=task_month_options)
date_time_day_label = tk.Label(root, text="Day")
date_time_day = tk.Entry(root)
date_time_minutes_label = tk.Label(root, text="Minutes")
date_time_minutes = tk.Entry(root)
date_time_seconds_label = tk.Label(root, text="Seconds")
date_time_seconds = tk.Entry(root)
date_time_submit_button = tk.Button(root, text="Submit", command=lambda: submit('date_time'))


def clear_date_time_task_elements():
  date_time_label.pack_forget()
  date_time_year_label.pack_forget()
  date_time_year.pack_forget()
  date_time_month_label.pack_forget()
  date_time_month.pack_forget()
  date_time_day_label.pack_forget()
  date_time_day.pack_forget()
  date_time_minutes_label.pack_forget()
  date_time_minutes.pack_forget()
  date_time_seconds_label.pack_forget()
  date_time_seconds.pack_forget()
  date_time_submit_button.pack_forget()

def schedule_date_time_task():
  clear_delay_task_elements()

  date_time_label.pack()
  date_time_year_label.pack()
  date_time_year.pack()
  date_time_month_label.pack()
  date_time_month.pack()
  date_time_day_label.pack()
  date_time_day.pack()
  date_time_minutes_label.pack()
  date_time_minutes.pack()
  date_time_seconds_label.pack()
  date_time_seconds.pack()
  date_time_submit_button.pack()

# Task schedule initial elements
task_label = tk.Label(root, text="Schedule a New Task:")
task_name = tk.Entry(root)

task_schedule_type_label = tk.Label(root, text="Select a option of schedule")
schedule_type_delay = tk.Button(root, text="Delay", command=schedule_delay_task)
schedule_type_date_time = tk.Button(root, text="Date and time", command=schedule_date_time_task)

def schedule_task():
  task_label.pack()
  task_name.pack()
  task_schedule_type_label.pack()
  schedule_type_delay.pack()
  schedule_type_date_time.pack()

def update_remaining_time():
    file_data = read_file_data(tasks_file_path)
    current_time = time.strftime("%H:%M:%S")
    tasks_data = get_tasks_remaining_time(file_data)
    time_label.config(text=f"Current Time: {current_time}\n{tasks_data}")

    root.after(1000, update_remaining_time)  # Update every 1000 milliseconds (1 second)

def remove_show_tasks_elements():
  time_label.pack_forget()

def remove_schedule_task_elements():
  task_label.pack_forget()
  task_name.pack_forget()
  task_schedule_type_label.pack_forget()
  schedule_type_delay.pack_forget()
  schedule_type_date_time.pack_forget()
  delay_type_label.pack_forget()
  delay_type.pack_forget()

def handle_back():
  print('back')

  remove_show_tasks_elements()
  remove_schedule_task_elements()
  clear_date_time_task_elements()
  clear_delay_task_elements()

  back_button.pack_forget()

  main_label.pack()
  add_task_button1.pack()
  add_task_button2.pack()
  exit_button.pack()
  # TODO
  #  remove root loop
  # root.mainloop().destroy()

def handle_show_tasks():
  handle_action_selection()
  update_remaining_time()
  time_label.pack()

def handle_schedule_task():
  print('schedule task')
  handle_action_selection()
  schedule_task()




# Initial elements
main_label = tk.Label(root, text="Task Time Tracker", font=("Helvetica", 16), padx=10, pady=5)
add_task_button1 = tk.Button(root, text="Show tasks", command=handle_show_tasks)
add_task_button2 = tk.Button(root, text="Schedule task", command=handle_schedule_task)
back_button = tk.Button(root, text="Back", command=handle_back)
exit_button = tk.Button(root, text="Exit", command=root.quit)


main_label.pack()
add_task_button1.pack()
add_task_button2.pack()
exit_button.pack()

def handle_action_selection():
   main_label.pack_forget()
   add_task_button1.pack_forget()
   add_task_button2.pack_forget()
   exit_button.pack_forget()
   if back_button.winfo_ismapped() == 0:
     back_button.pack()

root.mainloop()












