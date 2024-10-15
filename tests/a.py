from datetime import datetime , timedelta

day = datetime.now()
print(day)
yesterday = day - timedelta(days=1)
print(yesterday)
yesterday_date = yesterday.strftime("%Y-%m-%d")
print(yesterday_date)