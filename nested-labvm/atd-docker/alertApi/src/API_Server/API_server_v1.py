#!/usr/bin/env python

from flask import Flask, json, request, render_template
# Run this code using uWSGI - uwsgi --ini uwsgi_conf.ini

api = Flask(__name__)
alert_log = {"data":[]}
file_path = "./"
file_name = "alert_log.json"
dump_file = "alert_dump.json"

def fileProc(file_name, file_path, action, data='BLANK'):
    "Basic File handling routine to Open/New read or append text to a file then close it"
    file_spec = file_path + file_name

    if action == "wj":
        fileInput = data
        try:
            fhandle = open(file_spec, 'w')
        except IOError as file_error:
            fileError = str("Could not open file to writej:"+str(file_spec)
                            + "Error:"+str(file_error))
            return fileError
        try:
            json.dump(fileInput, fhandle)
        except IOError as file_error:
            fileError = str("Could not writej to file:"+str(file_spec)
                            + "Error:"+str(file_error))
            return fileError
        else:
            fhandle.close()
            return

    if action == "rj":
        try:
            fhandle = open(file_spec, 'r')
        except IOError as file_error:
            fileError = str("Could not open file to readj:"+str(file_error))
            return fileError
        try:
            file_data = json.load(fhandle)
        except IOError as file_error:
            fileError = str("Could not readj file"+str(file_spec)
                            + "Error:"+str(file_error))
            return fileError
        else:
            fhandle.close()
            return file_data


#####################################################################
fileProc(file_name, file_path, 'wj', alert_log)
fileProc(dump_file, file_path, 'wj', alert_log)

@api.route('/alert', methods=['GET'])
def get_test():
    alert_report = fileProc(file_name, file_path, 'rj')["data"]
    print(f"Report: {str(alert_report)}")
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
            log_entry['Device'] = alert['labels']['deviceHostname']
        elif 'tag_hostname' in alert['labels']:
            log_entry['Device'] = alert['labels']["tag_hostname"]
        elif 'deviceId' in alert['labels']:
            log_entry['Device'] = alert['labels']['deviceId']
        else:
            log_entry['Device'] = "Not Known"
        log_entry['Event'] = alert['labels']['eventType']
        log_entry['Severity'] = alert['labels']['severity']
        log_entry['Started'] = alert['startsAt']
        log_entry['AlertSource'] = api_data['receiver']
        print(f"Incoming: {str(log_entry)}")
        log_data.append(log_entry)
    dump_log = fileProc(dump_file, file_path, 'rj')
    dump_log["data"].append(api_data)
    fileProc(dump_file, file_path, 'wj', dump_log)
    alert_log = fileProc(file_name, file_path, 'rj')
    for log_entry in log_data:
        alert_log["data"].append(log_entry)
    fileProc(file_name, file_path, 'wj', alert_log)
    return json.dumps({"success": True}), 201

if __name__ == '__main__':
    api.run()
