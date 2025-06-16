from datetime import datetime

def check():
    try:
        with open('reminders.txt', 'r') as f:
            reminders = f.readlines()
        to_return = []

        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        for reminder in reminders:
            reminder = reminder.strip().split('|')
            if len(reminder) > 2:
                time_str = reminder[0]
                description = ''.join(reminder[1:])
            elif len(reminder) == 2:
                time_str = reminder[0]
                description = reminder[1]
            else:
                continue

            try:
                parts = time_str.split(':')
                if len(parts) == 2:
                    reminder_hour = int(parts[0])
                    reminder_minute = int(parts[1])

                else:
                    reminder_hour = int(parts[0])
                    reminder_minute = 0

            except ValueError:
                continue

            if len(description) > 0 and \
               reminder_hour == current_hour and \
               reminder_minute == current_minute:
                to_return.append(description)
        return to_return
    except FileNotFoundError:
        print("Error: 'reminders.txt' not found.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
