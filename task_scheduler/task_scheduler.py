import inquirer
import json
import datetime
import os

tasks_file_path = 'tasks.json'

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

def task_scheduler():
  # Variables
  task_time_option_types = ['By Delay', 'By Date and time']
  task_time_delay_types = ['Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months', 'Years']
  task_month_options = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  # Functions
  def is_date_valid(date_answers):
    day, month, year = date_answers['day'], task_month_options.index(date_answers['month']) + 1, int(date_answers['year'])
    today = datetime.datetime.now()
    if month < today.month and year == int(today.year):
      print("Selected month is not valid")
      return False
    if int(day) < today.day and month == today.month and year == int(today.year):
      print("Selected day is not valid")
      return False
    return True

  def is_time_valid(time_answers, date_answers):
    day, month, year = date_answers['day'], task_month_options.index(date_answers['month']) + 1, int(date_answers['year'])
    hour, minute = time_answers['hour'], time_answers['minute'], time_answers['second']
    today = datetime.datetime.now()

    # Validates if is the same day, if not, date it's consequently valid
    is_same_day = day == today.day and month == today.month and year == int(today.year)
    if(not is_same_day):
      return True
    # Validates if hour is bigger or the same as current hour
    if hour < today.hour:
      print("Selected hour is not valid")
      return False
   # Validates if minute is bigger or the same as current minute, if hour is also the same
    if minute <= today.minute and hour == today.hour:
      print("Selected minute is not valid")
      return False
    return True

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

  # Questions
  first_questions = [
    inquirer.Text('task_name', message="Enter the name of the task", validate=lambda _, x: x != ''),
    inquirer.List('schedule_type',
      message="Select a option of schedule",
      choices=task_time_option_types,
    )
  ]
  delay_questions = [
    inquirer.List('delay_type',
      message="Select a delay type",
      choices=task_time_delay_types,
    ),
    inquirer.Text('delay_multiplier', message="Enter the delay (number)", validate=lambda _, x: x.isdigit() and int(x) > 0),
  ]
  date_questions = [
    inquirer.Text('day', message="Enter the day", validate=lambda _, x: x.isdigit() and int(x) > 0),
    inquirer.List('month',
      message="Select the month",
      choices=task_month_options,
      validate=lambda _, x: x in task_month_options
    ),
    inquirer.Text('year', message="Enter the year (e.g. 2020)", validate=lambda _, x: x.isdigit() and int(x) > 0 and len(x) == 4 and int(x) >=  datetime.datetime.now().year),
  ]
  time_questions = [
    inquirer.Text('hour', message="Enter the hour (24h format)", validate=lambda _, x: x.isdigit() and int(x) > 0 and int(x) <= 24),
    inquirer.Text('minute', message="Enter the minute", validate=lambda _, x: x.isdigit() and int(x) >= 0 and int(x) <= 60),
    inquirer.Text('second', message="Enter the second", validate=lambda _, x: x.isdigit() and int(x) >= 0 and int(x) <= 60),
  ]

  # Main
  first_answers = inquirer.prompt(first_questions)
  if first_answers['schedule_type'] == 'By Delay':
    delay_answers = inquirer.prompt(delay_questions)
    to_remind_date = get_date_after_delay(delay_answers)
    new_task = {
      'name': first_answers['task_name'],
      'date': to_remind_date
    }
    save_data_on_file(new_task, tasks_file_path)
    print("We will remind you about task: '"+first_answers['task_name']+"' in " +
      delay_answers['delay_multiplier'] + " " + delay_answers['delay_type'] + " ("+str(to_remind_date)+")"
    )
    return new_task
  else:
    date_answers = inquirer.prompt(date_questions)
    while not is_date_valid(date_answers):
      date_answers = inquirer.prompt(date_questions)

    time_answers = inquirer.prompt(time_questions)
    while not is_time_valid(time_answers, date_answers):
      time_answers = inquirer.prompt(time_questions)

    full_date = datetime.datetime(int(date_answers['year']), task_month_options.index(date_answers['month']) + 1, int(date_answers['day']), int(time_answers['hour']), int(time_answers['minute']), int(time_answers['second']))
    to_remind_date = full_date
    new_task = {
      'name': first_answers['task_name'],
      'date': to_remind_date
    }

    save_data_on_file(new_task, tasks_file_path)
    print("We will remind you about task: '"+first_answers['task_name']+"' in " +
       str(to_remind_date)
    )
    return new_task

def action_selector():
  # Questions
  action_questions = [
    inquirer.List('main_menu',
      message="Select a option",
      choices=['Schedule a task', 'Show tasks', 'Exit'],
    )
  ]

  # Main
  action = inquirer.prompt(action_questions)
  if action['main_menu'] == 'Schedule a task':
    task_scheduler()
    action_selector()
  elif action['main_menu'] == 'Show tasks':
    tasks = read_file_data(tasks_file_path)
    if len(tasks) == 0:
      print("You don't have any tasks scheduled, please schedule one or more")
      action_selector()
      return

    print("              Tasks:")
    print('Name ---------------- Date                ---------------- Remaining time to alert')
    now = datetime.datetime.now()
    for task in tasks:
      task_parsed_date = datetime.datetime.strptime(task['date'], '%Y-%m-%d %H:%M:%S')
      task_remaining_time = task_parsed_date - now
      overdue = task_remaining_time < datetime.timedelta(0)
      task['remaining_time_to_alert'] = datetime.timedelta(0) if overdue else task_remaining_time

    ordered_tasks = sorted(tasks, key=lambda task: task['remaining_time_to_alert'])
    for task in ordered_tasks:
      pins = 20 - len(task['name'])
      # implement year logic
      remaining_days = task['remaining_time_to_alert'].days
      remaining_hours, remainder = divmod(task['remaining_time_to_alert'].seconds, 3600)
      remaining_minutes, _ = divmod(remainder, 60)
      remaining_seconds = task['remaining_time_to_alert'].seconds % 60
      remaining_time = f"{remaining_days} day(s), {remaining_hours} hour(s) and {remaining_minutes} minute(s) and {remaining_seconds} seconds"
      print(task['name']+" " + '-' * pins + " " + str(task['date']) + ' ---------------- ' + remaining_time)
  else:
    print("Exiting application...")
    exit()

def main():
  read_file_data(tasks_file_path)
  while True:
    action_selector()

main()