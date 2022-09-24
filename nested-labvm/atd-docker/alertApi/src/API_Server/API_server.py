#!/usr/bin/env python

from flask import Flask, json, request, render_template
# Run this code using uWSGI - uwsgi --ini uwsgi_conf.ini
from pymemcache.client import base

# Don't forget to run `memcached' before running this next line:
client = base.Client(('localhost', 11211))

api = Flask(__name__)
alert_log = {"data":[]}
client.set('alert_log', json.dumps(alert_log))

print(f"Check: {json.loads(client.get('alert_log'))}")

@api.route('/alert', methods=['GET'])
def get_test():
    alert_report = json.loads(client.get('alert_log'))['data']
    print(f"Report: {alert_report}")
    n = len(alert_report)
    if len(alert_report) < 1:
        return render_template('noReport.html', title='CVP Alert Report')
    else:
        return render_template('alertReport.html', title='CVP Alert Report', report=alert_report, check=n)

@api.route('/alert', methods=['POST'])
def post_test():
    # Get Data from incoming post request
    api_data = json.loads(request.data)
    # Parse data to separate and format Alert Notifications
    log_data = []
    for alert in api_data['alerts']:
        log_entry = {}
        if alert['status'] == 'firing':
            log_entry['Status'] = 'new'
        elif alert['status'] == 'resolved':
            log_entry['Status'] = 'closed'
        else:
            log_entry['Status'] = 'open'
        if 'deviceHostname' in alert['labels']:
            log_entry['DeviceId'] = alert['labels']['deviceHostname']
        elif 'tag_hostname' in alert['labels']:
            log_entry['DeviceId'] = alert['labels']["tag_hostname"]
        elif 'deviceId' in alert['labels']:
            log_entry['DeviceId'] = alert['labels']['deviceId']
        else:
            log_entry['DeviceId'] = "Not Known"
        log_entry['Event'] = alert['labels']['eventType']
        log_entry['Severity'] = alert['labels']['severity']
        log_entry['Started'] = alert['startsAt']
        log_entry['AlertSource'] = api_data['receiver']
        print(f"Incoming: {str(log_entry)}")
        log_data.append(log_entry)
    alert_log = json.loads(client.get('alert_log'))
    for log_entry in log_data:
        alert_log["data"].append(log_entry)
    client.set('alert_log', json.dumps(alert_log))
    return json.dumps({"success": True}), 201

if __name__ == '__main__':
    api.run()
